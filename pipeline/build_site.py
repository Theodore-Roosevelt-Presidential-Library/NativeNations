"""Build the HTML site from site/api/v1/ (run build_api.py first).

Writes: index.html (search), map.html, embed.html, about.html, nations/{id}/index.html,
widgets/{card,list,map}.html, robots.txt, sitemap.xml.
Set PUBLIC = True only after the pilot is approved; until then every page is noindex.
"""
import json, pathlib, html, datetime, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
BASE = "https://nativenations.labs.trlibrary.com"
REPO = "https://github.com/Theodore-Roosevelt-Presidential-Library/NativeNations"
PUBLIC = False
KBYG = "https://americanindigenoustourism.org/know-before-you-go-guides/"
LEAFLET = ('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="">'
           '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>')
STATE_NAMES = {"AK":"Alaska","AL":"Alabama","AZ":"Arizona","CA":"California","CO":"Colorado","CT":"Connecticut","FL":"Florida","IA":"Iowa","ID":"Idaho","IN":"Indiana","KS":"Kansas","LA":"Louisiana","MA":"Massachusetts","ME":"Maine","MI":"Michigan","MN":"Minnesota","MO":"Missouri","MS":"Mississippi","MT":"Montana","NC":"North Carolina","ND":"North Dakota","NE":"Nebraska","NM":"New Mexico","NV":"Nevada","NY":"New York","OK":"Oklahoma","OR":"Oregon","RI":"Rhode Island","SC":"South Carolina","SD":"South Dakota","TX":"Texas","UT":"Utah","VA":"Virginia","WA":"Washington","WI":"Wisconsin","WY":"Wyoming"}
e = lambda s: html.escape(str(s if s is not None else ""), quote=True)

nations = json.loads((SITE / "api/v1/nations.json").read_text())
vocab = json.loads((SITE / "api/v1/vocab.json").read_text())

def page(title, body, *, desc="", path="/", nav="", extra_head="", widget=False):
    robots = "" if PUBLIC else '<meta name="robots" content="noindex, nofollow">'
    canon = f"{BASE}{path}"
    if widget:
        return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>{e(title)}</title><link rel="stylesheet" href="/assets/app.css">{extra_head}</head>
<body class="widget">{body}<script src="/assets/widget.js"></script></body></html>"""
    def link(href, label, key):
        cur = ' aria-current="page"' if key == nav else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{robots}
<title>{e(title)} | Theodore Roosevelt Presidential Library</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:type" content="website"><meta property="og:site_name" content="Theodore Roosevelt Presidential Library">
<link rel="stylesheet" href="/assets/app.css">
<script src="/assets/common.js"></script>
{extra_head}
</head><body>
<header class="site-head"><div class="wrap">
  <a class="logo" href="https://www.trlibrary.com/" aria-label="Theodore Roosevelt Presidential Library"><img src="/assets/brand/trpl-logo-horizontal-black.svg" alt="Theodore Roosevelt Presidential Library"></a>
  <a class="site-title" href="/">Native Nations</a>
  <nav class="site-nav" aria-label="Main">{link("/", "Search", "search")}{link("/states/", "States", "states")}{link("/peoples/", "Peoples", "peoples")}{link("/map.html", "Map", "map")}{link("/embed.html", "Embed &amp; API", "embed")}{link("/about.html", "About", "about")}</nav>
</div></header>
{'' if PUBLIC else '<div class="devnote"><div class="wrap">In development. Listings are drafts and have not yet been reviewed by the nations or their tourism alliances.</div></div>'}
<main>{body}</main>
<footer class="site-foot"><div class="wrap">
<p>Native Nations points you to the tourism resources Native nations and their partners publish themselves. Every link goes to the site that owns the content.</p>
<p>Names come from the Federal Register list of federally recognized tribes (91 FR 4102, January 30, 2026). Headquarters, regions and websites come from the Bureau of Indian Affairs Tribal Leaders Directory. Map data &copy; OpenStreetMap contributors.</p>
<p>See something wrong? <a href="{REPO}/issues/new">Tell the Library</a>. A project of the <a href="https://www.trlibrary.com/">Theodore Roosevelt Presidential Library</a> &middot; <a href="https://labs.trlibrary.com/">Library Labs</a></p>
</div></footer>
</body></html>"""

def write(rel, text):
    p = SITE / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)

def states_text(n):
    return ", ".join(STATE_NAMES.get(s, s) for s in n["states"])

def fact_rows(n):
    rows = []
    def row(k, v):
        if v: rows.append(f"<tr><th scope=row>{k}</th><td>{v}</td></tr>")
    row("Name in the federal list", e(n["fr_name"]))
    if n["aka"]: row("Also known as", e(", ".join(n["aka"])))
    if n["fr_former_names"]: row("Previously listed as", e("; ".join(n["fr_former_names"])))
    if n["fr_note"] and not n["fr_former_names"]: row("Federal list note", e(n["fr_note"]))
    if n.get("peoples"):
        row("Peoples", ", ".join(f'<a href="/peoples/{pp["id"]}/">{e(pp["name"])}</a>' for pp in n["peoples"]) + ' <span class="caption">(draft)</span>')
    row("State" + ("s" if len(n["states"]) > 1 else ""), ", ".join(f'<a href="/states/{s.lower()}/">{e(STATE_NAMES.get(s, s))}</a>' for s in n["states"]))
    if n["hq"]: row("Tribal government headquarters", e(f'{n["hq"]["city"]}, {STATE_NAMES.get(n["hq"]["state"], n["hq"]["state"])}'))
    if n["nearest_town"] and (not n["hq"] or n["nearest_town"] != n["hq"]["city"]): row("Nearest town", e(n["nearest_town"]))
    if n.get("areas"):
        row("Reservation and trust land", "<br>".join(f'{e(a["name"])} <span class="caption">({a["land_sq_mi"]:,} sq mi of land, U.S. Census)</span>' for a in n["areas"]))
    if n["bia_region"]: row("BIA region", e(n["bia_region"]))
    if n["official_website"]:
        u = n["official_website"]; host = urllib.parse.urlsplit(u).netloc.replace("www.", "")
        row("Official website", f'<a href="{e(u)}" rel="noopener">{e(host)}</a>')
    for a in n["alliances"]:
        row("Tourism alliance", f'<a href="{e(a["url"])}" rel="noopener">{e(a["name"])}</a>')
    row("Federal recognition", e(n["fr_citation"]))
    return "\n".join(rows)

def history_links(n):
    hs = [l for l in n["links"] if l["type"] in ("history", "reference")]
    if not hs:
        return ""
    out = ['<h2>History</h2><p class="caption">Start with the nation&rsquo;s own telling.</p><ul class="linklist">']
    for l in sorted(hs, key=lambda l: l["type"] != "history"):
        out.append(f'<li><a href="{e(l["go"])}" rel="noopener" target="_blank">{e(l["label"])}</a><span class="caption">{e(l["type_label"])} &middot; {e(urllib.parse.urlsplit(l["url"]).netloc.replace("www.", ""))}</span></li>')
    out.append("</ul>")
    return "\n".join(out)

def visit_links(n):
    links = [l for l in n["links"] if l["type"] not in ("official", "history", "reference")]
    if not links:
        site = f' Start with the <a href="{e(n["official_website"])}" rel="noopener">official website</a>.' if n["official_website"] else ""
        return f'<p class="empty">Tourism links for this nation haven&rsquo;t been added yet.{site}</p>'
    groups = [("From the nation", [l for l in links if l["publisher"] == "nation"]),
              ("From tourism partners", [l for l in links if l["publisher"] != "nation"])]
    out = []
    for title, ls in groups:
        if not ls: continue
        out.append(f'<p class="label">{title}</p><ul class="linklist">')
        for l in ls:
            out.append(f'<li><a href="{e(l["go"])}" rel="noopener" target="_blank">{e(l["label"])}</a><span class="caption">{e(l["type_label"])} &middot; {e(urllib.parse.urlsplit(l["url"]).netloc.replace("www.", ""))}</span></li>')
        out.append("</ul>")
    return "\n".join(out)

def jsonld(n):
    d = {"@context": "https://schema.org", "@type": "GovernmentOrganization", "name": n["name"],
         "alternateName": [x for x in [n["fr_name"], *n["aka"]] if x != n["name"]] or None,
         "url": n["official_website"] or None,
         "address": {"@type": "PostalAddress", "addressLocality": n["hq"]["city"], "addressRegion": n["hq"]["state"], "addressCountry": "US"} if n["hq"] else None,
         "subjectOf": {"@type": "WebPage", "url": f'{BASE}/nations/{n["id"]}/'}}
    d = {k: v for k, v in d.items() if v}
    return f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>'

def fact_page(n):
    loc = n["hq"]
    where = states_text(n)
    desc = f'Plan a visit with {n["name"]}: official website, tourism links and tribal government headquarters in {where}.'
    mapblock = ""
    if loc:
        mapblock = f"""<h2>Where</h2><div id="minimap" class="minimap" style="height:340px" data-lat="{loc['lat']}" data-lon="{loc['lon']}" data-label="{e(n['name'])}" data-areas="{",".join(a["aiannhce"] for a in n.get("areas", []))}"></div>
<p class="caption">The point marks the tribal government headquarters.{" Shaded areas are reservation and trust land as drawn by the U.S. Census Bureau (TIGER/Line 2026). These are legal boundaries, not homelands, and some nations describe theirs differently." if n.get("areas") else ""} <a href="https://native-land.ca/" rel="noopener">Explore Indigenous territories on Native Land Digital</a>.</p>"""
    snippet = e(f'<div data-nativenations="card" data-id="{n["id"]}"></div>\n<script src="{BASE}/embed.js" async></script>')
    body = f"""<section class="fact-hero"><div class="wrap">
<div class="crumb"><a href="/">All nations</a> &rsaquo; {" / ".join(f'<a href="/states/{s.lower()}/">{e(STATE_NAMES.get(s, s))}</a>' for s in n["states"])}</div>
<h1>{e(n["name"])}</h1>
{f'<p class="legal">{e(n["fr_name"])}</p>' if n["name"] != n["fr_name"] else ''}
{f'<p>{e(n["blurb"])}</p>' if n["blurb"] else ''}
</div></section>
<div class="wrap fact-body">
<div>
<h2>Plan your visit</h2>
{visit_links(n)}
<p class="caption" style="margin-top:14px">Before you go, read the <a href="{KBYG}" rel="noopener">Know Before You Go guides</a> from the American Indigenous Tourism Association. Each nation sets its own rules for photography, ceremonies and permits.</p>
{history_block("nations", n["id"])}
{history_links(n)}
{land_block(n)}
{cession_block(n)}
{mapblock}
</div>
<aside>
<h2>Facts</h2>
<table class="facts">{fact_rows(n)}</table>
<h2>Embed this card</h2>
<div class="snippet">{snippet}</div>
<p class="caption">Sources: {", ".join(f'<a href="{e(s["url"])}" rel="noopener">{e(s["name"])}</a>' for s in n["sources"])}. Last verified {e(n["last_verified"])}. Status: {e(n["review_status"].replace("_", " "))}.<br>
<a href="{REPO}/issues/new?title={urllib.parse.quote('Correction: ' + n['name'])}">Suggest a correction</a> &middot; <a href="/api/v1/nations/{n['id']}.json">JSON</a></p>
</aside>
</div>
<script>window.NN_MINI=true</script><script src="/assets/map.js" defer></script>"""
    return page(n["name"], body, desc=desc, path=f'/nations/{n["id"]}/', extra_head=LEAFLET + jsonld(n))

def pby_root(p, plist):
    return next((x["name"] for x in plist if x["id"] == p["parent"]), p["name"])

HIST = ROOT / "data/histories"
def history_block(kind, id_):
    f = HIST / kind / f"{id_}.json"
    if not f.exists():
        return ""
    h = json.loads(f.read_text())
    if h.get("hold"):
        return ""
    srcs = "".join(f'<li><a href="{e(x["url"])}" rel="noopener">{e(x["name"])}</a></li>' for x in h.get("sources", []))
    paras = "".join(f"<p>{e(par)}</p>" for par in h["summary"].split("\n\n"))
    return f"""<h2>History</h2>
<p class="label" style="color:var(--night)">Draft &middot; not yet reviewed by the nation{"s" if kind == "peoples" else ""} or the Library&rsquo;s historians</p>
{paras}
<details><summary class="caption">Sources</summary><ul class="caption">{srcs}</ul></details>"""

def cession_block(n):
    cs = n.get("cessions") or []
    if not cs:
        return ""
    rows = "".join(
        f'<li><b>{e((c.get("date") or "")[:4] or "Date unknown")}</b> Royce cession {e(c["cession"])}'
        f'<span class="caption"> &middot; Named in the 1899 record: {e(c.get("royce_tribes") or "")}'
        + (f' &middot; <a href="{e(c["treaty_url"])}" rel="noopener" target="_blank">Treaty or act</a>' if c.get("treaty_url") else "")
        + (f' &middot; <a href="{e(c["royce_url"])}" rel="noopener" target="_blank">Royce schedule</a>' if c.get("royce_url") else "")
        + "</span></li>" for c in cs)
    years = sorted({c["date"][:4] for c in cs if c.get("date")})
    span = f" between {years[0]} and {years[-1]}" if len(years) > 1 else ""
    return f"""<h2>Lands ceded by treaty</h2>
<p>The U.S. Forest Service links {len(cs)} land cession{"s" if len(cs) != 1 else ""}{span} to this nation, drawn from Charles Royce&rsquo;s 1899 maps of lands the United States recorded as ceded. Many cessions were made under pressure or by people who did not speak for every band, and nations may tell this history differently. The nation&rsquo;s own account governs here.</p>
<details><summary class="caption">See the cessions, with links to each treaty</summary><ol class="timeline">{rows}</ol>
<p class="caption">Source: USDA Forest Service, <a href="https://catalog.data.gov/dataset/tribal-lands-ceded-to-the-united-states-feature-layer" rel="noopener">Tribal Lands Ceded to the United States</a> (CC BY 4.0). The Forest Service notes these links to present-day nations are being re-evaluated. Turn on &ldquo;Treaty cessions&rdquo; on the <a href="/map.html">map</a> to see the areas.</p></details>"""


def land_block(n):
    f = HIST / "land" / f"{n['id']}.json"
    h = json.loads(f.read_text()) if f.exists() else None
    if h and h.get("hold"):
        h = None
    if not h and not n.get("areas"):
        return ""
    out = ['<h2>The land</h2>']
    if h:
        out.append('<p class="label" style="color:var(--night)">Draft &middot; not yet reviewed by the nation or the Library&rsquo;s historians</p>')
        out += [f"<p>{e(par)}</p>" for par in h["land_summary"].split("\n\n")]
        if h.get("homelands"):
            out.append(f'<h3 style="margin-top:20px">Homelands, in the nation&rsquo;s words</h3><p>{e(h["homelands"])}</p>')
        if h.get("sacred_places") and h.get("sacred_places_approved"):
            out.append('<h3 style="margin-top:20px">Places the nation holds sacred</h3><ul class="linklist">' + "".join(
                f'<li>{e(sp["name"])}<span class="caption">{e(sp.get("note", ""))} <a href="{e(sp["nation_source_url"])}" rel="noopener" target="_blank">The nation&rsquo;s words</a></span></li>' for sp in h["sacred_places"]) + "</ul>"
                + '<p class="caption">Treat these places as the nation asks. Follow its guidance before visiting any of them.</p>')
        if h.get("nation_boundary_statement"):
            b = h["nation_boundary_statement"]
            out.append(f'<p><a href="{e(b["url"])}" rel="noopener" target="_blank">{e(b.get("label") or "The nation&rsquo;s own map and boundary description")}</a></p>')
        if h.get("disputed"):
            out.append('<p class="empty">The nation describes its boundaries differently from the federal record. Its own description governs here.</p>')
        if h.get("timeline"):
            out.append('<ol class="timeline">' + "".join(f'<li><b>{e(t["year"])}</b> {e(t["event"])}</li>' for t in h["timeline"]) + "</ol>")
        srcs = "".join(f'<li><a href="{e(x["url"])}" rel="noopener">{e(x["name"])}</a></li>' for x in h.get("sources", []))
        out.append(f'<details><summary class="caption">Sources</summary><ul class="caption">{srcs}</ul></details>')
    return "\n".join(out)

def filters_html():
    states = sorted({s for n in nations for s in n["states"]}, key=lambda s: STATE_NAMES.get(s, s))
    regions = sorted({n["bia_region"] for n in nations if n["bia_region"]})
    st = "".join(f'<option value="{s}">{e(STATE_NAMES.get(s, s))}</option>' for s in states)
    rg = "".join(f'<option value="{e(r)}">{e(r)}</option>' for r in regions)
    al = "".join(f'<option value="{k}">{e(v["name"])}</option>' for k, v in vocab["alliances"].items())
    plist = json.loads((SITE / "api/v1/peoples.json").read_text())
    pp = "".join(f'<option value="{p["id"]}">{"— " if p["parent"] else ""}{e(p["name"])}</option>' for p in sorted(plist, key=lambda p: (pby_root(p, plist), p["parent"] is not None, p["name"])))
    return f"""<form class="controls" id="filters" role="search" onsubmit="return false">
<label><span class="label">Search</span><input type="search" name="q" placeholder="Nation, town or former name" autocomplete="off"></label>
<label><span class="label">State</span><select name="state"><option value="">All states</option>{st}</select></label>
<label><span class="label">BIA region</span><select name="region"><option value="">All regions</option>{rg}</select></label>
<label><span class="label">Tourism alliance</span><select name="alliance"><option value="">Any</option>{al}</select></label>
<label><span class="label">People</span><select name="people"><option value="">Any</option>{pp}</select></label>
<label class="check"><input type="checkbox" name="visit" value="1"> Has tourism links</label>
</form>"""


STATE_LINKS = {k: v for k, v in json.loads((ROOT / "data/states.json").read_text()).items() if not k.startswith("_")}

def state_card(n, code):
    hq = n["hq"]["state"] if n["hq"] else None
    others = [STATE_NAMES.get(s, s) for s in n["states"] if s != code]
    note = []
    if not code:
        others = [STATE_NAMES.get(s, s) for s in n["states"]]
        note = [", ".join(others)] if others else []
    elif hq and hq != code: note.append(f"Headquartered in {STATE_NAMES.get(hq, hq)}")
    if code and others: note.append("Also in " + ", ".join(others))
    town = n["nearest_town"] or (n["hq"] or {}).get("city")
    visit = any(l["type"] != "official" for l in n["links"])
    return f"""<article class="card{' has-links' if visit else ''}">
<h3><a href="/nations/{n['id']}/">{e(n['name'])}</a></h3>
<div class="where">{e(town or '')}</div>
{f'<div class="caption">{e(" · ".join(note))}</div>' if note else ''}
{'<div><span class="pill">Tourism links</span></div>' if visit else ''}
<div class="more"><a href="/nations/{n['id']}/">Plan your visit &rsaquo;</a></div></article>"""

def build_states():
    codes = sorted({s for n in nations for s in n["states"]}, key=lambda s: STATE_NAMES.get(s, s))
    api = []
    rows = []
    for code in codes:
        name = STATE_NAMES.get(code, code)
        members = sorted([n for n in nations if code in n["states"]],
                         key=lambda n: (-any(l["type"] != "official" for l in n["links"]), n["name"]))
        based = [n for n in members if n["hq"] and n["hq"]["state"] == code]
        crossing = [n for n in members if len(n["states"]) > 1]
        info = STATE_LINKS.get(code, {})
        partner = ""
        if info.get("links"):
            partner = '<h2>Statewide partners</h2><ul class="linklist">' + "".join(
                f'<li><a href="{e(l["url"])}?utm_source=trlibrary&amp;utm_medium=referral&amp;utm_campaign=nativenations" rel="noopener" target="_blank">{e(l["label"])}</a>'
                f'<span class="caption">{e(vocab["link_types"][l["type"]])} &middot; {e(urllib.parse.urlsplit(l["url"]).netloc.replace("www.", ""))}</span></li>' for l in info["links"]) + "</ul>"
        snippet = e(f'<div data-nativenations="list" data-state="{code}"></div>\n<script src="{BASE}/embed.js" async></script>')
        body = f"""<section class="hero"><div class="wrap">
<div class="crumb"><a href="/states/" style="color:var(--sand)">All states</a></div>
<h1>Native nations in {e(name)}</h1>
<p>{len(members)} federally recognized nation{'s' if len(members) != 1 else ''}{f", {len(crossing)} of them across state lines" if crossing else ""}.</p>
</div></section>
<div class="wrap fact-body">
<div>
<h2>Nations</h2>
<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(260px,1fr))">{"".join(state_card(n, code) for n in members)}</div>
</div>
<aside>
{partner}
<h2>Where</h2>
<div id="statemap" class="minimap" style="height:340px" data-state="{code}" data-areas="{",".join(sorted({a["aiannhce"] for n in members for a in n.get("areas", [])}))}"></div>
<p class="caption">Points mark tribal government headquarters; shaded areas are reservation and trust land (U.S. Census). Neither shows homelands. A nation whose lands cross state lines appears on each state&rsquo;s page.</p>
<p class="caption" style="margin-top:14px">Before you go, read the <a href="{KBYG}" rel="noopener">Know Before You Go guides</a> from the American Indigenous Tourism Association.</p>
<h2>Embed this list</h2>
<div class="snippet">{snippet}</div>
<p class="caption"><a href="/api/v1/states/{code.lower()}.json">JSON</a></p>
</aside></div>
<script src="/assets/map.js" defer></script>"""
        write(f"states/{code.lower()}/index.html", page(f"Native nations in {name}", body,
              desc=f"The {len(members)} federally recognized Native nations in {name}, with links to their own tourism pages.",
              path=f"/states/{code.lower()}/", nav="states", extra_head=LEAFLET))
        rec = {"code": code, "name": name, "count": len(members), "headquartered_here": len(based),
               "cross_state": len(crossing), "alliances": info.get("alliances", []), "links": info.get("links", []),
               "nations": [{"id": n["id"], "name": n["name"], "states": n["states"],
                            "hq_state": n["hq"]["state"] if n["hq"] else None} for n in members]}
        api.append({k: v for k, v in rec.items() if k != "nations"})
        (SITE / "api/v1/states").mkdir(parents=True, exist_ok=True)
        (SITE / "api/v1/states" / f"{code.lower()}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False))
        rows.append(f'<tr><th scope=row><a href="/states/{code.lower()}/">{e(name)}</a></th><td>{len(members)}</td><td>{len(crossing) or ""}</td><td>{"Yes" if info.get("links") else ""}</td></tr>')
    (SITE / "api/v1/states.json").write_text(json.dumps(api, indent=1, ensure_ascii=False))
    write("states/index.html", page("Native nations by state", f"""<section class="hero"><div class="wrap">
<h1>Native nations by state</h1>
<p>Federally recognized nations in {len(codes)} states. A nation whose lands cross state lines is listed in each of its states.</p>
</div></section>
<div class="wrap" style="max-width:820px">
<table class="facts" style="margin-top:28px"><thead><tr><th>State</th><th>Nations</th><th>Across state lines</th><th>Statewide partners</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
</div>""", desc="Find federally recognized Native nations by state, with links to their own tourism pages.", path="/states/", nav="states"))

def build_peoples():
    plist = json.loads((SITE / "api/v1/peoples.json").read_text())
    byid = {n["id"]: n for n in nations}
    pby = {p["id"]: p for p in plist}
    DRAFT = '<p class="empty" style="margin-top:20px">Draft. These groupings are being reviewed with the nations before this page is published. Each nation names itself; follow its links to learn how it tells its own history.</p>'
    for p in plist:
        members = sorted([byid[i] for i in p["nations"]], key=lambda n: (-any(l["type"] != "official" for l in n["links"]), n["name"]))
        kids = [c for c in plist if c["parent"] == p["id"]]
        parent = pby.get(p["parent"]) if p["parent"] else None
        aka = f'<p>Also called {e(", ".join(p["also_called"]))}</p>' if p["also_called"] else ""
        sub = ""
        if kids:
            sub = '<h2>Within the ' + e(p["name"]) + '</h2><ul class="linklist">' + "".join(
                f'<li><a href="/peoples/{c["id"]}/">{e(c["name"])}</a><span class="caption">{len(c["nations"])} nation{"s" if len(c["nations"]) != 1 else ""}</span></li>' for c in kids) + "</ul>"
        states = sorted({s for n in members for s in n["states"]}, key=lambda s: STATE_NAMES.get(s, s))
        body = f"""<section class="hero"><div class="wrap">
<div class="crumb"><a href="/peoples/" style="color:var(--sand)">All peoples</a>{f' &rsaquo; <a href="/peoples/{parent["id"]}/" style="color:var(--sand)">{e(parent["name"])}</a>' if parent else ''}</div>
<h1>{e(p["name"])}</h1>{aka}
<p>{len(members)} federally recognized nation{"s" if len(members) != 1 else ""} today, in {e(", ".join(STATE_NAMES.get(s, s) for s in states))}.</p>
</div></section>
<div class="wrap fact-body"><div>
{DRAFT}
{history_block("peoples", p["id"])}
<h2>Nations today</h2>
<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(260px,1fr))">{"".join(state_card(n, "") for n in members)}</div>
{sub}
{('<h2>Related peoples</h2><p class="caption">Related, but each identifies as its own people.</p><ul class="linklist">' + "".join(f'<li><a href="/peoples/{r}/">{e(pby[r]["name"])}</a></li>' for r in p.get("related", []) if r in pby) + '</ul>') if p.get("related") else ""}
</div><aside>
<h2>Where</h2><div id="peoplemap" class="minimap" style="height:340px" data-ids="{",".join(p["nations"])}" data-areas="{",".join(sorted({a["aiannhce"] for i in p["nations"] for a in byid[i].get("areas", [])}))}"></div>
<p class="caption">Points mark tribal government headquarters today; shaded areas are reservation and trust land (U.S. Census). Neither shows homelands or historic territories. For territories, see <a href="https://native-land.ca/" rel="noopener">Native Land Digital</a>.</p>
<p class="caption"><a href="/api/v1/peoples.json">JSON</a></p>
</aside></div><script src="/assets/map.js" defer></script>"""
        write(f'peoples/{p["id"]}/index.html', page(p["name"], body, desc=f'{p["name"]}: the federally recognized nations today and links to their own tourism pages.',
              path=f'/peoples/{p["id"]}/', nav="peoples", extra_head=LEAFLET))
    def item(p, depth):
        return f'<tr><th scope=row style="padding-left:{depth * 22}px"><a href="/peoples/{p["id"]}/">{e(p["name"])}</a></th><td>{e(", ".join(p["also_called"]))}</td><td>{len(p["nations"])}</td></tr>'
    rows = []
    for p in sorted([x for x in plist if not x["parent"]], key=lambda x: x["name"]):
        rows.append(item(p, 0))
        rows += [item(c, 1) for c in plist if c["parent"] == p["id"]]
    write("peoples/index.html", page("Peoples and nations", f"""<section class="hero"><div class="wrap">
<h1>Peoples and nations</h1><p>Many peoples are made up of several nations today, and some nations bring together more than one people. Pick a people to see its nations.</p></div></section>
<div class="wrap" style="max-width:900px">{DRAFT}
<table class="facts" style="margin-top:20px"><thead><tr><th>People</th><th>Also called</th><th>Nations today</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
<p class="caption" style="margin-top:14px">This list is growing. It starts with the peoples of the Northern Plains and Rocky Mountains.</p></div>""",
        desc="Peoples and the federally recognized nations that belong to them today.", path="/peoples/", nav="peoples"))

def build():
    n_visit = sum(1 for n in nations if any(l["type"] != "official" for l in n["links"]))
    write("index.html", page("Native Nations", f"""<section class="hero"><div class="wrap">
<h1>Plan your visit with Native nations</h1>
<p>{len(nations)} federally recognized nations. Find each one&rsquo;s own website, tourism pages, events and tours, then go straight to the source.</p>
</div></section>
<div class="wrap">{filters_html()}<p class="count" id="count" aria-live="polite"></p><div class="grid" id="results"></div>
<p style="text-align:center;margin:24px 0"><button class="btn ghost" id="more" hidden>Show more</button></p></div>
<script src="/assets/search.js" defer></script>""", desc="Find the websites, tourism pages, events and tours that Native nations publish themselves.", nav="search"))

    write("map.html", page("Map of Native nations", f"""<div class="wrap"><h1 style="margin-top:28px">Map</h1>
{filters_html()}
<div class="legend"><span><i class="dot links"></i>Tourism links added</span><span><i class="dot basic"></i>Federal facts only</span><label class="check" style="padding:0"><input type="checkbox" id="bnd" checked> Reservation and trust land (U.S. Census)</label><label class="check" style="padding:0"><input type="checkbox" id="ces"> Treaty cessions (Royce, 1899)</label><span class="caption">Points mark tribal government headquarters. Boundaries are legal geography, not homelands.</span></div>
<div class="mapwrap"><div id="map" role="region" aria-label="Map of tribal government headquarters"></div></div><p class="count" id="count" aria-live="polite"></p></div>
<script src="/assets/map.js" defer></script>""", desc="Map of federally recognized Native nations with links to their tourism resources.", path="/map.html", nav="map", extra_head=LEAFLET))

    for n in nations:
        write(f'nations/{n["id"]}/index.html', fact_page(n))

    write("widgets/card.html", page("Native nation card", '<div id="w" data-widget="card"></div>', widget=True))
    write("widgets/list.html", page("Native nations list", '<div id="w" data-widget="list"></div>', widget=True))
    write("widgets/map.html", page("Native nations map", '<div id="w" data-widget="map"><div id="map" style="height:var(--h,480px);min-height:300px"></div></div>', widget=True, extra_head=LEAFLET))

    write("embed.html", page("Embed and API", f"""<div class="wrap" style="padding-bottom:20px"><h1 style="margin-top:28px">Embed &amp; API</h1>
<p>Put Native Nations on any website. Pick a widget and filters, then copy the code. Widgets size themselves to fit.</p>
<form class="controls" id="builder" onsubmit="return false" style="grid-template-columns:1fr 1fr 1fr 1fr 1fr">
<label><span class="label">Widget</span><select name="type"><option value="list">List</option><option value="map">Map</option><option value="card">Single nation card</option></select></label>
<label><span class="label">State</span><select name="state"><option value="">All states</option>{"".join(f'<option value="{s}"{" selected" if s == "ND" else ""}>{e(STATE_NAMES.get(s, s))}</option>' for s in sorted({s for n in nations for s in n["states"]}, key=lambda s: STATE_NAMES.get(s, s)))}</select></label>
<label><span class="label">Tourism alliance</span><select name="alliance"><option value="">Any</option>{"".join(f'<option value="{k}">{e(v["name"])}</option>' for k, v in vocab["alliances"].items())}</select></label>
<label class="check"><input type="checkbox" name="filters" value="1" checked> Search box</label>
<label><span class="label">Rows (list)</span><select name="limit"><option value="12">12</option><option value="24">24</option><option value="">All</option></select></label>
<label><span class="label">Nation (card)</span><select name="id"><option value="">Choose a nation</option>{"".join(f'<option value="{n["id"]}">{e(n["name"])}</option>' for n in sorted(nations, key=lambda n: n["name"]))}</select></label>
</form>
<div class="snippet" id="code"></div><p><button class="btn" id="copy">Copy code</button></p>
<h2>Preview</h2><div id="preview"></div>
<h2>Options</h2>
<table class="facts">
<tr><th>data-nativenations</th><td><code>list</code>, <code>map</code> or <code>card</code></td></tr>
<tr><th>data-id</th><td>Nation id (card). Find it in the nation&rsquo;s page address.</td></tr>
<tr><th>data-state</th><td>Two-letter state code, comma-separated for several (list, map)</td></tr>
<tr><th>data-alliance</th><td><code>ndnta</code>, <code>sdnta</code> (list, map)</td></tr>
<tr><th>data-visit</th><td><code>1</code> to show only nations with tourism links</td></tr>
<tr><th>data-limit</th><td>Maximum rows (list). Without filters, lists show 24 unless you set this.</td></tr>
<tr><th>data-height</th><td>Map height in pixels (map)</td></tr>
<tr><th>data-cessions</th><td><code>1</code> draws treaty cession areas (Royce, 1899, via the USDA Forest Service) on a map widget</td></tr>
<tr><th>data-boundaries</th><td><code>1</code> draws reservation and trust land boundaries on a map widget</td></tr>
<tr><th>data-filters</th><td><code>1</code> adds a search box and state filter to a list</td></tr>
<tr><th>data-people</th><td>People id, e.g. <code>lakota</code> (list, map)</td></tr>
<tr><th>data-name</th><td>Name a widget when a page has more than one, so each gets its own address parameters</td></tr>
<tr><th>data-deeplink</th><td><code>off</code> to stop the widget reading and updating your page&rsquo;s address</td></tr>
</table>
<h2>Deep links</h2>
<p>Widgets read <code>nn-</code> settings from the address of the page they sit on, and update it as people search or open a nation. That means any view can be bookmarked or shared from your own site:</p>
<div class="snippet">https://your-site.org/plan-your-trip?nn-state=SD&amp;nn-q=lakota
https://your-site.org/plan-your-trip?nn-nation=oglala-sioux-tribe
https://your-site.org/plan-your-trip?nn-people=dakota&amp;nn-visit=1</div>
<p class="caption">Any option above works with the <code>nn-</code> prefix: <code>nn-state</code>, <code>nn-q</code>, <code>nn-people</code>, <code>nn-alliance</code>, <code>nn-region</code>, <code>nn-visit</code>, <code>nn-nation</code>. With named widgets use <code>nn-{{name}}-state</code>. The back button works.</p>
<h2>JSON API</h2>
<table class="facts">
<tr><th><a href="/api/v1/index.json">/api/v1/index.json</a></th><td>Compact list of every nation, for search and maps</td></tr>
<tr><th><a href="/api/v1/nations.json">/api/v1/nations.json</a></th><td>Full records</td></tr>
<tr><th>/api/v1/nations/{{id}}.json</th><td>One nation</td></tr>
<tr><th><a href="/api/v1/nations.geojson">/api/v1/nations.geojson</a></th><td>Headquarters points</td></tr>
<tr><th><a href="/api/v1/boundaries/overview.geojson">/api/v1/boundaries/overview.geojson</a></th><td>All matched reservation and trust land areas, simplified (U.S. Census TIGER/Line 2026)</td></tr>
<tr><th><a href="/api/v1/cessions.geojson">/api/v1/cessions.geojson</a></th><td>Treaty cession areas from Royce&rsquo;s 1899 maps, digitized by the USDA Forest Service (CC BY 4.0); not legal boundaries or homelands</td></tr>
<tr><th>/api/v1/boundaries/{{aiannhce}}.geojson</th><td>One area in more detail; codes are listed on each nation&rsquo;s <code>areas</code></td></tr>
<tr><th><a href="/api/v1/vocab.json">/api/v1/vocab.json</a></th><td>Link types, tags, alliances</td></tr>
<tr><th><a href="/api/v1/meta.json">/api/v1/meta.json</a></th><td>Counts, build date, license</td></tr>
</table>
<p class="caption">Federal facts are public domain. Linked sites and their content belong to their owners; please link to them rather than copying.</p>
</div><script src="/assets/builder.js" defer></script>""", desc="Embed Native Nations widgets and use the JSON API.", path="/embed.html", nav="embed"))

    write("about.html", page("About Native Nations", f"""<div class="wrap" style="max-width:760px;padding-bottom:20px"><h1 style="margin-top:28px">About</h1>
<p>Native nations and their tourism alliances tell their own stories, run their own tours and publish their own event calendars. Native Nations is a front door to that work. It lists every federally recognized nation and sends you straight to the pages each one publishes.</p>
<h2>What you&rsquo;ll find</h2>
<p>For every nation: the name in the federal list, the states it&rsquo;s in, its tribal government headquarters and its official website. Where a nation or its tourism alliance has them, links to tourism pages, cultural centers, events, powwows and tours.</p>
<h2>What you won&rsquo;t</h2>
<p>Descriptions, photos or event listings copied from other sites. Sacred or ceremonial places. Homeland boundaries or migration routes; for territories, see <a href="https://native-land.ca/">Native Land Digital</a>.</p>
<h2>How listings are kept right</h2>
<p>Federal facts are refreshed from the Federal Register and the Bureau of Indian Affairs. Tourism links are confirmed with each nation or its tourism alliance before a listing leaves draft, and links are checked on a schedule. Any nation can ask for a change or for its listing to be removed, and the Library will make it.</p>
<p>Every link out carries a tag so partners can see how many people the Library sends their way.</p>
<h2>Start here</h2>
<p>The first listings are being built with the <a href="https://www.ndnta.com/">North Dakota Native Tourism Alliance</a> and North Dakota&rsquo;s five nations.</p>
<p><a href="{REPO}/issues/new">Suggest a change</a></p>
</div>""", desc="How Native Nations works and where its information comes from.", path="/about.html", nav="about"))

    build_states()
    build_peoples()

    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: " + BASE + "/sitemap.xml\n" if PUBLIC else "User-agent: *\nDisallow: /\n")
    today = datetime.date.today().isoformat()
    urls = ["/", "/states/", "/peoples/", "/map.html", "/embed.html", "/about.html"] + [f"/states/{s.lower()}/" for s in sorted({s for n in nations for s in n["states"]})] + [f'/nations/{n["id"]}/' for n in nations]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"<url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    print(f"built site: {len(nations)} fact pages ({n_visit} with tourism links)")

build()
