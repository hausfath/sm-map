"""
Export the viewer's data files from the interim/processed products.

  python3.13 scripts/export_viewer.py

Writes to src/data/:
  footprint_major.geojson   major + idonly ultramafic units, simplified, dissolved by class/confidence/source
  footprint_minor.geojson   minor units (ultramafic as a lesser constituent), simplified further
  sites.json                site table joined with environment and model results (all modes x scenarios)
  tailings_internal.geojson GRID-Arendal facilities within 5 km of major ultramafic (INTERNAL, publish=False)
  meta.json                 build stamp, counts, constants echoed for the legend
"""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import constants as C
OUT = ROOT / "src/data"; OUT.mkdir(parents=True, exist_ok=True)


def footprint():
    fp = gpd.read_file(ROOT / "data/interim/footprint_um.gpkg")
    fp = fp[fp.geometry.notna() & ~fp.geometry.is_empty]
    fp["Mha"] = fp.geometry.area / 1e10
    for name, sel, tol in [("footprint_major", fp.um_class.isin(["major", "idonly", "ophiolite"]), 2000),
                           ("footprint_minor", fp.um_class.eq("minor"), 5000)]:
        g = fp[sel].copy()
        g["source"] = g.ref_source.fillna("").str.slice(0, 80)
        g["um_rock"] = g["um_rock"].fillna("").replace("", "ultramafic rock (undifferentiated)")
        d = g.dissolve(by=["um_class", "um_rock", "conf", "source", "publish"], aggfunc={"Mha": "sum"}).reset_index()
        d["geometry"] = d.geometry.simplify(tol, preserve_topology=True)   # metres in Equal Earth
        d = d[~d.geometry.is_empty].to_crs(4326)
        d["Mha"] = d.Mha.round(3)
        path = OUT / f"{name}.geojson"
        d.to_file(path, driver="GeoJSON")
        print(f"{name}: {len(d)} features, {sum(g.geometry.notna())} source polygons, {path.stat().st_size/1e6:.1f} MB, {d.Mha.sum():.1f} Mha")


def sites():
    s = pd.read_csv(ROOT / "data/sites_v0.csv")
    env = pd.read_csv(ROOT / "data/processed/sites_env.csv")
    res = pd.read_csv(ROOT / "data/processed/sites_results.csv")
    keep_env = ["site", "t_air_c", "t_season_c", "precip_mm", "slope_deg", "road_km", "iso3", "grid_gco2_kwh", "grid_src", "elec_usd_per_mwh", "elec_src"]
    s = s.merge(env[keep_env], on="site", how="left")
    out = []
    for _, r in s.iterrows():
        rr = res[res.site == r.site]
        results = {}
        for _, x in rr.iterrows():
            results.setdefault(x["mode"], {})[x.scenario] = dict(
                gross=None if pd.isna(x.gross_t_per_t_p50) else round(float(x.gross_t_per_t_p50), 4),
                gross_p10=None if pd.isna(x.gross_p10) else round(float(x.gross_p10), 4),
                gross_p90=None if pd.isna(x.gross_p90) else round(float(x.gross_p90), 4),
                cost=None if pd.isna(x.cost_usd_per_tco2_p50) else round(float(x.cost_usd_per_tco2_p50)),
                cost_p10=None if pd.isna(x.cost_p10) else round(float(x.cost_p10)),
                cost_p90=None if pd.isna(x.cost_p90) else round(float(x.cost_p90)),
                not_viable=round(float(x.share_not_viable), 3),
                removal_Mt=None if pd.isna(x.removal_Mt_p50) else round(float(x.removal_Mt_p50), 2))
        fc = C.FEED_CLASSES.get(r.feed_class)
        out.append(dict(site=r.site, country=r.country, lat=float(r.lat), lon=float(r.lon), track=r.track,
                        processing_state=r.processing_state, feed_class=r.feed_class,
                        feed_class_name=fc.name if fc else r.feed_class,
                        reactive_mg_wt=list(fc.reactive_mg_wt) if fc else None,
                        commodity=r.commodity, status=r.status,
                        tonnage_mt=None if pd.isna(r.tonnage_mt) else float(r.tonnage_mt),
                        tonnage_status=r.tonnage_status if isinstance(r.tonnage_status, str) else "unknown",
                        tonnage_src=r.tonnage_src if isinstance(r.tonnage_src, str) else "",
                        coord_status=r.coord_status, notes=r.notes if isinstance(r.notes, str) else "",
                        env=dict(t_air_c=None if pd.isna(r.t_air_c) else round(float(r.t_air_c), 1),
                                 precip_mm=None if pd.isna(r.precip_mm) else round(float(r.precip_mm)),
                                 slope_deg=None if pd.isna(r.slope_deg) else round(float(r.slope_deg), 1),
                                 road_km=None if pd.isna(r.road_km) else round(float(r.road_km), 1),
                                 grid_gco2_kwh=None if pd.isna(r.grid_gco2_kwh) else round(float(r.grid_gco2_kwh)),
                                 grid_src=r.grid_src if isinstance(r.grid_src, str) else "",
                                 elec_usd_per_mwh=None if pd.isna(r.elec_usd_per_mwh) else float(r.elec_usd_per_mwh),
                                 elec_src=r.elec_src if isinstance(r.elec_src, str) else ""),
                        results=results))
    (OUT / "sites.json").write_text(json.dumps(out))
    print(f"sites.json: {len(out)} sites")
    return len(out)


def provinces():
    h = gpd.read_file(ROOT / "data/raw/hasterok_ophiolite_provinces.gpkg").to_crs(4326)
    h["geometry"] = h.geometry.simplify(0.02, preserve_topology=True)
    h[["name", "prov_ref", "geometry"]].to_file(OUT / "ophiolite_provinces.geojson", driver="GeoJSON")
    print(f"ophiolite_provinces.geojson: {len(h)} provinces (Hasterok et al. 2022, CC-BY 4.0; locator only)")


def tailings():
    t = pd.read_csv(ROOT / "data/interim/tailings_near_ultramafic_INTERNAL.csv")
    g = gpd.GeoDataFrame(t, geometry=gpd.points_from_xy(t.longitude, t.latitude), crs=4326)
    cols = ["mine", "tsf", "owner_company", "country", "status", "current_tailings_storage", "dist_km", "conf", "name", "lith", "geometry"]
    g = g[cols].rename(columns={"current_tailings_storage": "storage_m3", "name": "unit_name", "lith": "unit_lith"})
    g.to_file(OUT / "tailings_internal.geojson", driver="GeoJSON")
    print(f"tailings_internal.geojson: {len(g)} facilities")
    return len(g)


def main():
    footprint()
    provinces()
    n_sites = sites()
    n_t = tailings()
    meta = dict(built=time.strftime("%Y-%m-%d %H:%M"), n_sites=n_sites, n_tailings=n_t,
                horizon_yr=C.HORIZON_YR, frontier_ref=C.FRONTIER_REFERENCE_T_PER_T["t_per_t"],
                uptake_scenarios={k: v["t_per_t"] for k, v in C.UPTAKE_SCENARIOS.items()}, tiers=list(C.TIERS.keys()),
                modes=list(C.SYSTEM_MODES.keys()), internal=True,
                publish_flags={k: v["reason"] for k, v in C.DATA_PUBLISH_FLAGS.items() if not v["publish"]})
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1))
    print("meta.json written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
