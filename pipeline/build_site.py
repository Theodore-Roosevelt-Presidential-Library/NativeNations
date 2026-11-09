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
  <nav class="site-nav" aria-label="Main">{link("/", "Search", "search")}{link("/map.html", "Map", "map")}{link("/embed.html", "Embed &amp; API", "embed")}{link("/about.html", "About", "about")}</nav>
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
    row("State" + ("s" if len(n["states"]) > 1 else ""), e(states_text(n)))
    if n["hq"]: row("Tribal government headquarters", e(f'{n["hq"]["city"]}, {STATE_NAMES.get(n["hq"]["state"], n["hq"]["state"])}'))
    if n["nearest_town"] and (not n["hq"] or n["nearest_town"] != n["hq"]["city"]): row("Nearest town", e(n["nearest_town"]))
    if n["bia_region"]: row("BIA region", e(n["bia_region"]))
    if n["official_website"]:
        u = n["official_website"]; host = urllib.parse.urlsplit(u).netloc.replace("www.", "")
        row("Official website", f'<a href="{e(u)}" rel="noopener">{e(host)}</a>')
    for a in n["alliances"]:
        row("Tourism alliance", f'<a href="{e(a["url"])}" rel="noopener">{e(a["name"])}</a>')
    row("Federal recognition", e(n["fr_citation"]))
    return "\n".join(rows)

def visit_links(n):
    links = [l for l in n["links"] if l["type"] != "official"]
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
        mapblock = f"""<h2>Where</h2><div id="minimap" class="minimap" data-lat="{loc['lat']}" data-lon="{loc['lon']}" data-label="{e(n['name'])}"></div>
<p class="caption">The point marks the tribal government headquarters, not the nation&rsquo;s homelands or reservation boundary. <a href="https://native-land.ca/" rel="noopener">Explore Indigenous territories on Native Land Digital</a>.</p>"""
    snippet = e(f'<div data-nativenations="card" data-id="{n["id"]}"></div>\n<script src="{BASE}/embed.js" async></script>')
    body = f"""<section class="fact-hero"><div class="wrap">
<div class="crumb"><a href="/">All nations</a> &rsaquo; {e(where)}</div>
<h1>{e(n["name"])}</h1>
{f'<p class="legal">{e(n["fr_name"])}</p>' if n["name"] != n["fr_name"] else ''}
{f'<p>{e(n["blurb"])}</p>' if n["blurb"] else ''}
</div></section>
<div class="wrap fact-body">
<div>
<h2>Plan your visit</h2>
{visit_links(n)}
<p class="caption" style="margin-top:14px">Before you go, read the <a href="{KBYG}" rel="noopener">Know Before You Go guides</a> from the American Indigenous Tourism Association. Each nation sets its own rules for photography, ceremonies and permits.</p>
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

def filters_html():
    states = sorted({s for n in nations for s in n["states"]}, key=lambda s: STATE_NAMES.get(s, s))
    regions = sorted({n["bia_region"] for n in nations if n["bia_region"]})
    st = "".join(f'<option value="{s}">{e(STATE_NAMES.get(s, s))}</option>' for s in states)
    rg = "".join(f'<option value="{e(r)}">{e(r)}</option>' for r in regions)
    al = "".join(f'<option value="{k}">{e(v["name"])}</option>' for k, v in vocab["alliances"].items())
    return f"""<form class="controls" id="filters" role="search" onsubmit="return false">
<label><span class="label">Search</span><input type="search" name="q" placeholder="Nation, town or former name" autocomplete="off"></label>
<label><span class="label">State</span><select name="state"><option value="">All states</option>{st}</select></label>
<label><span class="label">BIA region</span><select name="region"><option value="">All regions</option>{rg}</select></label>
<label><span class="label">Tourism alliance</span><select name="alliance"><option value="">Any</option>{al}</select></label>
<label class="check"><input type="checkbox" name="visit" value="1"> Has tourism links</label>
</form>"""

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
<div class="legend"><span><i class="dot links"></i>Tourism links added</span><span><i class="dot basic"></i>Federal facts only</span><span class="caption">Points mark tribal government headquarters, not homelands or reservation boundaries.</span></div>
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
</table>
<h2>JSON API</h2>
<table class="facts">
<tr><th><a href="/api/v1/index.json">/api/v1/index.json</a></th><td>Compact list of every nation, for search and maps</td></tr>
<tr><th><a href="/api/v1/nations.json">/api/v1/nations.json</a></th><td>Full records</td></tr>
<tr><th>/api/v1/nations/{{id}}.json</th><td>One nation</td></tr>
<tr><th><a href="/api/v1/nations.geojson">/api/v1/nations.geojson</a></th><td>Headquarters points</td></tr>
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

    write("robots.txt", "User-agent: *\nAllow: /\nSitemap: " + BASE + "/sitemap.xml\n" if PUBLIC else "User-agent: *\nDisallow: /\n")
    today = datetime.date.today().isoformat()
    urls = ["/", "/map.html", "/embed.html", "/about.html"] + [f'/nations/{n["id"]}/' for n in nations]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"<url><loc>{BASE}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    print(f"built site: {len(nations)} fact pages ({n_visit} with tourism links)")

build()
