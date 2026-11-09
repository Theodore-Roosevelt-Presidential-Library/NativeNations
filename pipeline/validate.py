"""Check every nation record against docs/schema.md and the project's rules."""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
vocab = json.loads((ROOT / "data/vocab.json").read_text())
REQUIRED = ["id", "fr_name", "fr_citation", "states", "links", "review", "sources", "last_verified"]
BLOCKED_HOSTS = ["natow.org"]  # domain now redirects to spam (2026-11)
errors = []

def err(f, m): errors.append(f"{f}: {m}")

ids = set()
for p in sorted((ROOT / "data/nations").glob("*.json")):
    f = p.name
    try:
        r = json.loads(p.read_text())
    except Exception as e:
        err(f, f"bad JSON: {e}"); continue
    for k in REQUIRED:
        if k not in r: err(f, f"missing {k}")
    if r.get("id") != p.stem: err(f, "id must match file name")
    if not re.fullmatch(r"[a-z0-9-]+", r.get("id", "")): err(f, "id must be a lowercase slug")
    if r.get("id") in ids: err(f, "duplicate id")
    ids.add(r.get("id"))
    if r.get("review", {}).get("status") not in vocab["review_statuses"]: err(f, "bad review.status")
    for t in r.get("tags", []):
        if t not in vocab["tags"]: err(f, f"unknown tag {t}")
    for a in r.get("alliances", []):
        if a not in vocab["alliances"]: err(f, f"unknown alliance {a}")
    if r.get("blurb") and len(r["blurb"]) > 160: err(f, "blurb over 160 characters")
    for i, l in enumerate(r.get("links", [])):
        if l.get("type") not in vocab["link_types"]: err(f, f"link {i}: bad type {l.get('type')}")
        if l.get("publisher") not in vocab["publishers"]: err(f, f"link {i}: bad publisher")
        u = l.get("url", "")
        if not u.startswith("https://"): err(f, f"link {i}: url must be https")
        if any(h in u for h in BLOCKED_HOSTS): err(f, f"link {i}: blocked host")
        if "utm_" in u: err(f, f"link {i}: don't store UTM tags; build adds them")
    # never commit personal contact data from the BIA directory
    blob = p.read_text().lower()
    for bad in ["firstname", "lastname", "\"email\"", "\"phone\""]:
        if bad in blob: err(f, f"contains personal-contact field {bad}")

# places to learn
PL = ROOT / "data/places.json"
if PL.exists():
    KINDS = {"museum", "cultural_center", "heritage_center", "interpretive_center", "historic_site", "tribal_college", "park"}
    OPS = {"nation", "tribal_college", "federal", "state", "university", "nonprofit", "other"}
    pids = set()
    for pl in json.loads(PL.read_text())["places"]:
        f = f"places:{pl.get('id')}"
        for k in ("id", "name", "kind", "operator", "nations", "town", "state", "url", "about", "status", "sources"):
            if k not in pl: err(f, f"missing {k}")
        if pl.get("id") in pids: err(f, "duplicate id")
        pids.add(pl.get("id"))
        if pl.get("kind") not in KINDS: err(f, f"bad kind {pl.get('kind')}")
        if pl.get("operator") not in OPS: err(f, f"bad operator {pl.get('operator')}")
        if not str(pl.get("url", "")).startswith("https://"): err(f, "url must be https")
        if "utm_" in pl.get("url", ""): err(f, "don't store UTM tags")
        for nid in pl.get("nations", []):
            if nid not in ids: err(f, f"unknown nation {nid}")
        if len(pl.get("about", "").split()) > 30: err(f, "about over 30 words")

if errors:
    print("\n".join(errors)); sys.exit(1)
print(f"ok: {len(ids)} nations")
