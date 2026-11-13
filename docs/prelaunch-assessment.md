# Prelaunch assessment — 2026-11-12

## Direction

Keep the static-first Python pipeline and dependency-free browser reader. They fit daily editions, low hosting cost, downloadable evidence, and contributor accessibility. A frontend framework or service split would add migration work without solving the observed problems. Preserve the newspaper identity; make the story and its evidence easier to reach, with advanced controls behind disclosures.

## Implemented in this review

- Mobile lead text comes before the large decorative coverage illustration; settings have explicit all-category behavior and preserve keyboard focus. Advanced source/weight controls and feed syntax are disclosed on demand.
- Summary provenance, checking limits, claim evidence, and coverage-health disclosures distinguish model support, number checks, fallback writing, and invented samples. Only literal quotations from supplied articles are accepted as claim citations.
- Incomplete or malformed model verdicts cannot silently count as verification. Unchecked fallback remains possible and is labeled; model checking is not an independent truth guarantee.
- Government actions retain distinct immutable identities when several actions share a bill URL. Duplicate feed URLs retain one identity. Existing database story links and old archives remain supported.
- Research includes ingested government records even when no summary was written. Historical source labels, monitoring status, failures, and collection windows travel with each edition. Unknown historical monitoring does not imply absent coverage.
- Dated edition and story pages are readable without scripts, have canonical metadata, and survive the rolling research window. Old hash links can resolve through the archive index. The homepage also includes a no-script reading fallback.
- Publication stages one artifact, archives independently of deployment, serializes publication, and supports redeploying a validated prior workflow artifact.
- Fonts are self-hosted with license notices. Editing a recipe name avoids rebuilding the news DOM. Fixture asset budgets and a year-sized export measurement provide repeatable regression signals.
- Contributor, governance, security, architecture, and development guidance, issue/PR templates, pinned dependencies, and one check command establish the open-source contribution path.

## Evidence and limits

The local synthetic 365-day export produced 7,344 files, about 297 MB uncompressed, in 2.9 seconds. The homepage was 53 KB gzip; the story index was 28 KB gzip. Most history volume comes from independently readable static pages. These are local fixture measurements, not deployed performance or real-news quality evidence.

Validation on 2026-11-12: `npm run check` passed all 389 tests, JavaScript syntax checks, Ruff checks, and documented-setting validation. `pip check` found no broken requirements; `git diff --check` passed. The final archive-download route additionally passed all six durable-page tests. Browser review covered 320px, 390px, and 1280px layouts, dark appearance, research search, and script-free story reading, with no horizontal overflow at those widths.

Regression coverage includes database migration, archive restoration, successive government actions, invalid verifier responses, citation provenance, historical feed status, permanent pages, source/feed filtering, API parity, and reader interactions. Real-browser checks supplement jsdom; neither constitutes a full assistive-technology audit.

## Next decisions, in order

1. Run hosted CI and a private production-like publishing rehearsal, including redeploy and partial-failure recovery. Configure the hosting credentials. GitHub private vulnerability reporting has been enabled; the nightly publisher remains disabled until launch.
2. Review several real editions against original reporting. Measure grouping precision, false omissions, verifier failures, token cost, and feed freshness. Publish the results before describing provisional labels or ranking as independently validated.
3. Check mobile loading on the deployed domain and perform a keyboard/screen-reader pass. A synthetic size budget cannot establish LCP, INP, or accessibility conformance.
4. Review source-label evidence and source permissions. Expand center/right coverage only with documented rationale and stable feeds.
5. After that evidence, prioritize coverage quality and corrections over accounts, social features, personalization infrastructure, or a framework migration. State/local expansion and additional delivery channels remain separate roadmap projects.

Live integrations, deployment, external account configuration, human editorial judgment, and the entire long-term roadmap are not completed by these repository changes.
