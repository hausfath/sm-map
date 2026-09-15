# Surficial Mineralization Atlas: build plan (v0.1)

Status: revised 2026-09-08 after two independent reviews (spatial statistics /
GIS; low-temperature geochemistry). The v0 plan and every review finding with its
disposition are in `docs/REVIEWS_2026-09-08.md`; the literature basis is in
`docs/LITERATURE_SCAN.md`; what WSP delivered is in `DATA_INVENTORY.md`.

Decisions taken with Zeke (2026-09-08): ultramafic feedstock only (basalt
excluded; it is "not viable" for this pathway in Frontier's own alkalinity
comparison); bottom-up cost model from public spatial inputs now, Frontier
values later; 1 km where the inputs support it; WSP's surface and polygons
rebuilt, not recovered. **The tool is internal to Frontier for now**, so
GRID-Arendal tailings and Brazil SGB geology are used with `publish=False`
flags; permission must be obtained before any wider publication (TODO.md).
Frontier's 0.25 tCO2/t appears as a labelled reference line. Sites with
existing tailings are separated from greenfield sites and highlighted as the
lower-cost track. Both a passive pile and an engineered reactor mode (forced
air, water addition) are modelled, because Frontier's supported projects and
the Frontier overview's four system designs are engineered systems, while the
reviewers' field anchors are all passive.

**What changed from v0.** Both reviews reached the same structural conclusion:
ambient surficial carbonation is limited by reactive brucite content and by CO2
supply into the pile, not by where ultramafic rock outcrops. Every field
measurement of realised uptake (Diavik, Dumont, Mount Keith, Thetford lab
capacities) falls between 0.011 and 0.080 tCO2 per tonne over ~20 years,
against Frontier's working assumption of 0.25. Greenfield quarrying of
serpentinite does not reach $80/tCO2 on any measured number. So the **site
layer of existing fine-grained ultramafic tailings is the headline product**,
and the outcrop surface becomes a clearly labelled exploratory layer that
reports a cost floor, not a potential.

## 1. Products

1. **Site atlas** (points, headline), in two tracks. Track A: existing
   fine-grained ultramafic tailings (legacy asbestos, Ni sulfide and laterite,
   chromite/PGE, kimberlite), zero mining and comminution cost, shown as the
   lower-cost track. Track B: greenfield serpentinite bodies that would be
   purpose-mined (Frontier's "megaproject" concept), where mining and grinding
   dominate cost. Internal sources: 168 GRID-Arendal facilities within 5 km of
   major-class ultramafic (2,974 Mm3 stored; `tailings_near_ultramafic_INTERNAL.csv`). Per site: coordinates (hand-curated),
   tonnage with source and status, mineralogy class and reactive-Mg range,
   processing state (already ground), climate, grid CO2 intensity, distance to
   road, water stress, constraint flags, and modelled removal (tCO2, three
   scenarios) and cost ($/tCO2, median with P10/P90). Target: the 20 to 50
   sites that plausibly matter, with an honest "unknown tonnage" state.
2. **Outcrop context layer** (exploratory). Ultramafic footprint from Macrostrat
   plus regional overlays, coloured by mapping scale and ultramafic fraction,
   with a per-cell **cost floor** for quarry-and-heap under the three uptake
   scenarios. Potential (tonnes) is reported only aggregated to district
   polygons, never per cell.
3. **Reconciliation with WSP**: country-level agree/disagree table against the
   Rev5 attributes, and a quantitative cross-check at the eight GoldSET sites.

## 2. Feedstock: two attributes, not a tier ladder

Each site or map unit carries two independent attributes (reviewer M1/M6):

- **Processing state**: existing tailings (already ground, zero mining cost) or
  outcrop (must be quarried and ground).
- **Reactive mineralogy class**, each with a default reactive-Mg (brucite plus
  labile phases) wt% range held in `constants.py` and flagged as judgement
  until site data replace it:
  partially serpentinized peridotite/dunite (brucite-richest); serpentinite,
  lizardite/chrysotile; serpentinite, antigorite (less reactive); unserpentinized
  dunite/peridotite (olivine only, no brucite: near-zero ambient uptake, same
  logic as excluding basalt); komatiite; kimberlite tailings (primary calcite
  credited at zero); brucite marble / ophicarbonate; Ni-laterite saprolite;
  listwanite / talc-carbonate (already carbonated: **excluded**); Cr-PGE
  orthopyroxenite tailings (low).

Basalt and other mafic rock: excluded, drawn only as a grey reference overlay.
Kimberlite outcrop: dropped (hectare-scale pipes; 11 km2 in Macrostrat).

### 2a. Outcrop footprint (Macrostrat plus regional overlays)

- **Source.** Macrostrat (CC-BY 4.0). Harmonised lithology IDs miss most
  ultramafic units (Thetford's "plutonic: ultramafic rocks" is lith 52,
  generic plutonic), so classification parses each legend entry's
  Major/Minor/Incidental lithology text and unit name
  (`scripts/macrostrat_legend.py`). 'olivine' alone is not a term (it matches
  "olivine basalt" across 1.6 Mkm2 of flood basalt). Harmonised IDs are a
  fallback class ("idonly"), never an override: with IDs as override, GSC Map
  2159A "Intrusive: undivided" granitoid units listing "ultramafics" as one of
  twelve rock names put 83 Mha into the footprint.
- **Polygons** come from Macrostrat's merged "carto" vector tiles
  (`scripts/macrostrat_tiles.py`), which already select one source per location
  by scale precedence, removing cross-scale and cross-source double counting.
  Crawl z5 (serves small-scale sources), z8 and z10 (medium/large). Coarse-only
  hits are **kept** where the finer source is generic (the Chorlton "ophiolite
  complex" units disappear at z8 in Oman and Iran) and flagged low-confidence.
- **Classes and fraction.** Per cell: um_class (major / minor / idonly), the
  winning source and its scale, and an ultramafic fraction with a range
  (major 0.6 [0.35-0.85], minor 0.15 [0.05-0.35], idonly 0.5 [0.25-0.8];
  expert judgement, published as such). Headline footprint = major only.
  Merged footprint 2026-09-08 (on land, tile-simplified, with the regional
  overlays below): major 15.5 Mha (high-confidence 6.4, medium 7.3, low 1.8),
  minor 62 Mha, idonly 0.8 Mha. Table by country in
  `data/interim/footprint_by_country.csv`.
- **Coverage gaps and regional overlays** (`docs/DATA_SOURCES_REGIONAL.md`).
  Macrostrat has no usable ultramafic coverage in Oman/Semail, the Great Dyke,
  New Caledonia, Cuba, Goias, the Philippines, Sabah or the Yilgarn. Overlays
  acquired 2026-09-08 and wired into `scripts/build_footprint.py`: Geoscience
  Australia 1:1M (CC-BY 4.0; 2,417 units, 1.11 Mha), Georep New Caledonia
  peridotite massifs 1:50k (Licence Ouverte; 28k units, 0.48 Mha, includes
  laterite-over-peridotite classes), Quebec SIGEOM bedrock (CC BY 4.0; 8.4k
  units), USGS Africa surficial lithology class "Ultramafic" (public domain;
  69 coarse polygons, supplement only), and Brazil SGB 1:1M (licence unresolved:
  used for site verification, **not published**). Detailed national maps
  replace Macrostrat inside their hull; coarse products only fill gaps.
  Still open with no redistributable source: Oman, Turkey, Cyprus, non-EU
  Balkans, Urals, Cuba, Philippines, Indonesia/Malaysia, Zimbabwe detail.
  The USGS OFR 97-470 world series resolves ophiolites for Iran and SE Asia but
  carries no-redistribution clauses and is excluded from the public repo.
- **Scale as uncertainty.** 86% of the footprint area comes from small-scale
  (~1:1M to 1:5M) mapping. winning_scale is a categorical layer with nominal
  linework precision (large ~0.25 km, medium ~1 km, small ~5 km, tiny ~20 km);
  the viewer caps zoom per cell from it and colours the context layer by it.
  Effective resolution is 5-50 km, not 1 km, and the README says so.
- **Land mask**: Natural Earth 50m; offshore "ocean-continent transition
  peridotite" units (13.6 Mha) are excluded.

### 2b. Sites

Sources: USGS MRDS (public domain; 408 asbestos producers, of which the
chrysotile/serpentinite-hosted subset is kept and crocidolite/amosite in banded
iron formation excluded), Van Gosen 2019 US asbestos release, literature
tonnages (`docs/LITERATURE_SCAN.md`), WSP's Stage-2/3 site names. GRID-Arendal
tailings (CC BY-NC-SA with a no-derivatives clause; bulk access by permission)
is **not** redistributed; pending a permission request it is used only to
locate facilities, with modelled outputs published and no source attributes.
S&P Capital IQ is never published. Coordinates are hand-curated: MRDS
coordinates outside the US can be ~100 km off (Woodsreef), Wikidata returns the
wrong "Jeffrey Mine"; every site is checked against the ultramafic footprint.

## 3. Removal model

Per tonne of rock, over horizon T (default 20 yr):

    removal(T) = f_max * (1 - exp(-k T)) * capacity * phi

- **capacity** (stoichiometric, MgCO3 basis, from molar masses): brucite 0.7546,
  forsterite 0.6256, serpentine 0.4764 tCO2/t; whole rock by mineral mass
  fractions.
- **phi**, CO2:Mg of the product phase: hydromagnesite/dypingite 0.80 (the
  ambient product at Mount Keith), nesquehonite 1.00 (Diavik), artinite 0.50.
  Default 0.80. Magnesite does not nucleate at ambient (step-advancement Ea 159
  kJ/mol vs 45.5 for hydromagnesite growth).
- **f_max**: the reactive-Mg inventory (brucite plus labile phases), not bulk
  stoichiometry; passivation makes extent asymptotic.
- **k**: from the field anchors, with an Arrhenius factor exp(-Ea/R (1/T -
  1/T_ref)), Ea central 45.5 kJ/mol, band 42-60, labelled a carbonate-growth Ea
  (all silicate dissolution values are acid-regime), and a **non-monotonic
  moisture factor** peaking at 20-60 wt% water content and falling toward both
  dry and saturated, derived from precipitation, humidity and evaporation. Arid
  sites are not penalised by default; their water is a cost.
- **CO2 supply**: a gas-transport term (diffusive for passive heaps; advective
  with fan energy where forced) and a closure check: air volume required
  (0.766 g CO2 per m3 at 420 ppm) against air deliverable for the pile depth.
- **Two mineralization modes.** *Passive pile*: the field-anchored rates
  below. *Engineered reactor* (Frontier overview designs: irrigated heap-leach
  style piles, tiered sheltered aerated structures, flow-through aerated
  reactors, thin irrigated layers built up over time): rate multiplied by an
  enhancement factor E on k, with fan and pumping energy and water charged in
  the cost model and the CO2-supply closure enforced (air throughput must
  deliver the CO2 removed). E anchors: aeration ~5x passive (Power et al. 2020,
  verified); brucite carbonation up to ~4x faster with humidity/CO2 control
  (Harrison et al. 2013, verified); heap-leach acceleration at Woodsreef
  (Hamilton et al. 2020, UNVERIFIED, search running). E scenarios LOW 2 /
  CENTRAL 5 / HIGH 20 are judgement until the Frontier/DOE column results
  (expected Q1 2026 per the overview) replace them. f_max is unchanged by E:
  the reactor speeds approach to the reactive-Mg asymptote, it does not raise it
  unless a thermal or mechanochemical pre-treatment is added (a separate,
  costed option, not in v0).
- **Maturity tiers replace LOW/CENTRAL/HIGH (Zeke, 2026-09-08).** The viewer's
  second control is FOAK or NOAK. For the activated reactor each cost category
  (capex, fixed opex, electricity intensity, other variable opex) is drawn
  uniformly between the Arca and Anvil TEA values for that tier, with the site's
  own electricity price and grid intensity substituted and mining added for
  greenfield feed; handling and MRV are not charged separately because the TEAs
  carry them inside their lines. Passive and aerated modes have no TEA, so their
  judgement ranges are scaled by tier (FOAK 1-2x, NOAK 0.5-1x). Mineralogy,
  kinetics and enhancement-factor uncertainty are drawn inside the Monte Carlo.
- **Passive reference envelope** (sourced): 0.010 / 0.030 / 0.080 tCO2/t at
  20 yr, anchored to Diavik 0.011 (Wilson et al. 2011), Dumont field cells 0.028
  (Gras et al. 2020), Mount Keith 0.072 (Wilson et al. 2014, divisor
  unverified), Thetford lab capacities 0.022-0.080 (Assima 2012; Pronost 2011).
  Frontier's 0.25 is shown as a reference line (decision 2026-09-08) labelled
  as requiring 53-57% bulk serpentine conversion or 33-41 wt% brucite.
  Frontier's target rock, "highly serpentinized peridotite (~10% brucite and
  20%+ chrysotile)" (Frontier SM overview), is carried as its own feedstock
  class so the map can show where such rock is claimed versus verified.
- **Durability**: report the solid hydrous-carbonate vs dissolved bicarbonate
  split and a re-release flag.
- **Tonnage**: sites use published tonnage with status; outcrop potential only
  at district level (area x depth scenario x per-lith density: serpentinite
  2.55, peridotite/dunite 3.25, komatiite 2.90 t/m3), labelled a resource.

## 4. Cost model ($/tCO2, distributions not points)

    cost = (mining + comminution + handling/turning + water + transport + MRV + capex recovery) / removal(T), discounted

Leverage on $/tCO2 (reviewer): realised uptake 16.7x; tailings vs quarry 8.8x;
grind target 2x; transport 1.8x; water stress 1.5x; slope/labour <1.4x; MRV 1.1x.
The realised-uptake scenario is therefore the headline control in the viewer;
cost is its dependent readout.

| Term | Treatment | Spatial input |
|---|---|---|
| Mining | 0 for tailings; quarry band $4-30/t rock (Beerling 2020 SI, NASEM 2019, Strefler 2018) with slope and country modifiers applied inside the band | ETOPO 2022 slope (public domain); country cost index |
| Comminution | Strefler 2018 surface-area relation: 19.4 kWh/t at 50 um to 833 at 2 um; tailings already fine | electricity price by country |
| Net CO2 | grinding, fan, haul emissions subtracted; **grid intensity is a net-negativity gate**, cells failing are reported | Ember 2025 CO2 intensity (CC-BY), 104 areas |
| Handling/turning | $/t band, judgement, to be replaced by Frontier data | none |
| Water | absolute m3 per tCO2 against local renewable supply, plus Aqueduct class | WRI Aqueduct 4.0 (CC-BY) |
| Transport | road distance from a **global** unclipped GRIP4 raster (CC0), regionalised truck rate | GRIP4 0.01 deg presence rasters, then EDT |
| Land | ~250 ha per MtCO2 for a 5 m heap at 0.05 t/t, checked against constraints | WSP constraint layers |
| MRV | wide band, acknowledged gap (no published $/tCO2 figure) | none |
| Regulatory | asbestos-handling regime by country; Cr(VI)/Ni leachate cost term | country table |

Every imported cost constant is tagged with its CO2 source (air / flue gas /
pure CO2); CO2-sparging figures (NASEM $10-30) are rejected for this pathway.

**Uncertainty**: two-level Monte Carlo. Non-spatial parameters sampled once per
draw; country-level indices once per country per draw; only per-cell terms
(slope, distance, climate) per cell. Report median and P10/P90 per cell and
site, a variance decomposition, and an explicit realised-uptake floor below
which a cell is "not viable" rather than a very large number. If the spatial
share of $/tCO2 variance is under ~30%, present cost as archetype ranges plus a
spatial modifier rather than as a map.

## 5. Grid and viewer

- Analysis: 1 km Equal Earth (EPSG:8857) for area and tonnage inside the
  footprint; distance fields computed globally in geographic coordinates and
  sampled in. Global context at 0.05 deg.
- Viewer: erw-map architecture. 0.05 deg global textures always loaded; 1 km
  detail as sparse per-district equirectangular tiles. Cost encoded on a log
  scale with sentinel bytes for "not viable" and "no data"; gate: no byte value
  holds more than 2% of cells. Sites drawn on top with tonnage where known.
- Controls: uptake scenario (headline), horizon, product phase, grid-intensity
  gate on/off, constraint toggles, scale-confidence filter.

## 6. Gates (labelled by kind)

Arithmetic: mass closure (sum of mineral MgO <= whole-rock MgO; CO2:Mg matches
the assumed phase). Reproduction: Thetford, Woodsreef, Mount Keith, Diavik,
Baie Verte tonnages match sources; rasterised major-only footprint reproduces the
legend-area total within a few percent. Independent: Mount Keith, Diavik, Dumont
and Clinton Creek passive rates within 2x of the LOW/CENTRAL scenarios;
negative control (brucite-free serpentinite yields ~0 over 20 yr, as Woodsreef
and Clinton Creek show); site-to-footprint distance (every curated site within
5 km of a mapped ultramafic unit, else flagged); footprint vs independent
national compilations in the gap regions. Structural: net-CO2 gate share;
CO2-supply closure; land and water balance; already-carbonated lithologies
credited at zero; blind holdout (Thetford and Mount Keith rank top-10 when
withheld); cross-check against WSP's eight GoldSET sites. Falsifiable target
statement: if no scenario reaches 0.25 tCO2/t, say so.

## 7. Repository and licences

Public GitHub (MIT code). `constants.py` is the single source of truth and
generates the browser constants. Raw inputs downloaded, derived, deleted.
Licences verified: MRDS public domain; CHELSA core V2.1 CC0 (not the annual
product, which is CC-BY); Ember CC-BY 4.0; GRIP4 CC0; Aqueduct CC-BY 4.0;
Geoscience Australia CC-BY 4.0; Macrostrat CC-BY 4.0 with per-source licences
not machine-checkable (all sources cited from legend and refs; README says so);
GRID-Arendal not redistributable; S&P never published; WSP deliverables never
committed. `docs/LITERATURE_SCAN.md` marks every unverified number; nothing
marked UNVERIFIED enters `constants.py`.

## 8. Honest status (to be written before the first figure)

The atlas will state that: the outcrop layer's effective resolution is 5-50 km;
the footprint area is definitional (7 to 96 Mha depending on attribution) and
all totals are published; realised uptake is the dominant uncertainty and is
anchored to four field/lab lines, none near 0.25 tCO2/t; brucite content at the
key sites is unverified in the open literature; no published MRV cost exists;
and that greenfield quarrying is shown as a cost floor only.

## 9. Decisions log

- 2026-09-08 (Zeke): internal tool; GRID-Arendal and Brazil SGB usable with
  publish flags, permission before wider publication; paywalled anchors: search
  for open copies, else TODO.md; 0.25 tCO2/t reference line shown; separate
  existing-tailings sites as the lower-cost track; model engineered reactors
  (forced air, water) as well as passive piles.
- Open: Frontier/DOE column results and system TEA (Q1 2026) to replace the
  judgement constants; Frontier overview site figures labelled "Mt CDR"
  (Thetford ~700, Jeffrey 300-500, Baie Verte 20+, Belvidere ~10, New Idria
  10-30) need a units check before use.
