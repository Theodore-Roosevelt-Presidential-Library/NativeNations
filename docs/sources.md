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
