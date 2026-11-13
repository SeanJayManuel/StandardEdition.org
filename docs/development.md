# Development

## Supported baseline

CI uses Python 3.12 and Node.js 22. Use those versions for reproducing a failure. Other versions may work but are not the supported baseline. The site has no browser runtime npm dependency; Node runs shared RSS logic, tests, and the locked deployment CLI.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.lock
npm ci
npm run check
```

On Windows activate `.venv\Scripts\activate` instead. `npm run check` prefers the repository's virtual environment; set `PYTHON` to select another interpreter. It runs narrow Ruff correctness checks, JavaScript syntax checks, documented-setting validation, and pytest. `npm run lint` runs the faster checks alone. No formatter rewrite is required for unrelated files; match the existing local style and `.editorconfig`.

## Preview without keys

```sh
python -m boringnews.pipeline run --fixtures --mock-llm --date 2026-11-04
BN_SAMPLE=1 python -m uvicorn boringnews.web:app --reload
```

Open `http://localhost:8000`. The fixture edition is invented and must remain labeled as a sample. The first real embedding run can download a model; fixture work does not need it. Preview does not deploy anything.

For the exported artifact:

```sh
python -m boringnews.export_static --out site --sample --static-feed
python -m http.server 8001 --directory site
```

A plain file server cannot execute Cloudflare functions; `--static-feed` intentionally produces only the default RSS feed. Use the local FastAPI preview for custom RSS behavior. Do not mistake a successful static preview for validation of deployed edge functions.

## Configuration

Environment variables are read from the process. `.env` files are ignored by Git but are **not automatically loaded**. Use shell exports or your process manager. Keep secrets out of commands committed to the repo, logs, fixtures, screenshots, and PR descriptions. README lists public configuration names; `npm run lint` checks them against the implementation.

## Dependencies

`requirements.in` lists direct runtime dependencies. `requirements.lock` pins the complete tested runtime environment; `requirements-dev.lock` adds development tools. `requirements.txt` delegates to the runtime lock for existing install instructions. `package-lock.json` pins Node tooling, including Wrangler; deploy using `npm exec --no -- wrangler`, never an unpinned download.

Update dependencies in a focused PR. Resolve in a clean Python 3.12 environment, regenerate exact pins, inspect the diff, run `python -m pip check` and `npm run check`, and verify installation on Linux CI. Keep test tools out of the runtime lock. These are exact-version locks, not artifact-hash verification or a claim that every platform has been tested. For Node use `npm install --save-dev --save-exact PACKAGE@VERSION`, commit both manifests, and run `npm audit`.

## Validation of UI changes

Exercise Today, All stories, settings, a story, Research, and historical pages. Review 320px, 390px, and desktop widths; keyboard focus and Back/Forward; light/dark appearance; long text; no results and failed requests. Check for horizontal page overflow. jsdom tests execute behavior but do not measure layout, contrast, touch, or screen-reader quality. Include real-browser evidence in the PR and name untested states.

Tests use temporary databases and stand-in network services. One writer test binds localhost; sandboxed environments must permit that local socket. No production integration keys are needed.

## Performance regression checks

`npm run check` enforces a 100 KB gzip budget for the fixture homepage, a 400 KB total local-font budget, and deferred research loading. Recipe-name edits must preserve the existing news DOM. Run `python scripts/measure_site.py` for a temporary 365-edition static export; `--days` changes the synthetic history length. This measures artifact size and export time, not network latency or Core Web Vitals. The history repeats fixture content with distinct dates and story IDs; it is not a realistic year of news or a search-quality benchmark. Capture browser performance under a representative mobile connection before launch.

## Publication recovery rehearsal

CI builds two fictional editions, uploads the complete publication, and downloads it on a fresh runner. The recovery job verifies SHA-256 fingerprints, restores a new SQLite database using the saved archives, exports again, and requires every published file to match byte for byte. It has read-only repository permissions and uses no secrets.

To reproduce locally, choose an artifact directory that does not already exist:

```sh
python scripts/rehearse_publication.py build data/rehearsal
python scripts/rehearse_publication.py recover data/rehearsal
```

This validates loss of the working database and transfer of the publication artifact. It does not prove Cloudflare deployment, GitHub archive pushes, provider availability, or rollback on the live domain. The manifest detects accidental corruption; it is not a cryptographic signature from a trusted publisher.
