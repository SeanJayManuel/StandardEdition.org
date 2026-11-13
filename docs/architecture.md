# Architecture

The product publishes a daily edition. Build-time Python work produces static files; reader settings run locally, with small Cloudflare functions for custom RSS and MCP. Keep expensive ingestion, grouping, and writing out of reader requests.

| Boundary | Responsibility | Main code |
| --- | --- | --- |
| Inputs | Fetch feeds or fictional fixtures, normalize articles and market closes | `inputs.py`, `ingest.py`, `markets.py` |
| Storage | Local SQLite working state, article identity, edition snapshots | `db.py`, `edition.py` |
| Selection | Group articles, distinguish independent reports, score candidates | `cluster.py`, `reposts.py`, `rubric.py` |
| Writing | Generate summaries, validate output, retain verification evidence | `rewrite.py` |
| Publication | Archive complete editions, export HTML/data/feeds | `pipeline.py`, `export_static.py`, `render.py`, `public_api.py` |
| Reader | Settings, selection, routing, and accessible presentation | `web/core.js`, `web/app.js`, `web/index.html`, `web/style.css` |
| Research | Searchable record/story index and historical source context | `research.py`, `web/core.js`, `functions/mcp.js` |
| Edge | Read published data to serve custom feeds and MCP | `functions/` |

Paths in the table are under `boringnews/` unless qualified. [GLOSSARY.md](../GLOSSARY.md) defines the domain vocabulary.

## Contracts worth preserving

- Archive files are the published record and support rebuilding the working database. Schema changes need backward-compatible readers or an explicit version/migration, with restore tests. Preserve historical text and source context; current labels must not silently rewrite past evidence.
- A canonical URL is a link to a source, not necessarily the identity of an event. Successive government actions can share one URL.
- Reader selection is shared between the page and feeds. Python's build-time scoring is intentionally mirrored in JavaScript and protected by parity tests; change both with the ranking document.
- A coverage gap means an observation within the monitored feeds and time window. Unavailable or unmonitored sources are not evidence of absence.
- Verification must distinguish supported, rejected, and unchecked claims. Never infer successful verification from a missing verdict or missing citation.
- HTML and public data are untrusted-content boundaries: escape text, validate links, and avoid introducing HTML sinks for article/model text.
- Fixtures are fictional and deterministic. Test changing external behavior with local stand-ins rather than live provider calls.

## Where to work

For a source or label, start in `sources.yaml` and `docs/labeling.md`. For scoring, start in `rubric.py`, `web/core.js`, and parity tests. For a UI change, read `DESIGN.md`, then the corresponding view and published-page tests. For archive/API changes, inspect both export and restore consumers before editing the schema.

The current directory structure is intentional. Prefer a focused module with a clear data contract over a service split or framework migration. If a change alters these boundaries, document the tradeoff in `docs/decisions/` with the implementation.
