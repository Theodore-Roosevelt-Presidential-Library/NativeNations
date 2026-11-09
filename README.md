# Native Nations

A link-out directory of federally recognized Native nations and the tourism and visitor resources they publish themselves. Built by the Theodore Roosevelt Presidential Library and published at **https://nativenations.labs.trlibrary.com** (in development).

The directory stores only short facts and links. It sends visitors to each nation, its tourism alliance and Destination Native America rather than copying their content. See [docs/principles.md](docs/principles.md).

| Output | URL |
|---|---|
| Search (state, BIA region, alliance, tourism links) | `/` |
| Map of tribal government headquarters | `/map.html` |
| Fact page for each nation | `/nations/{id}/` |
| Embed builder and API docs | `/embed.html` |
| Widgets (card, list, map) | `/widgets/{card,list,map}.html` via `/embed.js` |
| JSON API | `/api/v1/index.json`, `nations.json`, `nations/{id}.json`, `nations.geojson`, `vocab.json`, `meta.json` |

## Embedding

```html
<div data-nativenations="list" data-state="ND"></div>
<script src="https://nativenations.labs.trlibrary.com/embed.js" async></script>
```

`data-nativenations` = `list | map | card`. Options: `data-id` (card), `data-state`, `data-region`, `data-alliance`, `data-visit="1"`, `data-limit`, `data-height` (map). Widgets resize themselves.

- Data model: [docs/schema.md](docs/schema.md)
- Sources and reuse terms: [docs/sources.md](docs/sources.md)
- Pilot: North Dakota's five nations, with the North Dakota Native Tourism Alliance.

## Running it

```bash
python pipeline/fetch_fr.py && python pipeline/fetch_bia.py && python pipeline/seed_nations.py   # refresh federal facts
python pipeline/validate.py
python pipeline/build_api.py && python pipeline/build_site.py
python -m http.server -d site 8000
```

Brand: follows the TRPL Brand repo (colors, Dharma Gothic / Frutiger Next from brand.labs.trlibrary.com; Georgia substitutes for ITC Clearface on the web).

Federal facts are public domain (Federal Register, BIA, US Census). Linked sites and their content belong to their owners.
