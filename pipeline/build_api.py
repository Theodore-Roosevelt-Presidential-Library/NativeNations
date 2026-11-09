"""Build the public JSON API into site/api/v1/.

Only federal facts and fields the nation has approved are published.
UTM tags are added to every outbound link here so partners can see Library referrals.
"""
import json, pathlib, datetime, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "site/api/v1"
UTM = {"utm_source": "trlibrary", "utm_medium": "referral", "utm_campaign": "nativenations"}
PUBLISHER_ORDER = ["nation", "alliance", "state_tourism", "aita", "federal", "native_land"]
vocab = json.loads((ROOT / "data/vocab.json").read_text())

def tag(url):
    u = urllib.parse.urlsplit(url)
    q = urllib.parse.urlencode(urllib.parse.parse_qsl(u.query) + list(UTM.items()))
    return urllib.parse.urlunsplit(u._replace(query=q))

def public(r):
    approved = r["review"]["status"] == "nation_approved"
    links = sorted(r["links"], key=lambda l: PUBLISHER_ORDER.index(l["publisher"]))
    return {
        "id": r["id"],
        "name": (r.get("display_name") if approved and r.get("display_name") else r["fr_name"]),
        "fr_name": r["fr_name"], "fr_citation": r["fr_citation"],
        "aka": r.get("aka", []) if approved else [],
        "states": r["states"], "region_group": r.get("region_group"), "nearest_town": r.get("nearest_town"),
        "fr_former_names": r.get("fr_former_names", []), "fr_note": r.get("fr_note"),
        "bia_region": r.get("bia_region"), "hq": r.get("hq"),
        "official_website": r.get("official_website"),
        "alliances": [dict(id=a, **vocab["alliances"][a]) for a in r.get("alliances", [])],
        "tags": r.get("tags", []) if approved else [],
        "blurb": r.get("blurb") if approved else None,
        "nearby_public_lands": r.get("nearby_public_lands", []),
        "links": [{"type": l["type"], "type_label": vocab["link_types"][l["type"]], "label": l["label"],
                   "publisher": l["publisher"], "url": l["url"], "go": tag(l["url"])} for l in links],
        "review_status": r["review"]["status"], "last_verified": r["last_verified"], "sources": r["sources"],
    }

recs = [json.loads(p.read_text()) for p in sorted((ROOT / "data/nations").glob("*.json"))]
pub = [public(r) for r in recs]
(OUT / "nations").mkdir(parents=True, exist_ok=True)
for n in pub:
    (OUT / "nations" / f"{n['id']}.json").write_text(json.dumps(n, indent=1, ensure_ascii=False))
(OUT / "nations.json").write_text(json.dumps(pub, indent=1, ensure_ascii=False))
def has_visit_links(n):
    return any(l["type"] not in ("official",) for l in n["links"])

index = [{"id": n["id"], "name": n["name"], "states": n["states"], "town": n["nearest_town"] or (n["hq"] or {}).get("city"),
          "region": n["bia_region"], "group": n["region_group"], "alliances": [a["id"] for a in n["alliances"]],
          "visit": has_visit_links(n), "lat": (n["hq"] or {}).get("lat"), "lon": (n["hq"] or {}).get("lon"),
          "aka": n["aka"], "former": n["fr_former_names"]} for n in pub]
(OUT / "index.json").write_text(json.dumps(index, separators=(",", ":"), ensure_ascii=False))
(OUT / "nations.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": [
    {"type": "Feature", "geometry": {"type": "Point", "coordinates": [n["hq"]["lon"], n["hq"]["lat"]]},
     "properties": {"id": n["id"], "name": n["name"], "states": n["states"], "point": "tribal government headquarters",
                    "url": f"https://nativenations.labs.trlibrary.com/nations/{n['id']}/"}}
    for n in pub if n["hq"]]}, ensure_ascii=False))
(OUT / "vocab.json").write_text(json.dumps(vocab, indent=1, ensure_ascii=False))
(OUT / "meta.json").write_text(json.dumps({
    "built": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    "count": len(pub),
    "by_status": {s: sum(1 for n in pub if n["review_status"] == s) for s in vocab["review_statuses"]},
    "license": "Federal facts: public domain (Federal Register, BIA, US Census). Library-entered fields: CC BY 4.0. Linked sites belong to their owners.",
}, indent=1))
print(f"built {len(pub)} nations -> site/api/v1/")
