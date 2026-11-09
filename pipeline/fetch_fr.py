"""Parse the Federal Register list of federally recognized tribes into data/sources/fr_list.json.

Usage: python pipeline/fetch_fr.py [path-or-url]
Default source: 91 FR 4102 (2026-01-30), FR Doc. 2026-01899, from govinfo.gov.
"""
import json, re, sys, pathlib, urllib.request, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "https://www.govinfo.gov/content/pkg/FR-2026-01-30/html/2026-01899.htm"
CITATION = "91 FR 4102 (2026-01-30)"
LOWER48 = "Indian Tribal Entities Within the Contiguous 48 States"
ALASKA = "Native Entities Within the State of Alaska"
END = "[FR Doc."

def load(src):
    if src.startswith("http"):
        req = urllib.request.Request(src, headers={"User-Agent": "trlibrary-nativenations/0.1"})
        return urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    return pathlib.Path(src).read_text()

def split_entry(text):
    """Separate a trailing explanatory parenthetical from the name itself."""
    name, note, former = text, None, []
    m = re.search(r"\s\(([^()]*(?:\([^()]*\)[^()]*)*)\)$", text)
    if m and len(m.group(1)) > 25:
        note = m.group(1).strip()
        name = text[:m.start()].strip()
        if note.lower().startswith("previously listed as"):
            former = [s.strip() for s in re.split(r";\s*", note[len("previously listed as"):]) if s.strip()]
            former = [re.sub(r"^and\s+", "", f) for f in former]
    return name, note, former

def parse(raw):
    body = html.unescape(re.sub(r"<[^>]+>", "", raw))
    lines = body.splitlines()
    out, section, buf = [], None, ""
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(LOWER48) or line.startswith(ALASKA):
            section = "lower48" if line.startswith(LOWER48) else "alaska"
            while lines[i].endswith(" "):  # heading wraps
                i += 1
            i += 1
            continue
        if line.startswith(END):
            break
        if re.fullmatch(r"\s*\[\[Page \d+\]\]\s*", line):
            i += 1
            continue
        if section and line.strip():
            buf += line
            if not line.endswith(" "):
                out.append((section, re.sub(r"\s+", " ", buf).strip())); buf = ""
        i += 1
    entries = []
    for section, text in out:
        name, note, former = split_entry(text)
        if "(See " in text and "See Supplementary" not in text:
            continue  # cross-reference line, not a separate entity
        entries.append({"fr_entry": text, "fr_name": name, "fr_note": note,
                        "fr_former_names": former, "section": section})
    return entries

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else URL
    entries = parse(load(src))
    out = ROOT / "data/sources/fr_list.json"
    out.write_text(json.dumps({"citation": CITATION, "source": URL, "count": len(entries),
                               "entries": entries}, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(entries)} entries ({sum(e['section']=='alaska' for e in entries)} Alaska) -> {out.relative_to(ROOT)}")
