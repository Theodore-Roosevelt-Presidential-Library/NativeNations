# Schema

One JSON file per nation in `data/nations/{id}.json`. Source codes: **F** = federal public-domain data, **L** = entered by the Library, **N** = must be approved by the nation before it publishes.

## Nation

| Field | Type | Src | Notes |
|---|---|---|---|
| `id` | slug | L | Fixed forever, derived from the Federal Register name. Never changes when a name changes. |
| `fr_name` | string | F | Exact Federal Register name. |
| `fr_citation` | string | F | e.g. `91 FR 4102 (2026-01-30)` |
| `fr_former_names` | string[] | F | |
| `display_name` | string | N | The name the nation uses publicly (e.g. "MHA Nation"). Falls back to `fr_name`. |
| `aka` | string[] | N | Self-designations and other names the nation uses. |
| `bia_tld_name` | string | F | `tribefullname` in the Tribal Leaders Directory, used to join. |
| `bia_region`, `bia_agency` | string | F | |
| `states` | string[] | F | USPS codes. |
| `hq` | {city, state, lat, lon} | F | Tribal government office point from the TLD. Not a visitor destination. |
| `nearest_town` | string | L | Visitor-friendly reference town. |
| `census_aiannh` | {geoid, name}[] | L | Matched by hand to TIGER 2026; `approximate`. |
| `official_website` | url | F/L | TLD `website`, checked by hand. |
| `alliances` | enum[] | L | `ndnta`, `sdnta`, `mita`, `aita` … |
| `tags` | enum[] | L→N | From `data/vocab.json` only. |
| `blurb` | string ≤ 160 chars | L→N | One Library-written sentence. Published only when `review.status` is `nation_approved`. |
| `nearby_public_lands` | id[] | L | IDs in the Public Lands Directory (directory.labs.trlibrary.com). Homelands associations need human review. |
| `links` | Link[] | L | See below. Nation-owned links sort first. |
| `review` | {status, by, date, notes} | L/N | `status`: `draft` · `library_reviewed` · `nation_contacted` · `nation_approved` · `nation_declined`. A nation that declines is published with federal facts only, or removed if it asks. |
| `sources` | {name, url, retrieved}[] | L | |
| `last_verified` | date | L | |

## Link

| Field | Type | Notes |
|---|---|---|
| `type` | enum | From `vocab.json` `link_types`. |
| `url` | url | Deepest stable page. UTM tags are added at build time, not stored. |
| `label` | string | Library's own short label. |
| `publisher` | enum | `nation` · `alliance` · `state_tourism` · `aita` · `federal` · `native_land` |
| `nation_approved` | bool | |
| `last_checked`, `http_status` | | Filled by the link checker. |

## Public API (generated)
- `/api/v1/nations.json` — all published nations (federal facts + approved fields only)
- `/api/v1/nations/{id}.json`
- `/api/v1/vocab.json`
- `/api/v1/meta.json` — counts, build date, sources
