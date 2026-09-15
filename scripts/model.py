"""
Removal and cost model for the SM Atlas site table (PLAN.md sections 3-4).

  python3.13 scripts/model.py            # writes data/processed/sites_results.csv and _draws.npz

Per site, per (system mode, mineralogy scenario):
  removal(T) [tCO2/t rock] = f_max * (1 - exp(-k T)),  f_max = reactive_Mg_wt * CAP_brucite * phi
  k = k0 * E * arrhenius(T_air) * moisture(P)          (moisture = 1 in reactor mode: irrigated)
  cost [$/tCO2] = PV(cost per t rock) / PV(net removal per t rock), 5%/yr, horizon T
  net removal = gross - (fan + grind) kWh * grid CO2 intensity - diesel

Uncertainty: two-level Monte Carlo (reviewer M2). Non-spatial parameters are drawn
once per draw; country-level indices (electricity price, grid intensity) once per
country per draw; per-site terms (climate, slope, road distance) are fixed. Report
median, P10, P90. Cells/sites whose net removal <= 0 in a draw are "not viable"
in that draw and excluded from the cost quantiles; the share is reported.

Every parameter comes from scripts/constants.py. Nothing here is tuned to a site.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd, rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import constants as C
from distances import RoadDistance

RNG = np.random.default_rng(20260908)
N_DRAWS = 2000

# ---- judgement parameters not yet in constants (flagged; move there once agreed)
K0_PER_YR = dict(LOW=0.046, CENTRAL=0.14, HIGH=0.35)   # passive brucite carbonation half-life 15 / 5 / 2 yr at 20 C, optimal moisture
K0_SRC = ("judgement: Baptiste columns carbonated 0.6 wt% brucite in ~120 d (Power et al. 2020) but field piles are "
          "CO2-supply limited (Mount Keith, Dumont, Black Lake); the LOW/CENTRAL/HIGH 20-yr extents must reproduce the "
          "reviewer envelope 0.011-0.080 tCO2/t for 2-8 wt% brucite (gate G3).")
ELEC_USD_PER_KWH = dict(lo=0.05, central=0.09, hi=0.15, src="judgement: global industrial band; replace with country data")
WATER_USD_PER_M3 = dict(lo=0.3, central=1.0, hi=3.0, src="judgement")
DIESEL_KGCO2_PER_T_QUARRIED = dict(lo=1.5, central=3.0, hi=6.0, src="judgement; Frontier POV: extraction+comminution ~0.05 tCO2 per tCO2 removed")
ACCESS_USD_PER_T_KM = 0.02   # consumables/logistics proxy on road distance, capped at 200 km (judgement)
GRIND_P80_UM = 50            # greenfield grind target; Strefler 19.4 kWh/t
DISCOUNT = C.COST["discount_rate"]["central"]
T_YEARS = C.HORIZON_YR


def tri(lo, c, hi, n=None):
    return RNG.triangular(lo, c, hi, N_DRAWS if n is None else n)


def arrhenius(t_c, ea_kj):
    tk, tr = t_c + 273.15, C.T_REF_C + 273.15
    return np.exp(-ea_kj / C.R_GAS * (1.0 / tk - 1.0 / tr))


def moisture_factor(p_mm):
    """Non-monotonic (Harrison et al. 2017): judgement shape on annual precipitation as a
    proxy for pile water content. 1.0 between 400 and 1500 mm; 0.3 at 0 mm; 0.5 at 3000 mm+."""
    p = np.asarray(p_mm, float)
    f = np.ones_like(p)
    f = np.where(p < 400, 0.3 + 0.7 * p / 400.0, f)
    f = np.where(p > 1500, np.clip(1.0 - 0.5 * (p - 1500) / 1500.0, 0.5, 1.0), f)
    return f


def sample_rasters(lons, lats):
    out = {}
    for key, path, scale, off in [("t_air_c", "data/raw/CHELSA_bio1_1981-2010_V.2.1.tif", 0.1, -273.15),
                                  ("t_season_c", "data/raw/CHELSA_bio4_1981-2010_V.2.1.tif", 0.01, 0.0),
                                  ("precip_mm", "data/raw/CHELSA_bio12_1981-2010_V.2.1.tif", 0.1, 0.0),
                                  ("slope_deg", "data/interim/slope_deg_x4_30s.tif", 0.25, 0.0)]:
        with rasterio.open(ROOT / path) as ds:
            v = np.array([x[0] for x in ds.sample(zip(map(float, lons), map(float, lats)))], float)
            v[v == ds.nodata] = np.nan
            out[key] = v * scale + off
    return out


def country_tables(sites):
    ne = gpd.read_file("zip://" + str(ROOT / "data/raw/ne_50m_admin_0_countries.zip"))[["ADMIN", "ISO_A3", "geometry"]]
    pts = gpd.GeoDataFrame(sites, geometry=gpd.points_from_xy(sites.lon, sites.lat), crs=4326)
    j = gpd.sjoin_nearest(pts, ne, how="left").drop_duplicates(subset=["site"])
    iso = j.set_index("site")["ISO_A3"].replace({"-99": None})
    # New Caledonia is a French territory in NE; Ember reports it separately? use FRA fallback
    em = pd.read_csv(ROOT / "data/raw/ember_yearly_full_release_long_format.csv", low_memory=False)
    ci = em[(em.Variable == "CO2 intensity")].sort_values("Year").groupby("ISO 3 code")["Value"].last()
    return iso, ci


def main():
    sites = pd.read_csv(ROOT / "data/sites_v0.csv")
    sites = sites[sites.lat.notna()].reset_index(drop=True)
    n = len(sites)
    env = sample_rasters(sites.lon.values, sites.lat.values)
    for k, v in env.items():
        sites[k] = v
    rd = RoadDistance("all")
    sites["road_km"] = rd.km(sites.lon.values, sites.lat.values)
    iso, ci = country_tables(sites)
    sites["iso3"] = sites.site.map(iso)
    sites["grid_gco2_kwh"] = sites.iso3.map(ci)
    sites.loc[sites.iso3.eq("NCL") & sites.grid_gco2_kwh.isna(), "grid_gco2_kwh"] = ci.get("FRA", np.nan)  # placeholder, flagged
    sites["grid_gco2_kwh"] = sites.grid_gco2_kwh.fillna(ci.median())
    sites["grid_src"] = np.where(sites.iso3.map(ci).notna(), "Ember latest year", "Ember global median (country missing)")
    # subnational overrides (TEAs, WSP option analysis): a site takes the override whose centre is
    # nearest among those whose radius contains it (so Thetford is Quebec, not New England)
    def _gc(lat1, lon1, lat2, lon2):
        return 2 * 6371.0088 * np.arcsin(np.sqrt(np.sin(np.radians(lat2 - lat1) / 2) ** 2 +
                                                 np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(np.radians(lon2 - lon1) / 2) ** 2))
    for i, s_ in sites.iterrows():
        cands = [(_gc(s_.lat, s_.lon, o["lat"], o["lon"]), o) for o in C.GRID_OVERRIDES]
        cands = [(d, o) for d, o in cands if d <= o["radius_km"]]
        if cands:
            d, o = min(cands, key=lambda t: t[0])
            sites.loc[i, "grid_gco2_kwh"] = o["gco2_kwh"]; sites.loc[i, "grid_src"] = o["name"] + ": " + o["src"]

    # per-site feed class parameters
    cls = sites.feed_class.map(lambda c: C.FEED_CLASSES.get(c, C.FEED_CLASSES["serp_lizardite"]))
    is_tailings = sites.processing_state.eq("tailings").values
    phi = C.PHI_PRODUCT[C.PHI_DEFAULT]
    ea = C.EA_KJ_MOL
    yrs = np.arange(1, T_YEARS + 1)
    disc = (1 + DISCOUNT) ** (-yrs)

    results = []
    draws_store = {}
    # electricity price per site: override or tier default (drawn per country per draw)
    def _gc(lat1, lon1, lat2, lon2):
        return 2 * 6371.0088 * np.arcsin(np.sqrt(np.sin(np.radians(lat2 - lat1) / 2) ** 2 +
                                                 np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(np.radians(lon2 - lon1) / 2) ** 2))
    sites["elec_usd_per_mwh"] = np.nan; sites["elec_src"] = "tier default range"
    for i, s_ in sites.iterrows():
        c = [(_gc(s_.lat, s_.lon, o["lat"], o["lon"]), o) for o in C.ELEC_PRICE_OVERRIDES]
        c = [(d, o) for d, o in c if d <= o["radius_km"]]
        if c:
            d, o = min(c, key=lambda t: t[0]); sites.loc[i, "elec_usd_per_mwh"] = o["usd_per_mwh"]; sites.loc[i, "elec_src"] = o["name"] + ": " + o["src"]
    for mode in ("passive_pile", "reactor_aerated", "reactor_activated"):
        M = C.SYSTEM_MODES[mode]
        for scen in ("FOAK", "NOAK"):
            T = C.TIERS[scen]; js = T["judgement_scale"]
            uni = lambda pair: RNG.uniform(pair[0], pair[1], N_DRAWS)
            # ---- draws: non-spatial (per draw)
            k0 = tri(K0_PER_YR["LOW"], K0_PER_YR["CENTRAL"], K0_PER_YR["HIGH"])   # kinetic uncertainty inside the MC
            ea_d = tri(ea["lo"], ea["central"], ea["hi"], N_DRAWS)
            handling = tri(C.COST["handling_usd_per_t"]["lo"], C.COST["handling_usd_per_t"]["central"], C.COST["handling_usd_per_t"]["hi"], N_DRAWS) * uni(js["handling"])
            quarry = tri(C.COST["quarry_usd_per_t"]["lo"], C.COST["quarry_usd_per_t"]["central"], C.COST["quarry_usd_per_t"]["hi"], N_DRAWS)
            mrv = tri(C.COST["mrv_usd_per_tco2"]["lo"], C.COST["mrv_usd_per_tco2"]["central"], C.COST["mrv_usd_per_tco2"]["hi"], N_DRAWS)
            cx = M["capex_usd_per_t_rock"]; capex = tri(cx["lo"], cx["central"], cx["hi"], N_DRAWS) * uni(js["capex"])
            fixed_other = np.zeros(N_DRAWS)
            if mode == "reactor_activated":   # TEA-tied: per-tCO2 categories become per-tonne-feed via the TEA uptake
                A = T["activated"]; uptake_tea = uni(A["uptake_t_per_t"])
                capex = uni(A["capex_usd_per_tco2"]) * uptake_tea
                fixed_other = uni(A["fixed_opex_usd_per_tco2"]) + uni(A["other_var_usd_per_tco2"])
                handling = np.zeros(N_DRAWS); mrv = np.zeros(N_DRAWS)   # inside the TEA capex / other-variable lines
                mwh_per_tco2 = uni(A["elec_mwh_per_tco2"])
            water_p = tri(WATER_USD_PER_M3["lo"], WATER_USD_PER_M3["central"], WATER_USD_PER_M3["hi"], N_DRAWS)
            diesel = tri(DIESEL_KGCO2_PER_T_QUARRIED["lo"], DIESEL_KGCO2_PER_T_QUARRIED["central"], DIESEL_KGCO2_PER_T_QUARRIED["hi"], N_DRAWS)
            Ev = M["E"]; E = tri(Ev["LOW"], Ev["CENTRAL"], Ev["HIGH"]) if isinstance(Ev, dict) else np.full(N_DRAWS, Ev)
            ek = M["elec_kwh_per_t_rock"]; fan = tri(ek["LOW"], ek["CENTRAL"], ek["HIGH"]) if "LOW" in ek else np.zeros(N_DRAWS)
            wk = M["water_m3_per_t_rock"]; water = tri(wk["LOW"], wk["CENTRAL"], wk["HIGH"]) if "LOW" in wk else np.zeros(N_DRAWS)
            activation = None
            if mode == "reactor_activated":
                activation = uptake_tea / (0.44 * phi)           # fraction of whole-rock capacity implied by the TEA uptake
                fan = mwh_per_tco2 * 1000.0 * uptake_tea         # kWh per tonne feed = MWh/tCO2 x tCO2/t
                water = np.zeros(N_DRAWS)                        # water is inside other variable opex in the TEAs
            # ---- country-level (per country per draw)
            dflt = T["activated"]["elec_usd_per_mwh_default"]
            elec_by_country = {c: uni(dflt) / 1000.0 for c in sites.iso3.fillna("NA").unique()}   # $/kWh, tier default
            ci_scale = {c: RNG.normal(1.0, 0.1, N_DRAWS) for c in elec_by_country}   # +-10% on reported intensity
            for i, s in sites.iterrows():
                fc = cls[i]
                lo_, c_, hi_ = fc.reactive_mg_wt
                rmg = tri(lo_, c_, hi_, N_DRAWS) / 100.0 if hi_ > lo_ else np.full(N_DRAWS, c_ / 100.0)   # mineralogy uncertainty inside the MC
                f_max = rmg * C.CAP_MGCO3["brucite"] * phi
                if activation is not None:   # pre-treatment liberates bulk serpentine Mg (whole-rock ~0.44 tCO2/t MgCO3 basis)
                    f_max = np.maximum(f_max, activation * 0.44 * phi)
                if fc.excluded:
                    f_max[:] = 0.0
                moist = 1.0 if mode != "passive_pile" else moisture_factor(s.precip_mm)
                k = k0 * E * arrhenius(s.t_air_c if np.isfinite(s.t_air_c) else 15.0, ea_d) * moist
                # annual gross removal per tonne over the horizon (tCO2/t)
                ext = f_max[:, None] * (1 - np.exp(-k[:, None] * yrs[None, :]))
                annual = np.diff(np.c_[np.zeros(N_DRAWS), ext], axis=1)
                gross_T = ext[:, -1]
                # energy and emissions per tonne rock (one-off for grind/quarry, annual for fan spread over first 5 yr)
                cc = s.iso3 if pd.notna(s.iso3) else "NA"
                elec = elec_by_country[cc] if pd.isna(s.elec_usd_per_mwh) else np.full(N_DRAWS, s.elec_usd_per_mwh / 1000.0)
                gci = s.grid_gco2_kwh * ci_scale[cc] / 1e6  # tCO2/kWh
                grind_kwh = 0.0 if is_tailings[i] else C.COST["grind_kwh_per_t"]["points"][GRIND_P80_UM]
                emis = grind_kwh * gci + fan * gci + (0.0 if is_tailings[i] else diesel / 1000.0)
                net_T = gross_T - emis
                # costs per tonne rock: one-off + annual
                oneoff = (0.0 if is_tailings[i] else quarry) + grind_kwh * elec + handling + capex \
                         + ACCESS_USD_PER_T_KM * min(s.road_km, 200.0) * (0.0 if is_tailings[i] else 1.0)
                annual_cost = ((fan * elec + water * water_p) / 5.0)[:, None] * (yrs[None, :] <= 5)   # reactor operation over first 5 yr
                pv_cost = oneoff + (annual_cost * disc[None, :]).sum(axis=1) + (mrv + fixed_other) * (annual * disc[None, :]).sum(axis=1)
                pv_net = ((annual - emis[:, None] / T_YEARS) * disc[None, :]).sum(axis=1)
                viable = pv_net > 0
                cost = np.where(viable, pv_cost / np.where(viable, pv_net, np.nan), np.nan)
                q = lambda a, p: float(np.nanpercentile(a, p)) if np.isfinite(a).any() else np.nan
                results.append(dict(site=s.site, country=s.country, track=s.track, feed_class=s.feed_class, mode=mode, scenario=scen,
                                    gross_t_per_t_p50=q(gross_T, 50), gross_p10=q(gross_T, 10), gross_p90=q(gross_T, 90),
                                    net_t_per_t_p50=q(net_T, 50), share_not_viable=float(1 - viable.mean()),
                                    cost_usd_per_tco2_p50=q(cost, 50), cost_p10=q(cost, 10), cost_p90=q(cost, 90),
                                    removal_Mt_p50=(q(gross_T, 50) * s.tonnage_mt) if pd.notna(s.tonnage_mt) else np.nan,
                                    t_air_c=round(float(s.t_air_c), 1) if np.isfinite(s.t_air_c) else np.nan, precip_mm=round(float(s.precip_mm)) if np.isfinite(s.precip_mm) else np.nan,
                                    moisture_factor=round(float(moist), 2) if np.isscalar(moist) else 1.0, slope_deg=round(float(s.slope_deg), 1) if np.isfinite(s.slope_deg) else np.nan,
                                    road_km=round(float(s.road_km), 1), grid_gco2_kwh=round(float(s.grid_gco2_kwh)), grid_src=s.grid_src,
                                    elec_usd_per_mwh=None if pd.isna(s.elec_usd_per_mwh) else float(s.elec_usd_per_mwh), elec_src=s.elec_src))
                draws_store[f"{s.site}|{mode}|{scen}"] = np.c_[gross_T, net_T, cost]
    res = pd.DataFrame(results)
    (ROOT / "data/processed").mkdir(exist_ok=True)
    res.to_csv(ROOT / "data/processed/sites_results.csv", index=False)
    np.savez_compressed(ROOT / "data/processed/sites_draws.npz", **{k.replace("|", "__"): v for k, v in draws_store.items()})
    sites.to_csv(ROOT / "data/processed/sites_env.csv", index=False)
    # ---- gate G3: modelled passive 20-yr extent for 2-8 wt% brucite vs reviewer envelope 0.011-0.080
    pd.set_option("display.width", 250)
    g = res[(res["mode"] == "passive_pile")].groupby("scenario")["gross_t_per_t_p50"].describe()[["min", "50%", "max"]].round(3)
    print("Gate G3, passive 20-yr gross tCO2/t across sites (envelope 0.011-0.080):\n", g)
    for tier in ("FOAK", "NOAK"):
        show = res[res.scenario == tier].pivot_table(index=["track", "site"], columns="mode", values=["cost_usd_per_tco2_p50", "share_not_viable"]).round(0)
        print(f"\n{tier} tier, by site:\n", show.to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
