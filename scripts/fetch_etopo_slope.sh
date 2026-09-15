#!/usr/bin/env bash
# ETOPO 2022 30 arc-second surface elevation (NOAA, public domain, 1.64 GB netCDF)
# -> slope in degrees at 30 arcsec, stored as Byte (degrees x 4, capped 63.75),
# DEFLATE-compressed; the netCDF is deleted afterwards.
set -euo pipefail
cd "$(dirname "$0")/.."
RAW=data/raw/etopo; OUT=data/interim/slope_deg_x4_30s.tif; mkdir -p "$RAW"
NC="$RAW/ETOPO_2022_v1_30s_N90W180_surface.nc"
[ -f "$OUT" ] && { echo "exists: $OUT"; exit 0; }
curl -s -L --retry 5 --retry-all-errors -C - -o "$NC" "https://www.ngdc.noaa.gov/thredds/fileServer/global/ETOPO2022/30s/30s_surface_elev_netcdf/ETOPO_2022_v1_30s_N90W180_surface.nc"
ls -la "$NC"
gdaldem slope -q -s 111120 -compute_edges "NETCDF:\"$NC\":z" "$RAW/slope_f32.tif" -co COMPRESS=DEFLATE -co TILED=YES -co BIGTIFF=YES
gdal_translate -q -ot Byte -scale 0 63.75 0 255 -a_nodata 255 -co COMPRESS=DEFLATE -co TILED=YES -co PREDICTOR=2 "$RAW/slope_f32.tif" "$OUT"
rm -f "$NC" "$RAW/slope_f32.tif"
gdalinfo -stats "$OUT" | grep -E "Size is|STATISTICS_MEAN|STATISTICS_MAX"
echo done
