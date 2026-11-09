# Native Nations

A link-out directory of federally recognized Native nations and the tourism and visitor resources they publish themselves. Built by the Theodore Roosevelt Presidential Library and published at **https://nativenations.labs.trlibrary.com** (in development).

The directory stores only short facts and links. It sends visitors to each nation, its tourism alliance and Destination Native America rather than copying their content. See [docs/principles.md](docs/principles.md).

| Output | URL |
|---|---|
| Directory | `/` |
| JSON API | `/api/v1/nations.json`, `/api/v1/nations/{id}.json`, `/api/v1/vocab.json`, `/api/v1/meta.json` |

- Data model: [docs/schema.md](docs/schema.md)
- Sources and reuse terms: [docs/sources.md](docs/sources.md)
- Pilot: North Dakota's five nations, with the North Dakota Native Tourism Alliance.

## Running it

```bash
python pipeline/fetch_bia.py --apply   # refresh federal fields from the BIA Tribal Leaders Directory
python pipeline/validate.py
python pipeline/build_api.py
python -m http.server -d site 8000
```

Federal facts are public domain (Federal Register, BIA, US Census). Linked sites and their content belong to their owners.
