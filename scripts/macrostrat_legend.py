"""
Classify Macrostrat legend entries as ultramafic feedstock (major / minor / none).

  python3.13 scripts/macrostrat_legend.py            # writes data/interim/macrostrat_um_legend.csv

WHY. Macrostrat harmonises ~80k map-unit legend entries to lithology IDs, but the
IDs miss most ultramafic units: "plutonic: ultramafic rocks" (USGS DS424) is coded
to generic 'plutonic' (52). So classification has to read the lithology TEXT with
the Major/Minor/Incidental structure Macrostrat uses where it has it. Free-text
lith strings are treated as ordered lists (first term = dominant). 'olivine' alone
is NOT an ultramafic term: it matches 'olivine basalt' in ~300 flood-basalt units
(1.6 Mkm2) and would put the WSP basalt error straight back in.

Output columns: legend_id, source_id, scale, um_class (major|minor|idonly|none), um_terms,
name, lith, area_km2, lith_id.
"""
import csv, json, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/interim/macrostrat_um_legend.csv"
API = "https://macrostrat.org/api/v2/geologic_units/map/legend?scale={}&format=json"

UM_LITH_IDS = {61, 62, 88, 100, 127, 128, 163, 164, 165, 166, 167, 168, 215, 216}
# term -> tier hint (used later to attach a default mineralogy)
UM_TERMS = {
    # stems, so English / French / Portuguese map legends all match
    "serpentin": "serpentinite",   # serpentinite, serpentinized, serpentinito, serpentinites
    "peridotit": "peridotite",     # peridotite, metaperidotite, peridotito; see also accented
    "péridotit": "peridotite",
    "dunit": "dunite",             # dunite, dunito, dunites
    "harzburg": "peridotite", "lherzol": "peridotite", "wehrlit": "peridotite",
    "pyroxenit": "pyroxenite", "piroxenit": "pyroxenite",
    "komatiit": "komatiite", "kimberlit": "kimberlite", "picrit": "picrite", "ophiolit": "ophiolite",
    "ultramaf": "ultramafic", "ultramáf": "ultramafic", "ultrabasic": "ultramafic", "ultrabásic": "ultramafic",
    "ultra mafi": "ultramafic",
    "soapstone": "talc-carbonate", "talc-carbonate": "talc-carbonate",
    "talc carbonate": "talc-carbonate", "listwanite": "talc-carbonate", "listvenite": "talc-carbonate",
}
TERM_RE = re.compile("|".join(map(re.escape, UM_TERMS)), re.I)
ROCK_NAME = {"serpentinite": "serpentinite", "peridotite": "peridotite", "dunite": "dunite", "pyroxenite": "pyroxenite",
             "komatiite": "komatiite", "kimberlite": "kimberlite", "picrite": "picrite", "ophiolite": "ophiolite complex",
             "ultramafic": "ultramafic rock (undifferentiated)", "talc-carbonate": "talc-carbonate (listwanite)"}
SPECIFIC = {"harzburg": "harzburgite", "lherzol": "lherzolite", "wehrlit": "wehrlite"}


def dominant_rock(*texts):
    """Readable label for the unit's ultramafic rock: the first SPECIFIC rock named (serpentinite,
    peridotite, dunite, harzburgite, ...) in name then lithology text; only if none is named does
    the generic term ('ophiolite complex', 'ultramafic rock (undifferentiated)') stand."""
    GENERIC = {"ophiolite", "ultramafic"}
    generic_hit = ""
    for t in texts:
        t = t or ""
        hits = []
        for k in UM_TERMS:
            m = re.search(re.escape(k), t, re.I)
            if m:
                hits.append((m.start(), k))
        for _, k in sorted(hits):
            label = SPECIFIC.get(k, ROCK_NAME.get(UM_TERMS[k], UM_TERMS[k]))
            if UM_TERMS[k] in GENERIC:
                generic_hit = generic_hit or label
            else:
                return label
    return generic_hit


def um_hits(text):
    """Sorted set of ultramafic term stems present in the text."""
    return sorted({k for k in UM_TERMS if re.search(re.escape(k), text or "", re.I)})


ROLE_RE = re.compile(r"(Major|Minor|Incidental)\s*:\s*\{([^}]*)\}", re.I)
SPLIT_RE = re.compile(r"[,;/]|\band\b|\bto\b|\bwith\b", re.I)


def classify(name, lith, lith_ids):
    """Return (um_class, terms).

    Text first, harmonised lith_id only as a fallback: Macrostrat's IDs are
    text-mined per legend entry and leak, e.g. GSC Map 2159A 'Intrusive:
    undivided' units listing 'ultramafics: serpentinized peridotite' as one of
    twelve rock names carry lith_id 61 (peridotite). Treating that as major puts
    83 Mha of granitoid terrane into the footprint.
    """
    name, lith = name or "", lith or ""
    roles = ROLE_RE.findall(lith)
    if roles:
        role_hits = {r.lower(): um_hits(t) for r, t in roles}
        if role_hits.get("major"):
            return "major", role_hits["major"]
        if role_hits.get("minor"):
            return "minor", role_hits["minor"]
        return "none", []
    if um_hits(name):
        return "major", um_hits(name)
    terms = [t.strip() for t in SPLIT_RE.split(lith) if t.strip()]
    hits = um_hits(lith)
    if hits:
        first = terms[0] if terms else ""
        n_um = sum(1 for t in terms if TERM_RE.search(t))
        if TERM_RE.search(first) or n_um * 2 >= max(len(terms), 1):
            return "major", hits
        return "minor", hits
    if set(lith_ids or []) & UM_LITH_IDS:
        return "idonly", ["harmonised-lith-id"]
    return "none", []


def main():
    rows = []
    for scale in ("tiny", "small", "medium", "large"):
        with urllib.request.urlopen(API.format(scale), timeout=600) as r:
            data = json.load(r)["success"]["data"]
        for x in data:
            cls, terms = classify(x.get("map_unit_name"), x.get("lith"), x.get("lith_id"))
            if cls == "none":
                continue
            rows.append(dict(legend_id=x["legend_id"], source_id=x["source_id"], scale=scale,
                             um_class=cls, um_terms=";".join(terms), um_rock=dominant_rock(x.get("map_unit_name"), x.get("lith")),
                             name=x.get("map_unit_name"),
                             lith=x.get("lith"), area_km2=x.get("area"),
                             lith_id=";".join(map(str, x.get("lith_id") or []))))
        print(f"{scale:7s} {len(data):6d} entries -> {sum(r['scale']==scale for r in rows):5d} ultramafic "
              f"(major {sum(r['scale']==scale and r['um_class']=='major' for r in rows)})")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    for cls in ("major", "minor", "idonly"):
        a = sum((r["area_km2"] or 0) for r in rows if r["um_class"] == cls)
        print(f"  {cls}: {sum(r['um_class']==cls for r in rows)} entries, legend area {a/1e3:,.0f} thousand km2 (all scales, overlapping)")
    print(f"wrote {OUT} ({len(rows)} rows, {len({r['source_id'] for r in rows})} sources)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
