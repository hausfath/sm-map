#!/usr/bin/env bash
# Stream GRIP4 (CC0) regional road shapefiles into two global 0.01-degree
# presence rasters (all roads; major roads GP_RTP<=3), deleting each raw zip after
# use. Distance-to-road is computed later from the UNCLIPPED global raster.
#   ./scripts/fetch_grip4_roads.sh
set -euo pipefail
cd "$(dirname "$0")/.."
RAW=data/raw/grip4; OUT=data/interim; mkdir -p "$RAW" "$OUT"
ALL=$OUT/roads_all_0p01deg.tif; MAJ=$OUT/roads_major_0p01deg.tif
for f in $ALL $MAJ; do
  [ -f "$f" ] || gdal_create -q -of GTiff -outsize 36000 18000 -a_srs EPSG:4326 -a_ullr -180 90 180 -90 -ot Byte -burn 0 -co COMPRESS=DEFLATE -co TILED=YES -co BIGTIFF=IF_SAFER "$f"
done
for r in 1 2 3 4 5 6 7; do
  z="$RAW/GRIP4_Region${r}_vector_shp.zip"
  [ -f "$OUT/.grip4_region${r}.done" ] && { echo "== region $r: already burned"; continue; }
  echo "== region $r: download"; curl -s -L --retry 5 --retry-all-errors -C - -o "$z" "https://dataportaal.pbl.nl/downloads/GRIP4/GRIP4_Region${r}_vector_shp.zip" || curl -s -L --retry 5 -o "$z" "https://dataportaal.pbl.nl/downloads/GRIP4/GRIP4_Region${r}_vector_shp.zip"
  unzip -q -o "$z" -d "$RAW/r$r"; shp=$(find "$RAW/r$r" -name "*.shp" | head -1); echo "   $(basename "$shp") $(du -sh "$RAW/r$r" | cut -f1)"
  gdal_rasterize -q -burn 1 -at "$shp" "$ALL"
  gdal_rasterize -q -burn 1 -at -where "GP_RTP <= 3" "$shp" "$MAJ"
  rm -rf "$z" "$RAW/r$r"; touch "$OUT/.grip4_region${r}.done"; echo "   rasterised and deleted raw"
done
gdalinfo -stats "$ALL" | grep STATISTICS_MEAN; gdalinfo -stats "$MAJ" | grep STATISTICS_MEAN
echo done
