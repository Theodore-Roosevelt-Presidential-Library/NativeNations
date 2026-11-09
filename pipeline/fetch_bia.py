"""Pull the BIA Tribal Leaders Directory and keep one row per tribe.

Writes data/sources/bia_tribal_leaders.json with organizational fields only.
Leader names, emails and phones are dropped on purpose and must never be committed.
Then fills federal fields (bia_*, hq, official_website) on any nation whose
bia_tld_name matches. Fields entered by hand are never overwritten.

Usage: python pipeline/fetch_bia.py [--apply]
"""
import json, sys, urllib.parse, urllib.request, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "https://biamaps.geoplatform.gov/server/rest/services/Hosted/Tribal_Leaders_Directory_new/FeatureServer/0/query"
KEEP = ["tribefullname", "tribe", "tribealternatename", "biaregion", "biaagency",
        "physicaladdress", "city", "state", "zipcode", "website",
        "latitude", "longtitude", "npsregion", "fwsregion", "blmregion", "directory"]

def fetch():
    tribes, offset = {}, 0
    while True:
        q = urllib.parse.urlencode({"where": "1=1", "outFields": ",".join(KEEP), "orderByFields": "objectid",
                                    "returnGeometry": "false", "f": "json",
                                    "resultOffset": offset, "resultRecordCount": 1000})
        req = urllib.request.Request(f"{URL}?{q}", headers={"User-Agent": "trlibrary-nativenations/0.1"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        if "error" in data:
            sys.exit(f"BIA service error: {data['error']}")
        feats = data.get("features", [])
        for f in feats:
            a = f["attributes"]
            name = (a.get("tribefullname") or "").strip()
            if not name:
                continue
            row = {k: a.get(k) for k in KEEP}
            row["longitude"] = row.pop("longtitude")  # source misspelling
            tribes.setdefault(name, row)
        if not data.get("exceededTransferLimit") or not feats:
            break
        offset += len(feats)
    return dict(sorted(tribes.items()))

def apply(tribes):
    n = 0
    for p in sorted((ROOT / "data/nations").glob("*.json")):
        rec = json.loads(p.read_text())
        t = tribes.get(rec.get("bia_tld_name") or "")
        if not t:
            continue
        rec["bia_region"] = t["biaregion"]; rec["bia_agency"] = t["biaagency"]
        if t.get("latitude") and t.get("longitude"):
            rec["hq"] = {"city": t["city"], "state": t["state"], "lat": t["latitude"], "lon": t["longitude"]}
        if not rec.get("official_website") and t.get("website"):
            rec["official_website"] = t["website"]
        p.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n"); n += 1
    print(f"updated {n} nation records")

if __name__ == "__main__":
    tribes = fetch()
    out = ROOT / "data/sources/bia_tribal_leaders.json"
    out.write_text(json.dumps({"source": URL, "retrieved": datetime.date.today().isoformat(),
                               "count": len(tribes), "tribes": tribes}, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(tribes)} tribes -> {out.relative_to(ROOT)}")
    if "--apply" in sys.argv:
        apply(tribes)
