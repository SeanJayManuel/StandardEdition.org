# Contributing to The Standard Edition

Contributions to code, accessibility, documentation, sources, and editorial rules are welcome. Start with [development](docs/development.md) for a key-free local edition and [architecture](docs/architecture.md) to find the right module.

## Before opening a pull request

1. For a bug, describe the observed behavior and a small reproduction. For a large feature, dependency, architecture change, new coverage area, or editorial policy change, open an issue first so we can agree on scope.
2. Create a branch from current `main`. Keep a pull request focused on one problem; avoid unrelated formatting or generated editions.
3. Add a regression test for changed behavior. Use fictional fixtures and local stand-ins; routine tests must not require provider keys, paid calls, or live news feeds.
4. Run `npm run check` from the repository root after installing the locked development dependencies. Include the command and result in your PR. Explain any check you could not run.
5. Update matching documentation in the same PR. Reader-facing changes must follow `DESIGN.md` and include desktop and narrow-screen screenshots, keyboard behavior, and empty/error states.

## Changes that affect editorial decisions

Source, label, clustering, ranking, and writing changes need a written rationale, examples of before/after behavior, and the corresponding `docs/` or `editorial/` change. A passing test suite does not establish editorial quality.

- Source proposals: link the feed, explain its coverage and role, and report feed health. Never invent a rating or claim permission you have not verified.
- Label proposals: cite the service, rating URL, original label, and date checked. Existing uncited labels are provisional; disagreement is welcome. See [labeling](docs/labeling.md).
- Grouping/ranking: include a representative evaluation corpus or reproducible fixture examples, including incorrect merges and sources that could not be read.
- Writing: preserve attribution and source evidence. Explain how unsupported claims, missing verdicts, and fallback output are handled.

The maintainer makes merge and publication decisions under [governance](docs/governance.md). Contributors are not expected to provide production credentials or deploy their changes.

## Review and conduct

Explain the problem, resulting behavior, validation, and tradeoffs. Respond to review in the PR, and keep disagreement about evidence and implementation, not people. See the [code of conduct](CODE_OF_CONDUCT.md). There is no guaranteed review response time; volunteers may need time to review editorial changes carefully.

Good first contributions include a documented reproduction, a focused regression test, accessibility fixes, unclear copy, and correcting stale setup instructions. Check existing issues before starting duplicate work.

## Security and licensing

Do not put credentials or exploit details in public issues. Use [security reporting](SECURITY.md). Do not commit `.env` files, local databases, model caches, generated sites, or real-person data in fixtures.

By submitting a contribution, you agree to license your contribution under the existing license for the affected files. See [license scope](LICENSES/README.md). Keep third-party attribution and license notices; no CLA is required by this project.
