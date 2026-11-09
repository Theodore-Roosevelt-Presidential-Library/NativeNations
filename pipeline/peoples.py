"""Resolve data/peoples.json into memberships: {people_id: [nation ids]} including children rolled up to parents."""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent

def resolve(nations):
    data = json.loads((ROOT / "data/peoples.json").read_text())["peoples"]
    ids = {n["id"] for n in nations}
    direct = {}
    for p in data:
        m = {n["id"] for n in nations if any(re.search(rx, n["fr_name"]) for rx in p["match"])}
        m |= {x for x in p["extra"] if x in ids}
        m -= set(p["exclude"])
        direct[p["id"]] = m
    full = {}
    for p in data:  # parents include their children's members
        kids = [c["id"] for c in data if c["parent"] == p["id"]]
        full[p["id"]] = direct[p["id"]].union(*[direct[k] for k in kids])
    by_nation = {}
    for pid, m in direct.items():
        for nid in m:
            by_nation.setdefault(nid, []).append(pid)
    missing = [x for p in data for x in p["extra"] if x not in ids]
    return data, {k: sorted(v) for k, v in full.items()}, by_nation, missing
