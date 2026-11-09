"""Split a history batch (JSON array) into data/histories/{nations|peoples}/{id}.json.
Usage: python pipeline/split_histories.py <batch.json> nations|peoples"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
src, kind = pathlib.Path(sys.argv[1]), sys.argv[2]
ids = {p.stem for p in (ROOT / "data/nations").glob("*.json")} if kind == "nations" else \
      {p["id"] for p in json.loads((ROOT / "data/peoples.json").read_text())["peoples"]}
out = ROOT / "data/histories" / kind; out.mkdir(parents=True, exist_ok=True)
n = 0
for h in json.loads(src.read_text()):
    if h["id"] not in ids:
        print("unknown id", h["id"]); continue
    h.setdefault("status", "draft")
    (out / f"{h['id']}.json").write_text(json.dumps(h, indent=2, ensure_ascii=False) + "\n"); n += 1
print(f"{n} {kind} histories written")
