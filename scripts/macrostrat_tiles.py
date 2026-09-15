"""
Crawl Macrostrat's merged 'carto' vector tiles and keep ultramafic map units.

  python3.13 scripts/macrostrat_tiles.py --zoom 5            # coarse sweep, writes hit-tile list
  python3.13 scripts/macrostrat_tiles.py --zoom 8 --parents  # descend into hit tiles

WHY TILES. The carto layer already arbitrates overlapping source maps by scale
precedence (one polygon per location), which removes the cross-scale and
cross-source double counting the API's per-lith queries suffer from. Features
carry map_id, legend_id, source_id, lith text and the full citation. Geometry is
tile-simplified, so the crawl descends to a zoom where the pixel is finer than
the mapping scale being served (z8 ~0.6 km at the equator).

Classification is by legend_id against data/interim/macrostrat_um_legend.csv
(scripts/macrostrat_legend.py). Output: data/interim/macrostrat_um_z{Z}.gpkg
with um_class, um_terms, source_id, scale-of-source unknown here (joined later).
"""
import argparse, csv, gzip, json, math, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import mapbox_vector_tile as mvt
from shapely.geometry import shape, box
from shapely.affinity import affine_transform

ROOT = Path(__file__).resolve().parents[1]
LEGEND = ROOT / "data/interim/macrostrat_um_legend.csv"
TILE = "https://tiles.macrostrat.org/carto/{z}/{x}/{y}.mvt"
R = 6378137.0
SERVED = {}   # (z,x,y) -> {source_id: n_features}; which maps serve each tile


def tile_bounds_3857(z, x, y):
    n = 2 ** z
    w = 2 * math.pi * R
    return (-w / 2 + x * w / n, w / 2 - (y + 1) * w / n, -w / 2 + (x + 1) * w / n, w / 2 - y * w / n)


def fetch(z, x, y, retries=3):
    for i in range(retries):
        try:
            with urllib.request.urlopen(TILE.format(z=z, x=x, y=y), timeout=60) as r:
                b = r.read()
            if b[:2] == b"\x1f\x8b":
                b = gzip.decompress(b)
            if r.status != 200:
                return None
            return b
        except Exception as e:
            if i == retries - 1:
                return None
            time.sleep(1 + i)


def decode_units(b, z, x, y, legend):
    if not b or b[:1] in (b"<", b"{"):      # HTML/JSON error body, not a tile
        return []
    try:
        d = mvt.decode(b)
    except Exception as e:                    # corrupt or truncated tile: log and skip
        print(f"  decode error z{z}/{x}/{y}: {str(e)[:60]}", flush=True)
        return []
    units = d.get("units")
    if not units:
        return []
    ext = units.get("extent", 4096)
    x0, y0, x1, y1 = tile_bounds_3857(z, x, y)
    sx, sy = (x1 - x0) / ext, (y1 - y0) / ext
    out = []
    served = {}
    for f in units["features"]:
        sid = f["properties"].get("source_id")
        served[sid] = served.get(sid, 0) + 1
    SERVED[(z, x, y)] = served
    for f in units["features"]:
        lid = f["properties"].get("legend_id")
        if lid not in legend:
            continue
        g = shape(f["geometry"])
        # mvt y axis: decode() returns y already flipped (origin bottom-left)
        g = affine_transform(g, [sx, 0, 0, sy, x0, y0])
        p = f["properties"]
        out.append((g, dict(map_id=p.get("map_id"), legend_id=lid, source_id=p.get("source_id"),
                            name=p.get("name"), lith=p.get("lith"), ref_source=p.get("ref_source"),
                            ref_title=p.get("ref_title"), z=z, tx=x, ty=y, **legend[lid])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zoom", type=int, default=5)
    ap.add_argument("--parents", help="csv of parent hit tiles (z,x,y) to descend from")
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    legend = {}
    with LEGEND.open() as f:
        for r in csv.DictReader(f):
            legend[int(r["legend_id"])] = dict(um_class=r["um_class"], um_terms=r["um_terms"], leg_scale=r["scale"])
    z = a.zoom
    if a.parents:
        tiles = []
        with open(a.parents) as f:
            for r in csv.DictReader(f):
                pz, px, py = int(r["z"]), int(r["x"]), int(r["y"])
                k = 2 ** (z - pz)
                tiles += [(z, px * k + i, py * k + j) for i in range(k) for j in range(k)]
    else:
        n = 2 ** z
        # skip high latitudes with no land geology of interest (>80N, <-60S)
        tiles = [(z, x, y) for x in range(n) for y in range(n)]
    print(f"z={z}: {len(tiles)} tiles")
    feats, hit_tiles, t0 = [], set(), time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(fetch, *t): t for t in tiles}
        for i, fu in enumerate(as_completed(futs)):
            t = futs[fu]
            units = decode_units(fu.result(), *t, legend)
            if units:
                hit_tiles.add(t); feats += units
            if (i + 1) % 200 == 0:
                print(f"  {i+1}/{len(tiles)} tiles, {len(hit_tiles)} hits, {len(feats)} units, {time.time()-t0:.0f}s", flush=True)
    import geopandas as gpd
    gdf = gpd.GeoDataFrame([p for _, p in feats], geometry=[g for g, _ in feats], crs="EPSG:3857")
    out = ROOT / f"data/interim/macrostrat_um_z{z}.gpkg"
    gdf.to_file(out, driver="GPKG")
    served_out = ROOT / f"data/interim/macrostrat_tile_sources_z{z}.csv"
    with served_out.open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["z", "x", "y", "source_id", "n_features"])
        for (tz, tx, ty), d in sorted(SERVED.items()):
            for sid, n in d.items():
                w.writerow([tz, tx, ty, sid, n])
    hits = ROOT / f"data/interim/macrostrat_hit_tiles_z{z}.csv"
    with hits.open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["z", "x", "y"]); w.writerows(sorted(hit_tiles))
    ee = gdf.to_crs("EPSG:8857")
    print(f"done: {len(gdf)} units in {len(hit_tiles)} tiles; area by class (Mha, tile-simplified):")
    print((ee.geometry.area.groupby(ee.um_class).sum() / 1e10).round(2).to_dict())
    print(f"wrote {out} and {hits}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
