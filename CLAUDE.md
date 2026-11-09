# Native Nations — working notes for Claude

A link-out directory of federally recognized Native nations and the tourism and visitation resources they publish themselves. Served as a static site + JSON API at nativenations.labs.trlibrary.com (GitHub Pages, built by `.github/workflows/pages.yml`).

## Non-negotiables
- **Link out, don't copy.** Store only short factual metadata (names, places, link URLs, tags). Never copy descriptions, photos, logos, event listings or itineraries from a nation's site, an alliance site, Destination Native America or any other source. The directory's job is to send visitors to them. See `docs/principles.md`.
- **Nations speak for themselves.** A nation's own statement about its name, spelling, people or separateness overrides every other source (federal, state, scholarly, Wikipedia). If a nation says it is distinct, give it its own page and use a "related peoples" link, never a shared grouping.
- **Nations name themselves.** Use the official name from the BIA list plus the self-designation the nation uses on its own site. Never invent or "correct" a name.
- **Homelands and sacred lands only in the nation's own words.** Describe homelands and name sacred places only when the nation itself has published them, linking its source. Never give directions or coordinates to a sacred place, never describe ceremonies, never list burial sites. Sacred places stay hidden until reviewers approve them (`sacred_places_approved: true` in the land history file). Never add a place as a visitor attraction unless the nation promotes it to visitors itself.
- **No homeland boundaries or migration routes.** Do not store or draw Native Land Digital data (its API terms forbid storing or redistributing it); link to native-land.ca instead. Do not draw migration lines.
- **Human review.** Any Library-written text and any "homelands" association with a park or place goes through the HistorianPanel human-review step for Indigenous history, and ideally the nation or its tourism alliance approves it. Records carry `review.status`; only `approved` records publish prose.
- **Every fact has a source and a `last_verified` date.**
- **Follow the TRPL style guide** (Brand repo: `plugins/trpl-brand/guide/`). Copy: plain, warm, specific; no museum-speak; nonpartisan; minimal we/our; "the Library" capitalized; "participants," never "visitors/guests/audience," for people at Library programs ("Plan your visit" as a verb is fine; otherwise write to "you"); no "experience" as filler; no unverifiable superlatives; no throat-clearing. Indigenous content and MHA Nation materials route to HistorianPanel for now (a named human reviewer is still to be chosen) before publishing.
- **Visual:** brand tokens in `site/assets/app.css` (Night Sky + Deep Orange + Gray Sky pairing; Deep Orange only on things you can click; text on white only in Dark Gray, Night Sky or Dark Forest). Dharma Gothic all caps for headlines, Georgia as the approved Clearface substitute for body, Frutiger Next for labels and captions; fonts load from brand.labs.trlibrary.com. Logo files come from the Brand repo unaltered.

## Layout
`data/nations/*.json` one record per nation · `data/links/` (reserved) · `data/sources/` federal reference data (public domain) · `pipeline/` fetch, validate, build scripts · `site/` pages and assets (`site/api/` is generated) · `docs/` schema, principles, sources.

## Common tasks
- Refresh federal data: `python pipeline/fetch_fr.py` (Federal Register list) → `python pipeline/fetch_bia.py` (BIA directory, organizational fields only) → `python pipeline/seed_nations.py` (creates/refreshes one record per nation; never touches hand-entered fields). Name mismatches between the two lists go in `data/sources/name_overrides.json`.
- Validate: `python pipeline/validate.py`
- Build: `python pipeline/build_api.py && python pipeline/build_site.py` (HTML pages are generated, not committed). Set `PUBLIC = True` in `build_site.py` only after the pilot is approved; until then every page is noindex and robots.txt blocks crawlers.
- Preview: `python -m http.server -d site 8000`
- Map points are **tribal government headquarters** (BIA), never homelands; say so wherever points appear.
