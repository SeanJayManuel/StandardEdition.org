# Launch checklist

Use this after the prelaunch PR passes hosted CI. Passing fixture tests alone is not permission to publish invented content as news.

## Current verified setup

- Repository: `SeanJayManuel/StandardEdition.org`; default branch: `main`.
- Tests run on pull requests. A second job downloads a fictional publication on a fresh runner and requires archive recovery to reproduce every published file byte for byte.
- GitHub private vulnerability reporting is enabled.
- The nightly publisher is manually disabled. No repository Actions secrets were configured when checked on 2026-11-12.
- `main` did not have branch protection when checked. Choose protection deliberately: requiring PRs for every write also affects the nightly archive bot, which currently pushes snapshots directly to `main`.

## Before the first real publication

1. Review and merge the prelaunch PR after both `tests` and `recovery` pass on its final commit.
2. Configure the Cloudflare Pages project `standard-edition`, domain routing, and repository Actions secrets through the provider/GitHub settings. The workflow reads `ANTHROPIC_API_KEY`, `CONGRESS_API_KEY`, `FRED_API_KEY`, `CLOUDFLARE_API_TOKEN`, and `CLOUDFLARE_ACCOUNT_ID`. Do not paste credentials into issues, PRs, or chat. Agree on a model-spending limit before running live writing.
3. Build real editions privately and review each summary against its original articles. Record incorrect grouping, unsupported claims, feed freshness, unexplained omissions, and per-edition usage/cost. Use the acceptance criteria in the roadmap; do not replace them with a fixture pass.
4. Validate the candidate on a preview host: custom RSS and MCP, mobile loading, keyboard and screen-reader behavior, source links, dated pages, evidence downloads, and correction display. A plain static file server does not execute edge functions.
5. Rehearse deployment and redeployment on the configured host. `Redeploy a saved edition` takes a prior nightly run ID, verifies its repository/branch/workflow provenance, and deploys the saved artifact without fetching feeds or calling the writer. Artifacts expire after 90 days. The fixture artifact from Tests is intentionally ineligible for production redeployment.
6. Enable and manually run the nightly workflow only when the edition and deployment are ready for readers. Confirm the archive and deploy jobs independently, then confirm the next scheduled edition.

## Recovery checks

- **Deploy fails after build:** keep the saved `publication-RUN_ID` artifact; fix the hosting issue and use the redeploy workflow. Do not regenerate the edition just to retry a deploy.
- **Archive push fails:** recover `archive/` from the same publication artifact, compare it with current `main`, and submit the missing snapshots for review. Preserve the published text and IDs.
- **Runner/database is lost:** restore from archived edition files with `python -m boringnews.archive restore`; do not rerun historical writing.
- **An edition is wrong:** publish a documented correction under the governance policy. For a service-breaking release, choose a known-good publication artifact and verify the domain after redeploying it.

The CI recovery rehearsal covers artifact transfer, integrity, database loss, and deterministic re-export. It does not exercise production credentials, archive pushes, CDN behavior, or a live Cloudflare rollback.
