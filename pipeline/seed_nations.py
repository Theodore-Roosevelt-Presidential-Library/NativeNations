"""Create or refresh one record per Federal Register entity in data/sources/fr_list.json.

Federal fields (fr_*, bia_*, hq, states, official_website when empty) are refreshed.
Hand-entered fields (display_name, aka, nearest_town, links, tags, blurb, review, ...) are never touched.
Run after fetch_fr.py and fetch_bia.py.
"""
import json, re, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
TODAY = datetime.date.today().isoformat()
fr = json.loads((ROOT / "data/sources/fr_list.json").read_text())
bia = json.loads((ROOT / "data/sources/bia_tribal_leaders.json").read_text())["tribes"]
overrides = json.loads((ROOT / "data/sources/name_overrides.json").read_text())
STATES = {"Alabama":"AL","Alaska":"AK","Arizona":"AZ","California":"CA","Colorado":"CO","Connecticut":"CT","Florida":"FL","Idaho":"ID","Iowa":"IA","Kansas":"KS","Louisiana":"LA","Maine":"ME","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Oklahoma":"OK","Oregon":"OR","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Texas":"TX","Utah":"UT","Virginia":"VA","Washington":"WA","Wisconsin":"WI","Wyoming":"WY","Indiana":"IN","Missouri":"MO"}
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower().replace("&", "and"))
bia_norm = {norm(k): k for k in bia}
FR_SRC = {"name": "Federal Register, Indian Entities Recognized (2026)", "url": fr["source"], "retrieved": TODAY}
BIA_SRC = {"name": "BIA Tribal Leaders Directory (organizational fields only)",
           "url": "https://biamaps.geoplatform.gov/server/rest/services/Hosted/Tribal_Leaders_Directory_new/FeatureServer/0",
           "retrieved": bia.get("retrieved", TODAY) if isinstance(bia, dict) and "retrieved" in bia else TODAY}

def bia_match(e):
    if e["fr_name"] in overrides:
        return overrides[e["fr_name"]]
    for c in [e["fr_name"], e["fr_entry"], *e["fr_former_names"]]:
        if norm(c) in bia_norm:
            return bia_norm[norm(c)]
    return None

def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower().replace("&", "and")).strip("-")
    if len(s) > 70:
        s = s[:70].rsplit("-", 1)[0]
    return s

def states_from_name(name):
    found = [abbr for full, abbr in STATES.items() if re.search(rf"(?:,|\bof|&|\band)\s+(?:{full})\b", name)]
    return found + [abbr for abbr in overrides.get("_states", {}).get(name, [])]

existing = {}
for p in (ROOT / "data/nations").glob("*.json"):
    r = json.loads(p.read_text()); existing[r["fr_name"]] = (p, r)

used, created, updated, unmatched = {r["id"] for _, r in existing.values()}, 0, 0, []
for e in fr["entries"]:
    tld = bia_match(e); t = bia.get(tld) if tld else None
    if e["fr_name"] in existing:
        p, r = existing[e["fr_name"]]; updated += 1
    else:
        nid = slug(e["fr_name"]); base, n = nid, 2
        while nid in used: nid, n = f"{base}-{n}", n + 1
        used.add(nid); p = ROOT / "data/nations" / f"{nid}.json"; created += 1
        r = {"id": nid, "display_name": None, "aka": [], "nearest_town": None, "census_aiannh": [],
             "official_website": None, "alliances": [], "tags": [], "blurb": None, "nearby_public_lands": [],
             "links": [], "review": {"status": "draft", "by": None, "date": None, "notes": "Federal facts only."},
             "sources": []}
    r.update({"fr_name": e["fr_name"], "fr_citation": fr["citation"], "fr_former_names": e["fr_former_names"],
              "fr_note": e["fr_note"], "region_group": "alaska" if e["section"] == "alaska" else "lower48",
              "bia_tld_name": tld})
    st = set(states_from_name(e["fr_name"]))
    if e["section"] == "alaska": st.add("AK")
    if t:
        r["bia_region"], r["bia_agency"] = t["biaregion"], t["biaagency"]
        if t.get("state"): st.add(t["state"])
        if t.get("latitude") and t.get("longitude"):
            r["hq"] = {"city": t["city"], "state": t["state"], "lat": round(float(t["latitude"]), 5), "lon": round(float(t["longitude"]), 5)}
        if not r.get("official_website") and t.get("website"):
            w = t["website"].strip()
            r["official_website"] = w if w.startswith("http") else "https://" + w
    else:
        unmatched.append(e["fr_name"]); r.setdefault("bia_region", None); r.setdefault("bia_agency", None); r.setdefault("hq", None)
    if "LUMBEE" in e["fr_name"].upper(): st.add("NC")
    st -= set(overrides.get("_states_remove", {}).get(e["fr_name"], []))
    r["states"] = sorted(st)
    names = {s["name"] for s in r["sources"]}
    for s in ([FR_SRC] + ([BIA_SRC] if t else [])):
        if s["name"] not in names: r["sources"].append(s)
    r.setdefault("last_verified", TODAY)
    p.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")

print(f"created {created}, refreshed {updated}, not in BIA directory: {unmatched}")
