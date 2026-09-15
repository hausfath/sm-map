# Regional ultramafic geology sources (audit of 2026-09-08)

A web-research subagent tested each source live (curl, WFS/REST GetCapabilities,
direct downloads). Everything below was actually opened unless marked UNVERIFIED.
Purpose: fill the districts where Macrostrat has no usable ultramafic coverage
(PLAN.md 2a). Licence text is as quoted on the source.

## Usable in the public pipeline

| District | Source | Access | Lithology field | Licence |
|---|---|---|---|---|
| New Caledonia | Georep "Massifs de péridotites" FeatureServer: `https://services1.arcgis.com/TZcrgU6CIbqWt9Qv/arcgis/rest/services/massifs_peridotites/FeatureServer`; full 1:50k geology `https://sig-public.gouv.nc//plateforme_telechargement/Geologie_SHP_Lyr_50000.7z` (44 MB) | REST / 7z | `unite`, `lithologie` (e.g. "Harzburgites", "Serpentinites"), `ultra_mafi` flag | Licence Ouverte (Etalab) |
| Quebec | SIGEOM bedrock geology `https://gq.mines.gouv.qc.ca/documents/SIGEOM/TOUTQC/FRA/SHP/SIGEOM_QC_Geologie_du_socle_SHP.zip` (476 MB) | SHP | `ETQT_LITH`, `DESC_1_A` (e.g. "Serpentinite, harzburgite, peridotite, pyroxenite ...") | CC BY 4.0 |
| Canada national | GSC Map 1860A (Wheeler et al. 1996, 1:5M) via NRCan OSTR `https://ostr-backend-prod.azure.cloud.nrcan-rncan.gc.ca/server/api/core/bitstreams/cc690136-a8a3-4e8f-af16-4a5f94462207/content` | Arc/Info coverage | `RXTP`/`SUBRXTP` = "ultramafic intrusive rocks" | Open Government Licence - Canada |
| Global (provinces) | Hasterok et al. 2022, Earth-Sci. Rev. 231:104069; data `github.com/dhasterok/global_tectonics`, Zenodo 10.5281/zenodo.5093930; `global_gprv.shp`, `prov_type = 'ophiolite complex'` (18 polygons incl. Semail, Sulawesi, Greater Antilles) | SHP | province outlines only | data CC-BY-4.0 (code GPL-3) |
| Global (lithology) | GSC Open File 5529 (Chorlton 2007) via OSTR; `intrusdt.dbf` field `INTCLASS` includes 'ULTRAMAFIC SUITE', 'MAFIC-ULTRAMAFIC SUITE' | SHP + 203 dBase tables | detailed but relational | Open Government Licence - Canada |
| Africa (coarse) | USGS Africa Terrestrial Ecosystems surficial lithology, ScienceBase 63e4622ed34e9fa19a9c007a (42 MB, 90 m raster) | IMG raster | `lithology` value 8 = "Ultramafic" (single bucket) | public domain |
| Greece only | EGDI 1:1M WFS `https://maps.europe-geology.eu/wfs/3034/` layer `ms:geologicunitview`, `representativelithology_title = ultramaficIgneousRock` (195 features); Turkey, Cyprus and non-EU Balkans return 0 features | WFS | | CC-BY-4.0 |
| Puerto Rico | USGS OFR 98-38 `https://pubs.usgs.gov/of/1998/of98-038/`, unit `KJs` serpentinite | e00 | `FMATN` | public domain |
| Australia | Geoscience Australia Surface Geology 1:1M REST layer 11 (already in `data/raw/ga_1m_ultramafic.gpkg`, 2,417 polygons, 1.11 Mha) | REST | `lithology` | CC-BY 4.0 |

## Added 2026-09-10: WSP's own ultramafic classes

The WSP `PotentialFeedstock_Rev1_202602` layer, set aside because 78% of it is
mis-tagged flood basalt, contains 4,188 polygons (35.6 Mha on land) in three
usable classes: Serpentinite (BGR IGME5000, GA, USGS, EGDI), Ophiolite complex
with Serpentinite (BGR), and Ophiolite Complex (25.7 Mha, tagged NRCan: this is
GSC Open File 5529, Chorlton 2007, "Generalized geology of the world", Open
Government Licence Canada). 23.8 Mha of it lay outside the footprint, mostly
Indonesia 4.8, Iran 3.4, Saudi Arabia 1.9, Oman 1.8, Turkey 1.7, PNG 1.3, Cuba
1.0, India 0.7, Mexico 0.7, Myanmar 0.6. It is now a "supplement" overlay with
its own class `ophiolite` (mantle-section fraction 0.15-0.60, judgement) and
medium confidence. All underlying sources are open, so it is publishable.

Also added 2026-09-10: the full GSC Open File 5529 database (of_5529.zip, 577 MB,
NRCan OSTR bitstream a2141be1-...; Open Government Licence Canada). The
`intrusdt.dbf` table links to `maf.shp` on RUNO_ID2; INTCLASS = ULTRAMAFIC SUITE
(186 rows) and MAFIC-ULTRAMAFIC SUITE (343) give 477 domain polygons, 71 Mha,
with China 1.1 Mha, Kazakhstan 2.2, Myanmar 1.8, Zimbabwe 2.4, Japan 1.0. These
are 1:35M-scale domains, so they enter as low confidence: ultramafic suite as
class `ophiolite` (fraction 0.15-0.6), mafic-ultramafic suite as `minor`.
Derived file: `data/raw/gsc5529_ultramafic_suites.gpkg`; raw archive deleted.

Still missing after this: **China detail** (Chorlton lumps its ultramafic belts into
"mafic and/or ultramafic", 57 Mha; Macrostrat has zero ultramafic units in
China; the USGS 97-470 Far East layer lumps ultrabasic with basic and is
non-redistributable). Hasterok et al. 2022 province outlines (Lancangjiang,
Ailaoshan, Erdaojing) are used as a low-confidence locator there.

## Usable locally only (licence unresolved or restrictive)

| District | Source | Issue |
|---|---|---|
| Brazil | SGB/CPRM `https://geoportal.sgb.gov.br/server/rest/services/geologia/litoestratigrafia_1000000/MapServer` (also `_250000` etc.); `LITOTIPOS` names dunito/serpentinito/cromitito (Niquelandia, Barro Alto confirmed) | SGB states it has no open-data plan; no licence text. Query for local use; ask SGB before redistributing. |
| South Africa | Council for Geoscience ArcGIS Portal, per-sheet 1:250k FeatureServers (e.g. Pretoria 2528), `descr` e.g. "Hortonolite dunite, harzburgite, pyroxenite" | CGS copyright with mandatory attribution; not CC. |
| Iran, SE Asia, Far East, Australia-NZ, Europe | USGS OFR 97-470 series on ScienceBase (e.g. 97-470B doi 10.5066/P9GI9NS4). 97-470F `TYPE='w'` and 97-470G `GLG in ('Mzo','To')` resolve ophiolites | UNESCO/AGSO/ESRI no-redistribution clauses; 97-470B (Arabia) is time-stratigraphic only, no ophiolite code. Exclude from the public repo. |

## Confirmed gaps (no open vector source found)

Oman/Semail (national ministry site is a JS app; BRGM 1:100k sheets not open), Turkey
(MTA sells vectors), Cyprus/Troodos, non-EU Balkans, Russia/Kazakhstan Urals (VSEGEI
WMS only, 403 from here), Cuba, Philippines (MGB blocks crawlers), Zimbabwe (403),
Zambia (registration), Eritrea, Egypt (PDF maps only), Malaysia (registration),
Indonesia (1:5M, login). CGMW Africa 1:10M is paid and non-redistributable.
OneGeology is closed. Stopgap for these districts: Hasterok province polygons
(locator only) and GSC 5529 classes, both flagged low confidence.

## Notes

- Macrostrat's citation "Geological Survey of Canada Map 2159A" for its source 2
  does not correspond to a real GSC map number; the 1:5M national map is 1860A.
- The Dryad "Geodatabase of ultramafic soils of the Americas" (10.5061/dryad.4xgxd25gj,
  CC0) could not be downloaded (bot check); worth a manual retry.
