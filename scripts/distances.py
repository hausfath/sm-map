"""
Great-circle distance from arbitrary points to the nearest road cell, from the
GLOBAL unclipped GRIP4 presence rasters (never a distance transform on a clipped
array: reviewer M3). Road cells are converted to unit vectors and indexed in a
KD-tree; chord distance is converted to arc length.

  from distances import RoadDistance
  rd = RoadDistance("major")            # or "all"
  rd.km(lons, lats) -> np.ndarray of km
"""
import numpy as np, rasterio
from pathlib import Path
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
R_KM = 6371.0088


def _unit(lon, lat):
    lon, lat = np.radians(lon), np.radians(lat)
    return np.c_[np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)]


class RoadDistance:
    def __init__(self, kind="major"):
        path = ROOT / f"data/interim/roads_{kind}_0p01deg.tif"
        with rasterio.open(path) as ds:
            a = ds.read(1)
            rows, cols = np.nonzero(a)
            xs, ys = rasterio.transform.xy(ds.transform, rows.astype(float), cols.astype(float))
        self.n = len(rows)
        self.tree = cKDTree(_unit(np.asarray(xs), np.asarray(ys)))

    def km(self, lons, lats):
        d, _ = self.tree.query(_unit(np.asarray(lons, float), np.asarray(lats, float)))
        return 2 * R_KM * np.arcsin(np.clip(d / 2, 0, 1))


if __name__ == "__main__":
    import time
    t = time.time()
    for kind in ("all", "major"):
        rd = RoadDistance(kind)
        pts = {"Thetford": (-71.30, 46.05), "New Idria": (-120.67, 36.41), "Semail": (58.10, 23.60),
               "Shabanie": (30.02, -20.20), "Mount Keith": (120.55, -27.21), "Asbestos Hill (Nunavik)": (-73.96, 61.81),
               "mid-Sahara": (10.0, 24.0), "mid-Pacific": (-150.0, 0.0)}
        lons, lats = zip(*pts.values())
        km = rd.km(lons, lats)
        print(f"{kind}: {rd.n:,} road cells, built in {time.time()-t:.0f}s")
        for k, v in zip(pts, km):
            print(f"  {k:<26} {v:8.1f} km")
