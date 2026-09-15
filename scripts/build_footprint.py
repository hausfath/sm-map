"""
Merge the multi-zoom Macrostrat crawls into one ultramafic footprint.

  python3.13 scripts/build_footprint.py

Rule (PLAN.md 2a). Zoom levels serve different map scales: z5 small-scale
compilations, z8 medium, z10 large. A unit found at a coarse zoom is KEPT unless a
finer zoom's tile is served by a source that is ultramafic-AWARE (it has
ultramafic legend entries somewhere in Macrostrat) and that finer source does not
classify this location as ultramafic: then the finer map is trusted (precision
gain). If the finer source is generic (no ultramafic entries anywhere), the coarse
hit survives with low confidence. Attribution is the finest zoom that hits.

Outputs
  data/interim/footprint_um.gpkg      polygons: um_class, um_terms, legend_id, source_id,
                                      ref_source, zoom, conf (high/medium/low), land-clipped
  data/interim/footprint_by_country.csv   Mha by country x class x conf
"""
import csv, sys
from pathlib import Path
import geopandas as gpd, pandas as pd, numpy as np
from shapely.geometry import box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"
ZOOMS = [5, 8, 10]
CONF = {10: "high", 8: "medium", 5: "low"}
sys.path.insert(0, str(ROOT / "scripts"))
from macrostrat_legend import classify, dominant_rock   # same text rules for regional overlays

# Regional overlays: national maps that take precedence over Macrostrat inside their
# own footprint where Macrostrat has no usable ultramafic coverage (PLAN.md 2a).
# (path, name field, lithology field, ref, licence)
OVERLAYS = [
    # (path, name field, lithology field, ref, licence, publish, mode)
    # mode "replace": a detailed national map; Macrostrat is dropped inside the overlay's hull.
    # mode "supplement": a coarse single-class product; only fills where nothing else maps ultramafic.
    (ROOT / "data/raw/ga_1m_ultramafic.gpkg", "name", "lithology",
     "Geoscience Australia, Surface Geology of Australia 1:1M (2012)", "CC-BY 4.0", True, "replace"),
    (ROOT / "data/raw/nc_massifs_peridotites_50k.gpkg", "unite", "lithologie",
     "Georep / DIMENC New Caledonia, Massifs de peridotites 1:50k", "Licence Ouverte (Etalab)", True, "replace"),
    (ROOT / "data/raw/quebec_sigeom_ultramafic.gpkg", "ETQT_LITH", "DESC_LITH",
     "Quebec SIGEOM, Geologie du socle (Zone geologique)", "CC BY 4.0", True, "replace"),
    (ROOT / "data/raw/africa_usgs_ultramafic.gpkg", "name", "lithology",
     "USGS Africa Terrestrial Ecosystems surficial lithology 90 m, class Ultramafic", "public domain", True, "supplement"),
    # WSP-compiled serpentinite / ophiolite polygons (sources: GSC world geology via NRCan, BGR IGME5000,
    # GA, USGS, EGDI; all open). Fills Oman, Iran, Indonesia, PNG, Arabia, Cuba, Turkey, India, Myanmar.
    (ROOT / "data/raw/wsp_ultramafic_classes.gpkg", "WSP_lithology", "WSP_lithology",
     "WSP PotentialFeedstock_Rev1_202602 ultramafic classes (GSC/NRCan world geology, BGR IGME5000, GA, USGS, EGDI)", "open sources via WSP compilation", True, "supplement"),
    # Hasterok et al. 2022 ophiolite PROVINCE outlines are NOT part of the footprint (tectonic provinces,
    # not outcrop; 'Semail' alone is 24 Mha). They are exported separately as a dashed locator layer.
    # GSC Open File 5529 (Chorlton 2007) intrusive domains classed ULTRAMAFIC SUITE / MAFIC-ULTRAMAFIC SUITE
    # (Open Government Licence Canada). Small-scale domains, so low confidence; fills China, Kazakhstan, Myanmar, Japan.
    (ROOT / "data/raw/gsc5529_ultramafic_suites.gpkg", "name", "lithology",
     "GSC Open File 5529 (Chorlton 2007) Generalized geology of the world, intrusdt.INTCLASS", "Open Government Licence - Canada", True, "supplement_low"),
    (ROOT / "data/raw/brazil_sgb_1m_ultramafic_LICENCE_UNRESOLVED.gpkg", "NOME", "LITOTIPOS",
     "SGB/CPRM Brazil, Litoestratigrafia 1:1M (2004)", "UNRESOLVED (no open-data plan): local use only", False, "replace"),
]


def tile_geom(z, x, y):
    n = 2 ** z; w = 2 * np.pi * 6378137.0
    return box(-w/2 + x*w/n, w/2 - (y+1)*w/n, -w/2 + (x+1)*w/n, w/2 - y*w/n)


def main():
    leg = pd.read_csv(INTERIM / "macrostrat_um_legend.csv")
    aware_sources = set(leg.source_id.unique())
    cls = leg.set_index("legend_id")[["um_class", "um_terms", "um_rock"]]
    layers = {}
    for z in ZOOMS:
        g = gpd.read_file(INTERIM / f"macrostrat_um_z{z}.gpkg").drop(columns=["um_class", "um_terms", "leg_scale"], errors="ignore")
        g = g.merge(cls, left_on="legend_id", right_index=True, how="left")
        g["zoom"] = z
        g["geometry"] = g.geometry.buffer(0)
        layers[z] = g
        print(f"z{z}: {len(g)} units")
    # tiles served by an ultramafic-aware source, per zoom (any aware source in the tile)
    aware_tiles = {}
    for z in ZOOMS:
        t = pd.read_csv(INTERIM / f"macrostrat_tile_sources_z{z}.csv")
        t["aware"] = t.source_id.isin(aware_sources)
        aw = t[t.aware].groupby(["x", "y"]).size().index
        aware_tiles[z] = gpd.GeoDataFrame(geometry=[tile_geom(z, x, y) for x, y in aw], crs=3857)
        print(f"z{z}: {len(aw)} tiles served by ultramafic-aware sources of {t.groupby(['x','y']).ngroups} crawled")
    # finest first; coarser layers are clipped by (a) finer hits and (b) finer aware tiles
    kept = [layers[10]]
    mask_hits = unary_union(layers[10].geometry.values)
    mask_aware = unary_union(aware_tiles[10].geometry.values)
    for z in (8, 5):
        g = layers[z].copy()
        cut = unary_union([mask_hits, mask_aware])
        g["geometry"] = g.geometry.difference(cut)
        g = g[~g.geometry.is_empty]
        print(f"z{z}: {len(g)} units survive after finer-zoom precedence")
        kept.append(g)
        mask_hits = unary_union([mask_hits, *g.geometry.values])
        mask_aware = unary_union([mask_aware, *aware_tiles[z].geometry.values])
    fp = pd.concat(kept, ignore_index=True)
    fp = gpd.GeoDataFrame(fp, geometry="geometry", crs=3857)
    fp["conf"] = fp.zoom.map(CONF)
    fp["licence"] = "CC-BY 4.0 (Macrostrat; per-source licences not machine-checkable)"
    fp["publish"] = True
    # regional overlays: classify with the same text rules, precedence over Macrostrat
    for path, namef, lithf, ref, lic, publish, mode in OVERLAYS:
        if not path.exists():
            print(f"overlay missing, skipped: {path.name}"); continue
        o = gpd.read_file(path).to_crs(3857)
        o["geometry"] = o.geometry.buffer(0)
        res = [classify(r[namef], r[lithf], None) for _, r in o.iterrows()]
        o["um_class"] = [c for c, _ in res]; o["um_terms"] = [";".join(t) for _, t in res]
        o["um_rock"] = [dominant_rock(r[namef], r[lithf]) for _, r in o.iterrows()]
        # an ophiolite complex is only part mantle section: separate class with a lower ultramafic fraction
        oph = o[lithf].astype(str).str.contains("ophiolit", case=False) & ~o[lithf].astype(str).str.contains("serpentin|peridotit|harzburg|dunit", case=False)
        o.loc[oph, "um_class"] = "ophiolite"
        lith = o[lithf].astype(str).str.lower()
        o.loc[lith.str.startswith("ultramafic suite"), "um_class"] = "ophiolite"     # domain-scale: part ultramafic
        o.loc[lith.str.startswith("mafic-ultramafic suite"), "um_class"] = "minor"
        o = o[o.um_class != "none"]
        o = gpd.GeoDataFrame(dict(legend_id=-1, source_id=-1, name=o[namef], lith=o[lithf], ref_source=ref,
                                  um_class=o.um_class, um_terms=o.um_terms, um_rock=o.um_rock, zoom=99, conf="high",
                                  licence=lic, publish=publish),
                             geometry=o.geometry.values, crs=3857)
        if mode == "replace":
            hull = unary_union(o.geometry.values).convex_hull.buffer(50_000)   # overlay's own footprint
            fp["geometry"] = fp.geometry.difference(hull)
            fp = fp[~fp.geometry.is_empty]
        else:  # supplement: keep everything already mapped, add the overlay only where nothing else is
            existing = unary_union(fp[fp.um_class.isin(["major", "idonly", "ophiolite"])].geometry.values)
            o["geometry"] = o.geometry.difference(existing)
            o = o[~o.geometry.is_empty]
            o["conf"] = "low" if mode == "supplement_low" else "medium"
        fp = pd.concat([fp, o], ignore_index=True)
        fp = gpd.GeoDataFrame(fp, geometry="geometry", crs=3857)
        print(f"overlay {path.name} [{mode}]: {len(o)} units ({o.um_class.value_counts().to_dict()})")
    # land clip and country attribution (Natural Earth 50m)
    land = gpd.read_file("zip://" + str(ROOT / "data/raw/ne_50m_admin_0_countries.zip"))[["ADMIN", "ISO_A3", "geometry"]].to_crs(8857)
    fp = fp.to_crs(8857)
    fp = gpd.overlay(fp, land, how="intersection", keep_geom_type=True)
    fp["Mha"] = fp.geometry.area / 1e10
    fp.to_file(INTERIM / "footprint_um.gpkg", driver="GPKG")
    tab = fp.pivot_table(index="ADMIN", columns=["um_class", "conf"], values="Mha", aggfunc="sum").fillna(0)
    tab["major_total"] = tab.get("major", pd.DataFrame(index=tab.index)).sum(axis=1)
    tab["ophiolite_total"] = tab.get("ophiolite", pd.DataFrame(index=tab.index)).sum(axis=1) if "ophiolite" in tab.columns.get_level_values(0) else 0.0
    tab = tab.sort_values("major_total", ascending=False)
    tab.round(3).to_csv(INTERIM / "footprint_by_country.csv")
    print("\nOn-land area by class and confidence (Mha):")
    print(fp.groupby(["um_class", "conf"])["Mha"].sum().round(2).to_string())
    print("\nTop 25 countries by major + ophiolite area (Mha):")
    tab["um_total"] = tab["major_total"] + tab["ophiolite_total"]
    print(tab.sort_values("um_total", ascending=False)[["major_total", "ophiolite_total"]].head(25).round(2).to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
