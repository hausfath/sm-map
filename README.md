# Surficial Mineralization Atlas (internal v0)

An interactive global map of where surficial mineralization of ultramafic rock
could remove CO2, and at what modelled cost. It rebuilds the feedstock layer of
WSP's CarbonIQ screening for Frontier from open geological sources, adds a site
table of existing ultramafic tailings, and runs a removal and cost model over
both.

**Status: internal to Frontier.** The repository is private because the viewer
contains GRID-Arendal tailings facilities, Brazil SGB geology and supplier TEA
calibration that need permission before wider publication (see `TODO.md`).
Client and supplier documents are never committed.

Live map (GitHub Pages, deployed from `src/` on every push to `main`):
https://hausfath.github.io/sm-map/

## What the map shows

- **Ultramafic footprint.** Map units whose dominant lithology is ultramafic,
  from Macrostrat's merged carto tiles plus regional overlays (Geoscience
  Australia 1:1M, Georep New Caledonia, Quebec SIGEOM, USGS Africa, GSC Open
  File 5529, Brazil SGB). Coloured by mapping-scale confidence. Units where
  ultramafic rock is a lesser constituent are a separate grey layer. Effective
  resolution is the mapping scale, 5 to 50 km for most of the footprint.
- **Sites.** Existing fine-grained ultramafic tailings (Track A, the lower-cost
  track) and greenfield or project sites (Track B), with tonnage where a source
  exists, climate, grid intensity, road distance, and modelled uptake
  (tCO2 per tonne at 20 years) and cost ($/tCO2, median with P10 to P90) for
  three system modes (passive pile, aerated reactor, activated reactor) and two
  maturity tiers (FOAK, NOAK).
- **Context layers.** Hasterok et al. 2022 ophiolite provinces (locator only)
  and GRID-Arendal tailings facilities within 5 km of major ultramafic (internal).

Every parameter and its source sits in `scripts/constants.py`. Frontier's
0.25 tCO2/t working assumption is shown as a reference in each site popup;
the field-anchored passive envelope is 0.010 to 0.080 tCO2/t over 20 years.

## Pipeline

Run with the Homebrew Python that has the geo stack (`/opt/homebrew/bin/python3.13`;
bare `python3` on this machine is 3.14 without packages). GDAL 3.13 CLI is needed
for the two shell scripts.

```bash
PY=/opt/homebrew/bin/python3.13
$PY scripts/macrostrat_legend.py                 # classify Macrostrat legend entries -> data/interim/macrostrat_um_legend.csv
$PY scripts/macrostrat_tiles.py --zoom 5         # crawl carto tiles; then --zoom 8 --parents and --zoom 10 --parents
$PY scripts/build_footprint.py                   # merge zooms + regional overlays -> data/interim/footprint_um.gpkg
./scripts/fetch_etopo_slope.sh                   # ETOPO 2022 slope (raw netCDF deleted after use)
./scripts/fetch_grip4_roads.sh                   # GRIP4 road presence rasters (raw zips deleted after use)
$PY scripts/model.py                             # removal + cost Monte Carlo -> data/processed/sites_results.csv
$PY scripts/export_viewer.py                     # write src/data/*.geojson, sites.json, meta.json
./scripts/serve.sh                               # http://localhost:8010/index.html
```

`data/sites_v0.csv` is the hand-curated site table (coordinates, feed class,
tonnage with source and status). `data/raw/` is downloaded, derived from and
deleted; it is not committed. `data/interim/` holds the derived products the
export reads.

## Layout

| Path | Contents |
|---|---|
| `src/` | The viewer: `index.html` (Leaflet, no build step) and `data/` written by the export |
| `scripts/` | Pipeline (above); `constants.py` is the single source of truth |
| `docs/` | Literature scan, regional data-source audit, reviewer findings, TEA calibration (internal) |
| `PLAN.md` | Build plan v0.1 with the decisions log |
| `TODO.md` | Open decisions, permissions and unverified numbers |
| `DATA_INVENTORY.md` | What the WSP deliverables contain and what is missing |

## Licences

Code: MIT. Data: Macrostrat CC-BY 4.0 (per-source licences cited in the legend
and not machine-checkable); Geoscience Australia CC-BY 4.0; Georep New Caledonia
Licence Ouverte; Quebec SIGEOM CC BY 4.0; GSC Open File 5529 Open Government
Licence Canada; USGS MRDS and Africa lithology public domain; Hasterok 2022
CC-BY 4.0; CHELSA V2.1 CC0; Ember CC-BY 4.0; GRIP4 CC0; ETOPO 2022 public domain.
Not redistributable and present only because the tool is internal: GRID-Arendal
tailings (CC BY-NC-SA, no derivatives, permission pending), Brazil SGB 1:1M
(terms unresolved), supplier TEA calibration. S&P Capital IQ and WSP
deliverables are never committed.
