"""Match Census TIGER AIANNH areas to nation records and write simplified boundary GeoJSON.

Inputs: TIGER/Line AIANNH shapefile (path arg), data/nations/*.json (hq points, names).
Outputs:
  data/boundaries/areas/{AIANNHCE}.geojson   (detail ~50 m, per area incl. reservation + off-reservation trust land)
  data/boundaries/overview.geojson           (all matched areas, ~500 m, for the national map layer)
  data/boundaries/matches.json               (nation id -> areas, with match method; ALL matches are drafts for review)
Rules: federal areas only (AIANNHR = F). Match 1: the BIA headquarters point falls inside the area.
Match 2 (only if no area contains the headquarters): every distinctive word of the area name appears in the nation's federal name, and the area lies within ~100 km of the headquarters.
Overrides in data/boundaries/overrides.json win (add / remove per nation).
"""
import json, re, sys, pathlib, collections
import shapefile
from shapely.geometry import shape, Point, mapping
from shapely.ops import unary_union

ROOT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else pathlib.Path(".")
r = shapefile.Reader(sys.argv[1])
areas = collections.defaultdict(lambda: {"parts": [], "recs": []})
for sr in r.iterShapeRecords():
    rec = sr.record.as_dict()
    if rec["AIANNHR"] != "F":
        continue
    g = shape(sr.shape.__geo_interface__)
    if not g.is_valid: g = g.buffer(0)
    a = areas[rec["AIANNHCE"]]; a["parts"].append((rec, g)); a["recs"].append(rec)

nations = [json.loads(p.read_text()) for p in sorted((ROOT / "data/nations").glob("*.json"))]
STOP = set("the of and band bands tribe tribes indian indians nation nations reservation community rancheria colony village native pueblo trust land lands off confederated san santa st".split())
def words(s): return {w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP and len(w) > 3}

overrides = {}
ov = ROOT / "data/boundaries/overrides.json"
if ov.exists(): overrides = json.loads(ov.read_text())

matches = {}
union = {code: unary_union([g for _, g in a["parts"]]) for code, a in areas.items()}
claimed = set()  # areas that contain some nation's headquarters
for n in nations:
    if n.get("hq") and n["hq"].get("lat") is not None:
        pt = Point(n["hq"]["lon"], n["hq"]["lat"])
        claimed |= {code for code, u in union.items() if u.contains(pt)}
for n in nations:
    found = {}
    if n.get("hq") and n["hq"].get("lat") is not None:
        pt = Point(n["hq"]["lon"], n["hq"]["lat"])
        for code, u in union.items():
            if u.contains(pt): found[code] = "hq_point"
    if not found and n.get("hq") and n["hq"].get("lat") is not None:
        nw = words(n["fr_name"])
        for code, a in areas.items():
            aw = words(a["recs"][0]["NAME"])
            rec = a["recs"][0]
            near = Point(float(rec["INTPTLON"]), float(rec["INTPTLAT"])).distance(pt) < 1.0  # ~100 km
            if aw and aw <= nw and near and code not in claimed:
                found[code] = "name"
    o = overrides.get(n["id"], {})
    for c in o.get("add", []): found[c] = "manual"
    for c in o.get("remove", []): found.pop(c, None)
    if found:
        matches[n["id"]] = [{"aiannhce": c, "name": areas[c]["recs"][0]["NAMELSAD"].replace(" Reservation", " Reservation"),
                             "geoids": sorted(rec["GEOID"] for rec in areas[c]["recs"]), "method": m,
                             "land_sq_mi": round(sum(rec["ALAND"] for rec in areas[c]["recs"]) / 2589988.11),
                             "status": "draft"} for c, m in found.items()]

out = ROOT / "data/boundaries"; (out / "areas").mkdir(parents=True, exist_ok=True)
used = {m["aiannhce"] for ms in matches.values() for m in ms}
shared = collections.Counter(m["aiannhce"] for ms in matches.values() for m in ms)
def feat(rec, g, tol):
    gs = g.simplify(tol, preserve_topology=True)
    gj = json.loads(json.dumps(mapping(gs)), parse_float=lambda x: round(float(x), 4))
    kind = {"R": "reservation", "T": "off-reservation trust land"}.get(rec["COMPTYP"], "statistical area")
    return {"type": "Feature", "geometry": gj, "properties": {"aiannhce": rec["AIANNHCE"], "geoid": rec["GEOID"], "name": rec["NAMELSAD"], "kind": kind, "lsad": rec["LSAD"], "source": "U.S. Census Bureau, TIGER/Line 2026 AIANNH"}}
overview = []
for code in sorted(used):
    a = areas[code]
    fc = {"type": "FeatureCollection", "features": [feat(rec, g, 0.0005) for rec, g in a["parts"]]}
    (out / "areas" / f"{code}.geojson").write_text(json.dumps(fc, separators=(",", ":")))
    overview += [feat(rec, g, 0.005) for rec, g in a["parts"]]
(out / "overview.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": overview}, separators=(",", ":")))
(out / "matches.json").write_text(json.dumps({"_note": "Draft matches between nations and Census areas. Method hq_point = BIA headquarters falls inside the area; name = area name words found in the nation's federal name; manual = overrides.json. Shared areas list more than one nation. Census areas are legal or statistical geography, not homelands; where a nation describes its boundary differently, the nation's description governs.", "matches": matches, "shared_areas": {c: [nid for nid, ms in matches.items() if any(m["aiannhce"] == c for m in ms)] for c, k in shared.items() if k > 1}}, indent=1, ensure_ascii=False))
print(f"federal areas {len(areas)}, nations matched {len(matches)}/{len(nations)}, areas used {len(used)}, shared {sum(1 for k in shared.values() if k>1)}")
methods = collections.Counter(m["method"] for ms in matches.values() for m in ms); print(methods)
