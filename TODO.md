# To-do (decisions and data still needed)

Status as of 2026-09-08. Items are grouped by what unblocks them.

## Before any publication beyond Frontier (internal tool is cleared, 2026-09-08)

- [ ] GRID-Arendal Global Tailings Portal: obtain written permission
      (tailingsdam@grida.no). Licence is CC BY-NC-SA with a no-derivatives
      clause; used internally for facility locations and storage volumes.
      Files: `data/interim/grid_arendal_tailings.csv`,
      `data/interim/tailings_near_ultramafic_INTERNAL.csv`.
- [ ] SGB/CPRM Brazil 1:1M geology: resolve redistribution terms (SGB states it has
      no open-data plan). Used internally for the Brazil footprint and site checks.
      File: `data/raw/brazil_sgb_1m_ultramafic_LICENCE_UNRESOLVED.gpkg`;
      `publish=False` rows in `data/interim/footprint_um.gpkg`.
- [ ] S&P Capital IQ mines layer: never publish (WSP-licensed). Local cross-check only.
- [ ] WSP deliverables: never commit; cite the memo, not the data.
- [ ] Macrostrat per-source licences are not machine-checkable; cite every source
      from the legend/refs and say so in the README.

## Numbers behind paywalls (second scan 2026-09-08 found open author copies; see LITERATURE_SCAN.md section 6)

- [x] Brucite wt% of Thetford Mines chrysotile residues (thesis copy found: 2.94 / 3.91 / 6.44 wt%) and measured CO2 capacity
      (Assima et al. 2012 IJGGC 12:124, 10.1016/j.ijggc.2012.10.001; Assima et
      al. 2013 Thermochim. Acta 566:281, 10.1016/j.tca.2013.06.006; Pronost et al.
      2011 ES&T 45:9413, 10.1021/es203063a).
- [x] Palandri & Kharaka 2004 (PDF retrieved; rows in constants.py) USGS OFR 2004-1068 rate table rows for forsterite,
      brucite, serpentine, magnesite (public domain, site bot-blocked).
- [x] Hamilton et al. 2020 (Monash thesis chapter; unit discrepancy 21.4 kg CO2 vs 21,414 g C flagged) Econ. Geol. 115:303 (10.5382/econgeo.4710): heap-leach
      and direct-air carbonation rates at Woodsreef; passivation factors.
- [x] Wilson et al. 2014 Mount Keith (11 Mt/yr divisor found): tailings throughput that the 39,800 t/yr
      divides by (rate per tonne is unverified without it).
- [x] Gras et al. 2020 Dumont (accepted manuscript found): brucite content, cell geometry, duration.
- [ ] Frontier/DOE-lab column results (expected Q1 2026 per the overview): the
      reactivity, passivation and system-design TEA numbers to replace the
      judgement constants.

## Model and data

- [ ] Pronost et al. 2011 ES&T primary text still not found (brucite 10-15 wt% for Ni residues, secondary only).
- [ ] Reconcile Dumont brucite: 10.2 wt% / 10.2 vol% (Gras) vs 10.88 wt% (Assima 2013).
- [ ] Add per-site passive reproduction gates (Mount Keith 3.6, Dumont 1.4 kg/t/yr; Woodsreef 0.0176 t/t at 33 yr; Black Lake ~0.001 kg/t/yr).
- [ ] Map activated-reactor scenarios to the TEAs' demo / FOAK / NOAK tiers.

- [ ] Anvil C1 TEA (Nevada site, confirmed 2026-09-08): obtain feed throughput so uptake per
      tonne can be derived.
- [ ] Both TEAs are confidential: `docs/TEA_CALIBRATION_INTERNAL.md` and `TEA_INTERNAL`
      in constants.py must be stripped before any publication.

- [ ] Frontier overview site figures ("Thetford ~700 Mt, Jeffrey ~300-500 Mt,
      Baie Verte 20+ Mt, Belvidere ~10 Mt, New Idria 10-30 Mt") are labelled
      "Mt CDR" in the document; confirm whether these are tailings tonnes or
      CO2 tonnes before use.
- [ ] Regional footprint gaps with no open source: Oman/Semail, Turkey, Cyprus,
      non-EU Balkans, Urals, Cuba, Philippines, Indonesia/Malaysia, Zimbabwe
      detail (`docs/DATA_SOURCES_REGIONAL.md`). Options: purchase/licence, or
      digitise from publications, flagged internal-only.
- [ ] Hand audit of the text-only and unstructured Macrostrat legend classes
      (`data/interim/macrostrat_um_legend.csv`), the committed single source of
      truth for what counts as ultramafic.
- [ ] Site coordinates still UNVERIFIED: Shabanie, Gaths, Havelock, Msauli,
      Bazhenovskoye, Dzhetygara, Balangero, Zidani, Dumont, Baptiste.
- [ ] WSP Stage-3 polygons 143 (Western Australia) and 22 (Turkey): centroids
      unknown (geometry never delivered); CarbonIQ export if a login appears.
- [ ] Ports and rail: GRIP4 is roads only. Candidate sources: World Port Index
      (NGA API returned 403), OSM rail (ODbL grey area).
- [ ] Moisture-term functional form and enhancement-factor parameters for the
      aerated/irrigated reactor mode (PLAN.md section 3) before the surface is built.
