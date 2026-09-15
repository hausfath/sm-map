# Data inventory: WSP surficial-mineralization deliverables (assessed 2026-09-08)

What is in the folder, what is usable, and what is missing. Written before any
processing so the gaps are on record. Paths are relative to `sm-map/`.

## 1. What WSP did (from the technical memo, RevB draft, 1 Sep 2026)

Three stages for the surface-mineralization (SM) pathway:

1. **Stage 1, suitability surface.** 1 km grid, Equal Earth (EPSG:8857). Eleven
   constraint ("no-go") layers and eleven weighted indicators, combined by
   weighted overlay. Weights (0-100): mineralization potential 100, local mean
   temperature 80, humidity 80, distance from protected areas 80, temperature
   seasonality 60, precipitation 60, distance from urban centres 60, water
   proximity 30, transport access 30, tailings/mine remediation 30, critical
   minerals 10. Cells scoring >= 90 were dissolved into **208 polygons**.
2. **Stage 2, heatmap ranking** of those polygons plus ~37 hand-added legacy
   asbestos / ultramafic mine sites (A-1..A-35, B-36, B-37). Score = 20% area,
   50% area of serpentinite/ophiolite feedstock, 30% Frontier/WSP judgement.
3. **Stage 3, GoldSET option analysis** of eight sites (Mine Jeffrey, Coral Bay
   WA, New Idria, Turkey polygon 22, Woodsreef, Bazhenovskoye, Shabanie, Cana
   Brava). Mine Jeffrey and Coral Bay tied at 68%.

WSP's own limitations list: screening-level only, no techno-economics, weights
are expert judgement, no reactivity/mineralogy information, no tonnage.

## 2. Files and their status

| Item | Location | Status |
|---|---|---|
| Indicator geodatabase | `SM_Indicators.gdb` (11 GB) | 17 vector layers readable with pyogrio/GDAL. 7 raster indicators present (block tables are the bulk of the 11 GB) but **not readable** with the GDAL bundled in rasterio 1.5 (no OpenFileGDB raster driver). Homebrew GDAL 3.13 would read them. |
| Feedstock polygons | layer `PotentialFeedstock_Rev1_202602` | 21,497 polygons, 1,325 Mha total. See section 4: dominated by flood-basalt provinces mis-tagged as an NRCan source. |
| Constraint layers (11) | `SM01_Con_*` .. `SM12_*` | Present and readable. WDPA, UNESCO, LandMark (23 features only), CCVI x3, Ramsar, permafrost, WRI Aqueduct (2,074 basins), UCDB urban. |
| Mines | `SM09_SNPCapitalIQ_LocationMines` | 26,448 points, primary commodity, owner. **Licensed S&P data: cannot be redistributed.** No asbestos-commodity records at all. |
| Tailings | `SM08_GlobalTailings_500m` | 2,113 GRID-Arendal tailings facilities (500 m buffers), with storage volumes. No lithology field. |
| OSM water / transport | `Water_proximity` (11.8 M lines), `TransportationX` (6.9 M lines) | Present, huge, used only for distance rasters. |
| Normalised indicator rasters | `WSP Final Results/01_ Databases/Frontier_SM_Rev1/NormData.gdb` | **Broken/incomplete** (9.6 MB; system catalog table missing; raster block tables absent). Only item names and extents survive. |
| Final suitability surface, constraints raster, WeightedSum | `.../Suitability_SM.gdb`, `Project.gdb` | **Empty directories (0 bytes).** The memo confirms the suitability surface was delivered only inside CarbonIQ (ArcGIS Online). |
| Suitable-surface / excluded-area shapefiles | `02_ Suitability surface/Shapefiles/Surface Mineralization/{Suitable Surface,Excluded Areas}` | **Empty directories.** |
| Stage-2 polygon shapefile | `.../Selected areas to Stage 2/*.zip` | **Zero features** (schema only, EPSG:3857). |
| Heatmap table | `03_ Heatmap/..._Rev5_...xlsx` | 245 rows: 208 polygons (attributes: country, area, suitability, feedstock ha, scores) + legacy mine sites. **No geometry and no coordinates** for any row. |
| Weights | `02_ Suitability surface/Suitability Indicators Weighting Refinement - SM-REV1-final.xlsx` | Weights and text ranges present; normalisation-function cells read `#VALUE!` (formulas lost). Ranges recoverable from `00_ RAW Data/SM_Preprocessing.xls` (buffer from/to, DIR/INV). |
| Option analysis | `04_ Option Analysis/Benchmarks with locations - Final.xlsx`, `Qualitative scoring/*.docx`, `Results/*.png` | Complete for the 8 sites. Includes grid carbon intensity, distance to protected areas/wetlands, water stress, climate stats, policy scores. |
| Ocean liming | `00_ RAW Data/OLFinal.gdb.zip` (533 MB) | Not needed for SM. |
| Correspondence | `Final Report Correspondence.docx` | Empty (title only). |
| ArcGIS project | `Frontier_SM_Rev1.aprx` | Layer definitions only; confirms the layer chain (Nrm_* -> WeightedSum -> Suitability -> Constraints). No weights or raster-function parameters inside. |

## 3. Raster indicators inside SM_Indicators.gdb (metadata only, data unread)

All 1 km Equal Earth unless noted: `LandSurfaceTemperature` (CHELSA bio1),
`SM02_SeasonalTemp` / `SM02_SeasonalTempCelsius` (CHELSA bio4),
`SM04_AnnualPrecip` (CHELSA bio12), `SM06_SolarPower` (1.2 km, status TEMP),
`NASA_Power_RH2M_20260224` (~0.5 deg), `SM00_MetamorphicRock` (GLiM
metamorphic). Every one is re-derivable from public sources.

## 4. Problems found in the feedstock layer

- 2,058 polygons (1,033 Mha, 78% of the layer) carry the source tag "NRC
  Geological Canada", but only 150 Mha of them lie in Canada. The largest are
  the Siberian Traps (66 Mha), Parana (48), Deccan (43), Ethiopian plateau (24),
  Columbia River and Antarctic units. These are **flood basalts**, all scored
  100 as "Mafic and/or Ultramafic".
- Classes that are actually ultramafic (Serpentinite 4.7 Mha, Ophiolite Complex
  30 Mha, Ophiolite with Serpentinite 2.1 Mha) total ~37 Mha and come from
  regional maps with uneven coverage: Europe/Anatolia 11.6 Mha, E/SE Asia 8.3,
  S/C Asia 6.5, N America 5.9, Africa/Middle East 2.6, Oceania 2.0, South
  America 0. Zimbabwe (Great Dyke, Shabanie), Brazil (Cana Brava, Niquelandia),
  Cuba, New Caledonia and the Yilgarn komatiites are absent or nearly so.
- Consequence: the Stage-1 "mineralization potential" indicator is mostly a
  basalt map, which the Frontier pathway note says "reacts too slowly in ambient
  air", while the serpentinite belts the pathway depends on are under-mapped.
- Basalt from Geoscience Australia is split into 9,866 small polygons (19 Mha)
  while the USGS Africa surficial lithology layer has invalid geometries.

## 5. What is missing for the stated goals

Goal 1 (quantify highest-potential areas) and goal 2 (cost and potential):

1. A **global ultramafic map** with consistent classes (serpentinite, peridotite,
   komatiite, kimberlite, ophiolite mantle section) and, where possible,
   brucite/serpentine content. Not in the deliverables.
2. **Tonnage** of accessible material: tailings tonnage at legacy asbestos,
   nickel, chromite, PGE and diamond mines; the WSP scoring used area only.
3. **Site coordinates** for the ~37 legacy mine sites in the heatmap table.
4. Any **cost** inputs: mining/quarrying, comminution, handling, energy and its
   carbon intensity, MRV. None in the deliverables.
5. Any **reactivity / carbonation-rate** basis: tCO2 per tonne of rock as a
   function of mineralogy, grain size, climate and time. None.
6. The delivered **suitability surface and 208 polygons** themselves (geometry).
   Recoverable only by rebuilding the weighted overlay ourselves or by exporting
   from CarbonIQ (ArcGIS Online, Frontier login).
7. A GDAL build with OpenFileGDB raster support, if we want to validate our
   rebuild against WSP's indicator rasters rather than re-deriving them.
