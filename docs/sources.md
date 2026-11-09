# Sources

Researched 2026-11-08. "Store" means the data may be kept in this repo; "Link only" means it may not.

## Federal reference data (store, credit the source)

| Source | What it gives | Access | Notes |
|---|---|---|---|
| Federal Register, *Indian Entities Recognized…* (91 FR 4102, 2026-01-30, doc 2026-01899) | Legal names of all 575 recognized tribes, former names in parentheses | https://www.govinfo.gov/content/pkg/FR-2026-01-30/html/2026-01899.htm | Authoritative list. No codes. federalregister.gov blocks bots; use govinfo. |
| BIA Tribal Leaders Directory | Name, alternate name, BIA region/agency, HQ address, city, state, zip, website, lat/lon, NPS/FWS/BLM regions | REST: `https://biamaps.geoplatform.gov/server/rest/services/BOGS/Tribal_Leadership_Directory/FeatureServer/0` · CSV: https://www.bia.gov/tribal-leaders-csv | One row per *leader*, no stable tribe ID: dedupe on `tribefullname`. Longitude field is spelled `longtitude`. **Never publish leader names, emails or phones.** BIA says it is not the official list; pair with the Federal Register. |
| Census TIGER/Line AIANNH (2026 vintage) | Reservation / trust-land / statistical-area names, GEOIDs, internal points | https://www2.census.gov/geo/tiger/TIGER2026/AIANNH/ · TIGERweb `AIANNHA/MapServer` | These are **places, not tribes**. Matching to tribes is manual and many-to-many; mark as reviewed-by-hand. |
| BIA Land Area Representations (LAR) | Polygons, `LARID`, `LARNAME` | `https://biamaps.geoplatform.gov/server/rest/services/DivLTR/BIA_AIAN_National_LAR/FeatureServer/0` | Illustrative only. Optional. |
| NPS Data API | — | — | Has **no** tribe affiliation data. Park "associated tribes" pages exist for some parks with no common URL; enter by hand. |

## Native-led and state tourism sites (link only)

| Site | Deep-link patterns | Terms |
|---|---|---|
| Destination Native America (American Indigenous Tourism Association) | `/tribes/{slug}`, `/listings/{slug}`, `/destinations/{region}`, `/upcoming_events`, `/bookable-tours`, `/pages/know-before-you-go` | "You may not reproduce any site content without written permission." Link only; don't reuse their category labels. ~132 tribes; Spirit Lake, Turtle Mountain and SD tribes not listed (Nov 2026). |
| North Dakota Native Tourism Alliance (ndnta.com) | `/mhanation`, `/turtlemountain`, `/sissetonwahpeton`, `/standingrocksioux`, `/spiritlake`, `/event-list`, `/contact` (tour booking) | None posted. Pilot partner. |
| South Dakota Native Tourism Alliance | `/about/tribal-nations-in-the-alliance/` (links to each nation's own site), `/calendar`, `/hire-a-native-guide/` | None posted. |
| Travel South Dakota | `travelsouthdakota.com/trip-ideas/{tribe-slug}`; *A Guide to Tribal Nations: Oceti Sakowin Homelands* | — |
| Visit Montana | `visitmt.com/indian-country/{slug}` (uses nations' own names, e.g. `niitsitapi-blackfeet`); `/indian-country/respectful-travel-in-indian-country` | — |
| Travel Oregon "Experience Indigenous Oregon" | https://traveloregon.com/places-to-go/tribal-nations/ (links to nations' sites) | https://traveloregon.com/legal/ |
| Native Land Digital | `https://native-land.ca/listings/territories/{slug}` | Data Sovereignty Treaty forbids storing or redistributing API data. Link only; check slugs by hand. |

## Not verified / do not use
- **natow.org now redirects to a gambling spam site. Do not link.** Use the GLITC program page instead.
- visitmita.org (Montana Indigenous Tourism Alliance), TravelOK nation pages, an Arizona American Indian Tourism Association site, Nez Perce Tourism's production domain: unverified.

## State partners (verified 2026-11-08)
Stored in `data/states.json`. Do not use: natow.org (hijacked), aaita.org (parked), natom.org (unrelated server), sioux.org (for sale), crowcreekconnections.org (spam redirect), swc.tc (spam), oglalalakotanation.info (third-party, not the nation's). Open by hand before adding: santeesiouxnation.com. visitmita.org confirmed by Matt 2026-11-08. Wind River Visitors Council is a county lodging-tax board, not tribe-led.

## Treaty cessions (added 2026-11-09)

- **USDA Forest Service, Tribal Lands Ceded to the United States** — Royce's Schedule of Indian Land Cessions maps, georeferenced 2015, revised 2018 (Office of Tribal Relations with Claudio Saunt). 718 mapped cessions pulled from `apps.fs.usda.gov/ArcX/rest/services/EDW/EDW_TribalCessionLands_01/MapServer/0`, simplified to ~0.01°. Data.gov lists CC BY 4.0; credit the Forest Service.
- Stored: `data/cessions/cessions.geojson` (map layer) and `data/cessions/by_nation.json` (Forest Service present-day tribe links matched to our nation ids; ~20 names hand-matched, e.g. the six Minnesota Chippewa bands → Minnesota Chippewa Tribe). Raw pulls in `data/sources/raw/fs_cessions_*.json`.
- Caveats shown on the site: U.S.-recognized cessions, not homelands or legal boundaries; coarse at local scale; the Forest Service is re-evaluating present-day tribe links; the nation's own account governs.
- Unlinked: only groups the Forest Service marks as unrecognized or nonfederally recognized. Skokomish, Coquille and North Fork were hand-linked 2026-11-09.

## Why 573 entries, not 575 (checked 2026-11-09)

The notice's summary says 575 Tribal entities; the printed list has 573 headings (348 in the contiguous 48 states, 225 in Alaska). The gap is in Alaska: four villages appear only as cross-references to two joint governments: Saint Paul Island and St. George Island → Pribilof Islands Aleut Communities of St. Paul & St. George Islands; Arctic Village and Village of Venetie → Native Village of Venetie Tribal Government. Counting each village as its own Tribe gives 573 − 2 + 4 = 575. This is the likely reason; BIA has not been asked to confirm. The directory keeps one page per printed heading, with the villages named on the joint government's page.
