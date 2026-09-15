"""
Single source of truth for every tunable in the SM Atlas.

Rules (see PLAN.md section 7):
  * Every number carries a `src` string naming the primary source, and a `status`
    of "verified" (page-verified by us or a reviewer, DOI given), "derived"
    (computed here from verified inputs), or "judgement" (expert range, to be
    replaced). Nothing marked UNVERIFIED in docs/LITERATURE_SCAN.md appears here.
  * Cost figures carry `co2_source` in {"air", "flue", "pure"}; only "air" enters
    the ambient model (reviewer B6: CO2-sparging costs are a different pathway).
  * The browser constants are generated from this file; never edit them by hand.
"""
from dataclasses import dataclass, field
from typing import Optional

# --------------------------------------------------------------------------
# Molar masses (g/mol), IUPAC 2013 conventional atomic weights
# --------------------------------------------------------------------------
M_Mg, M_Si, M_O, M_H, M_C, M_Ca, M_Fe = 24.305, 28.085, 15.999, 1.008, 12.011, 40.078, 55.845
M_CO2 = M_C + 2 * M_O                      # 44.009
M_BRUCITE = M_Mg + 2 * (M_O + M_H)         # Mg(OH)2 = 58.319
M_FORSTERITE = 2 * M_Mg + M_Si + 4 * M_O   # Mg2SiO4 = 140.691
M_SERPENTINE = 3 * M_Mg + 2 * M_Si + 5 * M_O + 4 * (M_O + M_H)  # Mg3Si2O5(OH)4 = 277.11

# Stoichiometric capacity, MgCO3 basis (tCO2 per tonne of pure mineral).
# derived: one CO2 per Mg. Reviewer-checked to 3 s.f.: 0.7546 / 0.6256 / 0.4764
CAP_MGCO3 = {
    "brucite": 1 * M_CO2 / M_BRUCITE,
    "forsterite": 2 * M_CO2 / M_FORSTERITE,
    "serpentine": 3 * M_CO2 / M_SERPENTINE,
}

# CO2:Mg of the product phase (phi). Ambient products are hydrous (reviewer M4).
# verified: Handbook of Mineralogy wt% CO2 totals reproduce these ratios exactly.
PHI_PRODUCT = {
    "nesquehonite": 1.00,    # MgCO3.3H2O, Diavik (Wilson et al. 2011, 10.1021/es202112y)
    "hydromagnesite": 0.80,  # Mg5(CO3)4(OH)2.4H2O, Mount Keith (Wilson et al. 2014, 10.1016/j.ijggc.2014.04.002)
    "dypingite": 0.80,       # Mg5(CO3)4(OH)2.5H2O
    "artinite": 0.50,        # Mg2(CO3)(OH)2.3H2O
    "magnesite": 1.00,       # does not nucleate at ambient: Ea 159 kJ/mol (Saldi et al. 2009)
}
PHI_DEFAULT = "hydromagnesite"

# --------------------------------------------------------------------------
# Kinetics
# --------------------------------------------------------------------------
EA_KJ_MOL = dict(central=45.5, lo=42.0, hi=60.0)
EA_SRC = ("central: hydromagnesite growth 45.5+-9 kJ/mol, pH 8-10, 25-75 C, Gautier et al. 2014 "
          "10.1016/j.gca.2014.03.044 (verified). Band: lizardite 42.0 (Daval et al. 2013 "
          "10.1016/j.chemgeo.2013.05.020), forsterite 42.6 (Rosso & Rimstidt 2000 "
          "10.1016/S0016-7037(99)00354-3) and 52.9 (Hanchen et al. 2006 10.1016/j.gca.2006.06.1560), "
          "brucite 60 (Jordan & Rammensee 1996 10.1016/S0016-7037(96)00309-2). All silicate values "
          "are acid-regime dissolution; field piles are gas/hydrology limited, so this over-predicts "
          "temperature sensitivity. Labelled a carbonate-growth Ea.")
T_REF_C = 20.0
R_GAS = 8.314e-3  # kJ/mol/K

# Moisture: non-monotonic, optimum water content 20-60 wt% (Harrison et al. 2017
# 10.1016/j.chemgeo.2017.05.003, verified; Quebec residues 22-49 %, Tremblay 2013 MSc, no DOI).
MOISTURE_OPT_WT = (0.20, 0.60)
MOISTURE_STATUS = "judgement: functional form to be specified before the surface is built (reviewer R6)"

# CO2 in air at 420 ppm, 1 atm, 15 C: g per m3 (derived: 420e-6 * 44.009 g/mol * 41.4 mol/m3)
CO2_AIR_G_M3 = 0.766

# --------------------------------------------------------------------------
# Realised uptake scenarios, tCO2 per tonne of bulk rock at HORIZON_YR (reviewer synthesis)
# --------------------------------------------------------------------------
HORIZON_YR = 20
UPTAKE_SCENARIOS = {
    "LOW": dict(t_per_t=0.010, src="Diavik kimberlite tailings, areal rate to 0.5 m over 20 yr: Wilson et al. 2011 "
                                   "ES&T 45:7727, 10.1021/es202112y (verified)"),
    "CENTRAL": dict(t_per_t=0.030, src="Dumont field cells 1.4+-0.3 kg CO2/t/yr x 20 yr: Gras et al. 2020 "
                                       "Chem. Geol. 10.1016/j.chemgeo.2020.119661 (abstract-verified); "
                                       "Thetford lab capacity 0.022 (Assima et al. 2012, brucite 2.2 wt%, "
                                       "number reviewer-verified, paper paywalled)"),
    "HIGH": dict(t_per_t=0.080, src="Mount Keith 39,800 t/yr over 20 yr (Wilson et al. 2014, divisor UNVERIFIED) "
                                    "~0.072; Thetford lab capacity at 8 wt% brucite 0.080 (Pronost et al. 2011)"),
}
FRONTIER_REFERENCE_T_PER_T = dict(
    t_per_t=0.25,
    src="Frontier pathway note: 1 GtCO2/yr needs ~4 Gt rock/yr 'assuming 25% of the rock reacts'. "
        "Note 25% conversion of serpentinite (0.44 t/t whole rock) gives 0.11, not 0.25; 0.25 requires "
        "53-57% bulk conversion or 33-41 wt% brucite (reviewer arithmetic, derived).",
    show_on_map=True,  # Zeke 2026-09-08: show as a labelled reference line
)

# --------------------------------------------------------------------------
# Feedstock classes: reactive-Mg (brucite + labile) wt% ranges. ALL judgement until
# site data replace them; the two attributes are independent (reviewer M1/M6).
# --------------------------------------------------------------------------
@dataclass
class FeedClass:
    name: str
    reactive_mg_wt: tuple       # (lo, central, hi) wt% brucite-equivalent
    density_t_m3: float
    excluded: bool = False
    note: str = ""

FEED_CLASSES = {
    "frontier_target": FeedClass("Frontier target rock: highly serpentinized peridotite, ~10% brucite, 20%+ chrysotile",
                                 (5.0, 10.0, 15.0), 2.6,
                                 note="Frontier SM overview (internal, 2026): 'likely the sweet spot of rock reactivity and "
                                      "abundance'; claimed, not verified at any mapped site"),
    "serp_partial": FeedClass("partially serpentinized peridotite/dunite", (2.0, 5.0, 10.0), 2.9,
                              note="brucite-richest; New Idria fresh serpentinite 7-8 wt% brucite (Mumpton & Thompson 1966, "
                                   "10.1346/CCMN.1966.0140122, verified abstract); Mount Keith 2.5 wt% at depth (Wilson 2014)"),
    "serp_lizardite": FeedClass("serpentinite, lizardite/chrysotile", (0.5, 3.0, 8.0), 2.55,
                                note="Thetford residues: 2.2 wt% brucite (Assima et al. 2012, reviewer-verified number) to 8 wt% "
                                     "(Pronost et al. 2011); papers paywalled; central set between them"),
    "serp_antigorite": FeedClass("serpentinite, antigorite", (0.0, 0.5, 2.0), 2.6, note="less reactive polymorph"),
    "dunite_fresh": FeedClass("unserpentinized dunite/peridotite", (0.0, 0.2, 1.0), 3.25,
                              note="olivine only; near-zero ambient uptake (same logic as excluding basalt)"),
    "komatiite": FeedClass("komatiite", (0.0, 1.0, 3.0), 2.9),
    "kimberlite_tailings": FeedClass("kimberlite tailings", (0.5, 2.0, 5.0), 2.7,
                                     note="primary calcite/dolomite credited at zero; outcrop dropped"),
    "brucite_marble": FeedClass("brucite marble / ophicarbonate", (5.0, 15.0, 30.0), 2.8, note="scarce"),
    "laterite_saprolite": FeedClass("Ni-laterite saprolite", (0.0, 1.0, 3.0), 1.8, note="already fine; >100 Mt/yr moved"),
    "listwanite": FeedClass("listwanite / talc-carbonate", (0.0, 0.0, 0.0), 2.8, excluded=True,
                            note="already carbonated"),
    "opx_tailings": FeedClass("Cr-PGE orthopyroxenite tailings", (0.0, 0.2, 1.0), 3.2, note="low"),
}

# Mineralization system modes (Zeke 2026-09-08: model engineered reactors, not only passive piles).
# E multiplies the rate constant k. Only "activated" raises f_max (pre-treatment liberates Mg from
# serpentine); aeration/irrigation alone speeds approach to the reactive-Mg asymptote.
SYSTEM_MODES = {
    "passive_pile": dict(E=1.0, activation=None, status="verified-anchored",
                         src="field rates: Diavik, Dumont, Mount Keith, Clinton Creek, Black Lake",
                         capex_usd_per_t_rock=dict(lo=1.0, central=3.0, hi=8.0, src="judgement: spreading/turning only"),
                         elec_kwh_per_t_rock=dict(lo=0, central=0, hi=0), water_m3_per_t_rock=dict(lo=0, central=0, hi=0)),
    "reactor_aerated": dict(E=dict(LOW=2.0, CENTRAL=5.0, HIGH=20.0), activation=None, status="judgement",
                    src="aeration ~5x passive, Power et al. 2020 10.1016/j.ijggc.2019.102895 (verified); brucite up to ~4x "
                        "with humidity/CO2 control, Harrison et al. 2013 10.1021/es3012854 (verified); Hamilton et al. 2020 "
                        "heap leach UNVERIFIED; Frontier/DOE column results expected Q1 2026",
                    designs="irrigated heap-leach piles; tiered sheltered aerated structures; flow-through aerated reactors; "
                            "thin irrigated layers built up over time (Frontier SM overview)",
                    capex_usd_per_t_rock=dict(lo=5.0, central=15.0, hi=40.0, src="judgement: pads, air handling, shelter"),
                    elec_kwh_per_t_rock=dict(LOW=20, CENTRAL=60, HIGH=150, src="fans/pumps; reviewer B4 upper case ~300 at 2000 Pa; "
                                                                             "humidity cycling designs (Arca WO2025199640A1) lower"),
                    water_m3_per_t_rock=dict(LOW=0.2, CENTRAL=0.5, HIGH=1.0, src="judgement; Anvil TEA 6.5 t water/tCO2, Arca 1.0")),
    "reactor_activated": dict(E=dict(LOW=5.0, CENTRAL=20.0, HIGH=50.0), status="TEA-anchored (internal)",
                    # activation fraction of BULK serpentine Mg made reactive by thermal/mechanochemical pre-treatment
                    activation=dict(LOW=0.25, CENTRAL=0.55, HIGH=0.80,
                                    src="Arca TEA Aug 2026: 100 kt/yr feed -> 29.7 kt CO2/yr gross = 0.30 tCO2/t feed, "
                                        "i.e. ~63% of serpentinite capacity (0.476 x 0.8 x ~1.25 Mg-normalised); CENTRAL set below it"),
                    src="Arca (Thetford, Bell Mine) and Anvil C1 TEAs shared with Frontier; INTERNAL, do not publish",
                    capex_usd_per_t_rock=dict(lo=20.0, central=45.0, hi=120.0,
                                              src="Arca: total capital incl. financing $114M demo / $198-234M FOAK-NOAK for 100 kt/yr feed x 20-30 yr "
                                                  "= $57-114/t feed; NOAK capex $25/tCO2 x 0.30 = $7.5/t; FOAK demo $212/tCO2 x 0.30 = $64/t"),
                    elec_kwh_per_t_rock=dict(LOW=200, CENTRAL=300, HIGH=400,
                                             src="Arca 0.7-1.3 MWh/tCO2 x 0.30 t/t = 210-390 kWh/t feed (microwave activation + comminution); "
                                                 "Anvil 0.61-0.79 MWh/tCO2 (feed rate not given)"),
                    water_m3_per_t_rock=dict(LOW=0.3, CENTRAL=0.5, HIGH=2.0, src="Arca 1 t/tCO2; Anvil 6.5 t/tCO2 x uptake"),
                    fixed_other_usd_per_tco2=dict(lo=45.0, central=90.0, hi=250.0,
                                                  src="fixed opex + other variable opex per tCO2: Arca NOAK 11+37, FOAK 22+48, demo 54+99; "
                                                      "Anvil NOAK 2+29, C1 82+73")),
}

# Maturity tiers (Zeke 2026-09-08): FOAK = the suppliers' "this project" columns, NOAK = their
# nth-of-a-kind columns. Activated-reactor costs are drawn UNIFORMLY between the Arca and Anvil
# values per category, so both TEAs bound every draw. Passive and aerated modes have no TEA; their
# judgement ranges are scaled by the tier multipliers below (flagged).
TIERS = {
    "FOAK": dict(label="First project (FOAK)",
                 activated=dict(  # $/tCO2 gross unless noted; (Arca demo, Anvil C1)
                     capex_usd_per_tco2=(212.5, 235.7), fixed_opex_usd_per_tco2=(52.3, 77.6),
                     elec_mwh_per_tco2=(0.608, 1.3), elec_usd_per_mwh_default=(46.0, 120.0),
                     other_var_usd_per_tco2=(69.2, 95.0),   # maintenance, grinding media, IP, MRV, water
                     uptake_t_per_t=(0.25, 0.297),           # Arca 100 kt feed -> 29.7 kt; Anvil feed unknown
                     src="Arca TEA Aug 2026 'This Project (demo)' gross-basis: capex 212.5, fixed 52.3, energy 61.8 (1.3 MWh @ $46), other var 95.0 -> $421.6 gross / $439 net; "
                         "Anvil C1 TEA gross-basis: capex 235.7, fixed 77.6, energy 73.0 (0.608 MWh @ $120), other var 69.2 -> $455.5 gross / $482 net"),
                 judgement_scale=dict(capex=(1.0, 2.0), handling=(1.0, 1.5), fixed_other=(1.0, 2.0))),
    "NOAK": dict(label="Nth plant (NOAK)",
                 activated=dict(
                     capex_usd_per_tco2=(24.3, 53.2), fixed_opex_usd_per_tco2=(2.3, 10.8),
                     elec_mwh_per_tco2=(0.7, 0.786), elec_usd_per_mwh_default=(40.0, 60.0),
                     other_var_usd_per_tco2=(28.7, 35.8),
                     uptake_t_per_t=(0.25, 0.297),
                     src="Arca NOAK gross-basis: capex 24.3, fixed 10.8, energy 30 (0.7 MWh @ $40), other var 35.8 -> $100.9 gross / $105 net; "
                         "Anvil NOAK gross-basis: capex 53.2, fixed 2.3, energy 47.2 (0.786 MWh @ $60), other var 28.7 -> $131.4 gross / $134 net"),
                 judgement_scale=dict(capex=(0.5, 1.0), handling=(0.7, 1.0), fixed_other=(0.5, 1.0))),
}
# Site electricity price overrides ($/MWh) where a TEA or tariff is known; else the tier default range.
ELEC_PRICE_OVERRIDES = [
    dict(name="Quebec (HydroQuebec industrial)", lon=-71.9, lat=46.0, radius_km=300, usd_per_mwh=46.0, src="Arca TEA demo column"),
    dict(name="Abitibi, Quebec", lon=-78.4, lat=48.6, radius_km=200, usd_per_mwh=46.0, src="Arca TEA demo column"),
    dict(name="Nevada", lon=-117.0, lat=39.0, radius_km=350, usd_per_mwh=120.0, src="Anvil C1 TEA (NOAK assumes $60 PV+BESS PPA)"),
]

# Frontier-supported project TEAs (INTERNAL; shared with Frontier under the TEA template, May 2025 version)
TEA_INTERNAL = {
    "arca_thetford": dict(site="Thetford Mines (Bell Mine), Quebec", feed_ktpa=100, gross_tco2_yr=29727, uptake_t_per_t=0.297,
                          total_usd_per_tco2_net=dict(demo=439, foak=140, noak=105), elec_mwh_per_tco2=dict(demo=1.3, foak=0.9, noak=0.7),
                          elec_usd_per_mwh=dict(demo=46, noak=40), grid_gco2_kwh=1.2, net_negativity=0.965,
                          capex_usd_per_tco2_net=dict(demo=221, foak=30, noak=25), process="comminution + microwave mineral activation + smart churning",
                          src="[Shared] Arca TEA August 2026.xlsx"),
    "anvil_c1": dict(site="Nevada (confirmed by Zeke 2026-09-08); contact-metamorphic brucite-bearing and serpentinite ore; NV grid 280 g/kWh",
                     gross_tco2_yr=42000, feed_ktpa=None, uptake_t_per_t=None,
                     total_usd_per_tco2_net=dict(c1=482, noak=134), elec_mwh_per_tco2=dict(c1=0.608, noak=0.786),
                     elec_usd_per_mwh=dict(c1=120, noak=60), water_t_per_tco2=6.5, net_negativity=0.945,
                     capex_usd_per_tco2_net=dict(c1=249, noak=54), process="crush, sort, comminution + pelletization, air handling, reactors",
                     src="[Anvil C1] Frontier TEA.xlsx"),
}

# Frontier Alkalinity POV (internal, v7) feedstock figures used for context panels
FRONTIER_POV = {
    "nickel_tailings": dict(production_mtpa=177, cdr_potential_t_per_t=0.66, src="POV table citing UN Global Tailings Review 2020; Bullock 2021"),
    "pge_tailings": dict(production_mtpa=88.5, cdr_potential_t_per_t=0.417, src="POV table; Bullock 2021"),
    "kimberlite_tailings": dict(production_mtpa=20, cdr_potential_t_per_t=0.558, src="POV table; Bullock 2021"),
    "chrysotile_production": dict(production_mtpa=1.3, reserves_gt=">2", cdr_potential_t_per_t=(0.5, 0.7), src="POV table citing USGS 2024; Bullock 2021"),
    "brucite_production": dict(production_mtpa=1.5, cdr_potential_t_per_t=1.15, price_usd_per_t=">150", src="POV table citing Caserini 2022; NAS mCDR"),
    "grind_energy_gj_per_t": {100: 0.04, 50: 0.07, 2: (1.5, 3.0)},
    "extraction_comminution_emissions_t_per_t_removed": (0.05, 0.10),
}

# Ultramafic fraction of a map unit by legend class (reviewer B3; judgement, published as such)
UM_FRACTION = {"major": (0.35, 0.60, 0.85), "minor": (0.05, 0.15, 0.35), "idonly": (0.25, 0.50, 0.80),
               "ophiolite": (0.15, 0.40, 0.60)}   # mantle section share of a mapped ophiolite complex (judgement)
SCALE_PRECISION_KM = {"large": 0.25, "medium": 1.0, "small": 5.0, "tiny": 20.0}

# --------------------------------------------------------------------------
# Costs. Every entry: value(s), unit, co2_source, status, src.
# --------------------------------------------------------------------------
COST = {
    "quarry_usd_per_t": dict(lo=3.97, central=10.0, hi=30.1, unit="$/t rock", co2_source="air", status="verified",
                             src="Beerling et al. 2020 SI (Indonesia 3.97, US 6.99, Italy 8.30; 10.1038/s41586-020-2448-9); "
                                 "NASEM 2019 mine+crush olivine 10.0 (10.17226/25259); Strefler et al. 2018 "
                                 "investment+O&M 30.1 (10.1088/1748-9326/aaa9c4). Spatial modifier applied inside the band."),
    "grind_kwh_per_t": dict(points={50: 19.4, 10: 127.8, 2: 833.0}, unit="kWh/t at P80 um", co2_source="air",
                            status="verified", src="Strefler et al. 2018 surface-area relation (19.4 at 50 um, 833 at 2 um); "
                                                   "Li, Planavsky, Reinhard 2024 127.8 at 10 um (10.3389/fclim.2024.1380651). "
                                                   "No Bond work index exists for these rocks (reviewer M10)."),
    "handling_usd_per_t": dict(lo=2.0, central=6.0, hi=15.0, unit="$/t rock", co2_source="air", status="judgement",
                               src="reviewer working value $6/t; Frontier data to replace"),
    "truck_usd_per_t_km": dict(lo=0.05, central=0.10, hi=0.12, unit="$/t/km", co2_source="air", status="verified",
                               src="Strefler 2018 citing Renforth 2012 $0.05/t/km (one remove); erw-map US $0.12 via USDA, "
                                   "BR/IN ~2x lower (erw-truck-rate-research memory)"),
    "mrv_usd_per_tco2": dict(lo=5.0, central=20.0, hi=40.0, unit="$/tCO2", co2_source="air", status="judgement",
                             src="no published $/tCO2 MRV figure (Isometric ERW v1.1 and Puro 2025 v2 checked by reviewer); "
                                 "Klitzke, Hausfather & Ransohoff 2022 hypothetical $40 EW / $20 DAC"),
    "fan_dp_pa": dict(lo=500, central=2000, hi=5000, unit="Pa", co2_source="air", status="judgement",
                      src="reviewer B4 worked example: 2000 Pa, 20% stripping -> ~302 kWh/t at 0.05 t/t over 20 yr"),
    "discount_rate": dict(central=0.05, status="judgement", src="erw-map convention"),
}
COST_REJECTED = {
    "nasem_sparged_tailings_usd_per_tco2": dict(lo=10, hi=30, co2_source="pure",
                                                src="NASEM 2019 Table 6.1; CO2-gas sparging = point-source route, not air (reviewer B6)"),
}
COST_COMPARATORS_AIR = {
    "kelemen_2019_surficial": dict(lo=55, hi=500, unit="$/tCO2", src="Kelemen et al. 2019 10.3389/fclim.2019.00009 (verified)"),
    "mcqueen_2020_mgo": dict(lo=46, hi=159, unit="$/tCO2", src="McQueen et al. 2020 10.1038/s41467-020-16510-3 (verified)"),
}

# Freight (Frontier Alkalinity POV, citing BTS; CBO 2022 and EPA emission factors). US-centric.
FREIGHT = {
    "truck": dict(usd_per_t_km=0.2426 / 1.609, gco2_per_t_km=181 / 1.609, src="Frontier POV table: 24.26 c/ton-mile, 181 gCO2/ton-mile (BTS; CBO 2022; EPA)"),
    "rail": dict(usd_per_t_km=0.0459 / 1.609, gco2_per_t_km=23 / 1.609, src="Frontier POV table: 4.59 c/ton-mile, 23 gCO2/ton-mile"),
    "water": dict(usd_per_t_km=0.0294 / 1.609, gco2_per_t_km=64 / 1.609, src="Frontier POV table: 2.94 c/ton-mile, 64 gCO2/ton-mile"),
}

# Data-use status (tool is INTERNAL to Frontier for now, Zeke 2026-09-08). Anything with
# publish=False must be dropped or re-licensed before wider publication (see TODO.md).
DATA_PUBLISH_FLAGS = {
    "grid_arendal_tailings": dict(publish=False, reason="CC BY-NC-SA + no-derivatives; permission required"),
    "tea_internal": dict(publish=False, reason="supplier TEAs shared with Frontier; confidential"),
    "frontier_docs": dict(publish=False, reason="Frontier SM overview and Alkalinity POV are internal"),
    "brazil_sgb_1m": dict(publish=False, reason="SGB has no open-data plan; terms unresolved"),
    "snp_capital_iq_mines": dict(publish=False, reason="WSP-licensed commercial data"),
    "wsp_deliverables": dict(publish=False, reason="client material"),
}

# Subnational grid CO2 intensity overrides (gCO2/kWh), applied within a radius of the named point.
# Ember is national; Quebec and Nevada differ from their national means by >100x / 30%.
GRID_OVERRIDES = [
    dict(name="Quebec (HydroQuebec)", lon=-71.9, lat=46.0, radius_km=300, gco2_kwh=1.2, src="Arca TEA LCA sheet: HydroQuebec 0.0012 t/MWh"),
    dict(name="Abitibi, Quebec (HydroQuebec)", lon=-78.4, lat=48.6, radius_km=200, gco2_kwh=1.2, src="Arca TEA LCA sheet: HydroQuebec 0.0012 t/MWh"),
    dict(name="Nunavik off-grid diesel", lon=-73.96, lat=61.81, radius_km=300, gco2_kwh=750, src="judgement: isolated diesel generation; no grid connection"),
    dict(name="Vermont / New England (ISO-NE)", lon=-72.5, lat=44.8, radius_km=150, gco2_kwh=230, src="judgement placeholder: ISO-NE marginal ~0.2-0.3 kg/kWh; replace with eGRID NEWE"),
    dict(name="Nevada", lon=-117.0, lat=39.0, radius_km=350, gco2_kwh=280, src="Anvil C1 TEA: NV grid 280 g/kWh (2025)"),
    dict(name="California", lon=-120.6, lat=36.4, radius_km=250, gco2_kwh=185, src="WSP option analysis, Carbon Intensity.docx: ~0.15-0.22 kg/kWh"),
    dict(name="Western Australia SWIS", lon=120.5, lat=-27.2, radius_km=900, gco2_kwh=500, src="WSP: ~0.45-0.55"),
    dict(name="New South Wales NEM", lon=150.7, lat=-30.4, radius_km=500, gco2_kwh=650, src="WSP: ~0.60-0.70"),
    dict(name="Brazil Centre-West (SIN)", lon=-48.5, lat=-14.0, radius_km=800, gco2_kwh=105, src="WSP: ~0.09-0.12"),
    dict(name="Zimbabwe", lon=30.1, lat=-20.2, radius_km=500, gco2_kwh=500, src="WSP: ~0.45-0.55"),
    dict(name="Turkey", lon=36.5, lat=38.0, radius_km=800, gco2_kwh=400, src="WSP: ~0.38-0.42"),
    dict(name="Urals (Russia)", lon=61.5, lat=57.0, radius_km=600, gco2_kwh=410, src="WSP: ~0.37-0.45"),
]

# Net-negativity gate: grid CO2 intensity (Ember yearly, CC-BY 4.0, latest year in data/raw)
GRID_INTENSITY_SRC = "Ember yearly_full_release_long_format.csv, variable 'CO2 intensity', gCO2/kWh"

# --------------------------------------------------------------------------
# Site tonnages used as reproduction gates (docs/LITERATURE_SCAN.md section 2)
# --------------------------------------------------------------------------
SITE_TONNAGE_MT = {
    "Thetford Mines / Asbestos / Nunavik region": dict(mt=800, status="reported-uncited",
        src="BAPE 2020 Rapport 351; figure carries no citation in the report and includes Nunavik"),
    "Black Lake pile": dict(mt=110, status="verified", src="Nowamooz et al. 2018 10.1021/acs.est.8b01128"),
    "Woodsreef tailings": dict(mt=25, status="verified", src="NSW DPE 2018 fact sheet (plus 75 Mt waste rock)"),
    "Baie Verte tailings": dict(mt=47, status="verified-inconsistent", src="AMEC 2005 Phase I ESA (also 'over 40')"),
    "Clinton Creek tailings": dict(mt=10, status="verified", src="Wilson et al. 2009 10.2113/gsecongeo.104.1.95"),
    "Cassiar tailings": dict(mt=17, status="verified", src="Wilson et al. 2009"),
    "Havelock/Bulembu milled": dict(mt=50, status="verified", src="Gan et al. 2022 10.17159/2411-9717/1612/2022"),
    "Shabanie + Gaths tailings": dict(mt=143, status="approximate", src="Runganga 2024 10.56532/mjsat.v4i1.159"),
    "Lowell (Belvidere) pile": dict(mt=45, status="one-remove", src="Van Baalen et al. 2009 citing EPA 2009a: 30-60 Mt"),
}
# Verified 2026-09-08 from open author copies (docs/LITERATURE_SCAN.md section 6)
BRUCITE_WT_VERIFIED = {
    "Black Lake residue (Thetford)": dict(wt=2.94, src="Assima et al. 2012 IJGGC 12:124, via Assima PhD thesis 2014 (U. Laval, corpus.ulaval.ca/handle/20.500.11794/24881) ch. III"),
    "Black Lake <75 um": dict(wt=3.914, src="Assima et al. 2013 Thermochim. Acta 566:281, thesis ch. VI Table VI.5; 1.04 wt% at 1.8-2 mm"),
    "Asbestos (Jeffrey) residue <75 um": dict(wt=6.442, src="Assima et al. 2013, Table VI.5"),
    "Dumont Ni residue": dict(wt=10.88, alt=(10.2, "wt% or vol%, Gras et al. 2020 citing Assima"), src="Assima et al. 2013 Table VI.5; unreconciled 10.2 vs 10.88"),
    "Raglan": dict(wt=0.0, src="Assima et al. 2013 Table VI.5"),
    "Renard kimberlite": dict(wt=1.759, src="Assima et al. 2013 Table VI.5"),
    "Mount Keith": dict(wt=(1.0, 2.5), src="Wilson et al. 2014 accepted manuscript (Waikato Research Commons 10289/8967): 1.0-2.5 wt% at depth; 2.5 used as model input"),
    "New Idria fresh serpentinite": dict(wt=(7.0, 8.0), src="Mumpton & Thompson 1966 (abstract)"),
}
LIQUID_SATURATION_OPT = dict(beta=(0.30, 0.35), src="Assima et al. 2012: initial rate highest near beta 30-35%; higher counter-productive (CO2 diffusion)")

# Palandri & Kharaka 2004, USGS OFR 2004-1068 (public domain), transcribed from the PDF tables.
# log k in mol m-2 s-1 at 25 C; Ea kJ/mol; n = order in H+ (or P(CO2) for the carbonate mechanism).
PALANDRI_KHARAKA_2004 = {
    "forsterite": dict(acid=(-6.85, 67.2, 0.470), neutral=(-10.64, 79.0), table="23 p.34"),
    "enstatite": dict(acid=(-9.02, 80.0, 0.600), neutral=(-12.72, 80.0), table="26 p.37"),
    "diopside": dict(acid=(-6.36, 96.1, 0.710), neutral=(-11.11, 40.6), table="26 p.37"),
    "anorthite": dict(acid=(-3.50, 16.6, 1.411), neutral=(-9.12, 17.8), table="13 p.24"),
    "lizardite": dict(acid=(-5.70, 75.5, 0.800), neutral=(-12.40, 56.6), table="30 p.39"),
    "chrysotile": dict(neutral=(-12.00, 73.5), base=(-13.58, 73.5, -0.230), table="30 p.39"),
    "brucite": dict(acid=(-4.73, 59.0, 0.500), neutral=(-8.24, 42.0), table="32 p.40"),
    "magnesite": dict(acid=(-6.38, 14.4, 1.000), neutral=(-9.34, 23.5), carbonate=(-5.22, 62.8, 1.000), table="33 p.41; Ea assigned from calcite"),
    "_note": "antigorite is not in the report; do not substitute",
}

PASSIVE_RATE_ANCHORS = {
    "Woodsreef 33-yr passive": dict(tco2_per_t=0.0176, years=33, src="Hamilton et al. 2020 via Hamilton PhD thesis 2019 (Monash, 10.4225/03/5b09f98e7230b) ch. 5: 17.6 g CO2/kg over 33 yr"),
    "Dumont field cell EC-2": dict(kg_per_t_yr=1.4, brucite_wt=10.9, thickness_m=0.35, years=4,
                                   src="Gras et al. 2020 accepted manuscript (corpus.ulaval.ca 20.500.11794/39308): 1.4+-0.3 kg CO2/t/yr, 2011-2015; EC-1 2 m thick, 104 t"),
    "Mount Keith": dict(tco2_yr=39800, tailings_mt_yr=11.0, kg_per_t_yr=3.6, brucite_wt=(1.0, 2.5),
                        src="Wilson et al. 2014 accepted manuscript: 11 Mt/yr over ~16.6 km2 TSF2; ~4 wt%/yr hydromagnesite in upper 10 cm"),
    "Clinton Creek": dict(tco2_yr=6300, src="Wilson et al. 2009 (verified); 164 kt over 26 yr"),
    "Black Lake": dict(tco2_yr=100, src="Nowamooz et al. 2018 (verified abstract)"),
}
ENHANCED_RATE_ANCHORS = {
    "Woodsreef direct CO2 gas, 28 d": dict(g_co2_per_kg_yr=(209.8, 261.1), co2_source="pure/enriched", src="Hamilton et al. 2020 (thesis ch. 5): 16.1-20.1 g CO2/kg in 28 d = 33 yr of passive"),
    "Woodsreef simulated heap leach": dict(kg_co2_m2_yr=21.4, co2_source="air (leachate carbonation)", src="Hamilton et al. 2020 abstract: ~3.5x the highest passive field rate (Clinton Creek); results text says 21,414 g C/m2/y, unreconciled units"),
    "Baptiste aeration": dict(kg_co2_m2_yr=19.0, factor_vs_passive=5.4, co2_source="air", src="Power et al. 2020"),
}
