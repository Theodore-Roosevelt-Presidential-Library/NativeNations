"""Merge research batches from data/research/*.json into nation records.

Batch format: {"batch": "...", "researched": "YYYY-MM-DD", "nations": [
  {"id": "...", "official_website": "https://...", "nearest_town": "...", "aka": ["..."],
   "alliances": ["sdnta"], "tags": ["cultural_center"], "nearby_public_lands": ["Theodore Roosevelt National Park"],
   "links": [{"type": "...", "url": "https://...", "label": "...", "publisher": "nation", "verified": "YYYY-MM-DD"}],
   "notes": "...", "sources": [{"name": "...", "url": "..."}]}]}

Rules: links are added if their URL is new (dedup by URL); aka/tags/alliances are unioned;
official_website and nearest_town only fill empty fields unless --overwrite.
Nothing changes review.status. Run validate.py afterwards.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
vocab = json.loads((ROOT / "data/vocab.json").read_text())
overwrite = "--overwrite" in sys.argv
files = [pathlib.Path(a) for a in sys.argv[1:] if not a.startswith("--")] or sorted((ROOT / "data/research").glob("*.json"))
skipped = []
for f in files:
    b = json.loads(f.read_text()); n_links = 0
    for item in b["nations"]:
        p = ROOT / "data/nations" / f"{item['id']}.json"
        if not p.exists():
            skipped.append(f"{f.name}: unknown id {item['id']}"); continue
        r = json.loads(p.read_text())
        for k in ("official_website", "nearest_town"):
            if item.get(k) and (overwrite or not r.get(k)): r[k] = item[k]
        r["aka"] = list(dict.fromkeys(r.get("aka", []) + item.get("aka", [])))
        r["alliances"] = list(dict.fromkeys(r.get("alliances", []) + [a for a in item.get("alliances", []) if a in vocab["alliances"]]))
        r["tags"] = list(dict.fromkeys(r.get("tags", []) + [t for t in item.get("tags", []) if t in vocab["tags"]]))
        r["nearby_public_lands"] = list(dict.fromkeys(r.get("nearby_public_lands", []) + item.get("nearby_public_lands", [])))
        have = {l["url"].rstrip("/") for l in r["links"]}
        for l in item.get("links", []):
            if l["type"] not in vocab["link_types"] or l["publisher"] not in vocab["publishers"]:
                skipped.append(f"{item['id']}: bad link {l}"); continue
            if not l["url"].startswith("https://") or l["url"].rstrip("/") in have: continue
            r["links"].append({"type": l["type"], "url": l["url"], "label": l["label"], "publisher": l["publisher"],
                               "nation_approved": False, "last_checked": l.get("verified"), "http_status": 200 if l.get("verified") else None})
            have.add(l["url"].rstrip("/")); n_links += 1
        names = {s["name"] for s in r["sources"]}
        for s in item.get("sources", []):
            if s["name"] not in names: r["sources"].append({**s, "retrieved": b["researched"]})
        if item.get("notes"):
            r["review"]["notes"] = (r["review"].get("notes") or "") + f" [{b['researched']} research] " + item["notes"]
        r["last_verified"] = b["researched"]
        p.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
    print(f"{f.name}: {len(b['nations'])} nations, {n_links} links added")
if skipped: print("\n".join(["SKIPPED:"] + skipped))
