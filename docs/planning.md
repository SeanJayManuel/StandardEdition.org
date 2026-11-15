# Planning notes

The working detail behind the [roadmap](roadmap.md): each item's current state, what's missing, and what counts as done. The roadmap is the short version. This page is for people working on an item.

Last reviewed: 2026-11-15.

Each item has an ID (L5, T3, R1) that issues and pull requests can refer to. IDs aren't reused.

| Status | Meaning |
| --- | --- |
| ✅ | Built |
| 🟡 | Partly built. The item says what's missing |
| ⬜ | Not started |

| Size | Meaning |
| --- | --- |
| S | Under a day |
| M | A few days |
| L | A week or more |

## Decisions

Only the maintainer can make these.

### Open

| # | Decision | Affects |
| --- | --- | --- |
| D1 | **When to turn the scheduled job on.** Agreed in principle on 2026-11-15. It waits on the secrets (L1) | L2 |
| D7 | **How much AI writing is disclosed** on each story, beyond the "written by" field in edition files | T5 |
| D10 | **How to reach readers under censorship.** The goal is set: the same access a US reader has. Still open: which routes to run first (mirrors, Tor, email), and what we can honestly promise about their safety | I5, I6 |
| D11 | **Can anything outside the press and public records affect a story's score?** Recommended: no. Not urgent while X1 is on hold | X1, X2 |
| D12 | **Can the project store email addresses** to send an edition by email? It's the first reader data the project would hold | R9 |
| D13 | **Can a reliability rating sit beside the lean label?** Commercial services show one. Every rating of this kind is contested, and the services' terms need checking | T2 |

### Decided

| # | Date | Decision |
| --- | --- | --- |
| D4 | 2026-11-13 | **Rating services.** Cite AllSides now under its CC BY-NC 4.0 terms, with credit, and email AllSides to confirm a free site counts as non-commercial. Ask Ad Fontes and Media Bias/Fact Check for written permission before citing them |
| D5 | 2026-11-13 | **A failed day.** The last good edition stays up, with a "This edition is out of date" banner |
| D6 | 2026-11-13 | **Spending.** A $10 monthly limit on the Claude API, set in the Anthropic Console |
| D9 | 2026-11-13 | **Outlets.** 14 added, `wsj-world` removed. See T3 |
| D14 | 2026-11-15 | **Editions a day.** Two to begin with, then more if they hold up. See L12 and [the decision record](decisions/0001-two-editions-a-day.md) |
| D15 | 2026-11-15 | **Direction.** A free, open-source alternative to paid coverage-comparison services |
| D16 | 2026-11-15 | **Writing model.** Move to an open-source model once one is shown to write and check as well. See T9 |

The numbers D2, D3 and D8 aren't in use.

## Phase 0: Launch

Goal: a real edition, published on schedule every day, that the maintainer would be happy for a stranger to read.

### L1. Accounts, hosting and secrets 🟡 S

- **Built:** the Cloudflare Pages project, the domain, and the nightly workflow's deploy step. The site is live.
- **Gaps:** four repository secrets aren't set: `ANTHROPIC_API_KEY`, `CONGRESS_API_KEY`, `FRED_API_KEY` and `CLOUDFLARE_API_TOKEN`. `CLOUDFLARE_ACCOUNT_ID` is set (checked 2026-11-15).
- **Needs a person:** create the keys and add them in the repository's Actions secrets. Never paste a key into an issue, a pull request or a chat.
- **Done when:** a manual run of the nightly workflow builds and deploys an edition.

### L2. Safe nightly job 🟡 S

- **Built:** tests run before the build, so failing tests stop a deploy. `pipeline run --require-writer`, used by the nightly job, stops before writing anything when a required key is missing, and stops before storing when every story fell back, which catches a bad key or an outage. Saving the archive and deploying are separate jobs, and a saved edition can be redeployed without rebuilding it.
- **Gaps:** the workflow is disabled on GitHub and has never completed a run (D1). It waits on the secrets (L1). The archive job pushes straight to `main`, so branch protection has to allow for it.
- **Limit:** a partial outage, where only some stories fall back, still publishes. Those stories show their writer in the edition file.
- **Done when:** the workflow is enabled, a manual run succeeds, and the next scheduled run publishes by itself.

### L3. Tests on pull requests ✅ S

- **Built:** `.github/workflows/tests.yml`, on Python 3.12 and Node 22, with read-only permissions and no secrets. A second job rehearses recovering a publication from its archive. Both have passed on real pull requests since 2026-11-13.

### L4. Verify every live source 🟡 S

- **Exists:** `python -m boringnews.pipeline check-feeds`, and tests for the failure paths. Checked live on 2026-11-05: 14 of 16 sources work.
- **Gaps:**
  - `wsj-world` was removed on 2026-11-13: its newest item was from January 2025. Dow Jones's new feed may be for personal use only.
  - CBC News (World) was tried on 2026-11-13 and left off: it closes the connection for our user agent, though it answers browsers.
  - `war-department-releases` returns 403 Access Denied to our requests. It may behave differently from GitHub, which is unknown.
  - Each official source's `max_items` cap is a guess.
- **Done when:** every source reports healthy or is removed, with the reason in the commit.

### L5. Real editions, read by a person 🟡 M

- **Built:** the writer, retries, linter and fact check. The first live edition (2026-11-13) had 22 stories, all written and checked by Claude Haiku 5.5, for about $0.04.
- **Gaps:** one edition isn't a pattern. Still unknown: whether 8,000 tokens is always enough (raised from 2,000 on 2026-11-13, because adaptive thinking counts toward the limit), how often the fallback writer is used, how many bullets the fact check wrongly removes, and what an edition costs with 25 outlets. PR #9 estimated about $0.08.
- **Needs a person:** read each full edition against its sources, and judge it.
- **Done when:** five editions in a row are good enough to publish unedited, and cost per edition is in the ledger.

### L6. Tune grouping and ranking on real news 🟡 M

- **Exists:** grouping by embeddings and shared names, with a word-based fallback (`docs/clustering.md`). Hand-labeled on one day: 0 wrong published groups, down from 4. Edition files record every grouping and the method used.
- **Gaps:** one day has been measured (see the [appendix](#appendix-first-check-on-real-news-2026-11-05)), and it needs a normal news week. Rubric thresholds are uncalibrated: on that day only about 10 stories would be written, and only 1 reached all three sides. This doesn't need a model, so it can run locally.
- **Done when:** a week of real editions is hand-checked for wrongly merged or split stories, the settings are updated, and `docs/clustering.md` and `docs/ranking.md` record the result.

### L7. Market ticker permissions ⬜ S

- **Exists:** the ticker, which is hidden if FRED can't be reached. It shows the latest close FRED has, and a series that lags shows its own date. FRED has no live prices, and the edition is built before markets open, so the newest close is usually the prior trading day's. Decided (2026-11-05): stay with FRED's free closes, not live prices.
- **Gaps:** FRED's S&P 500 and Dow series are copyrighted and say reproduction needs the owner's permission.
- **Needs a person:** check the terms, then keep, replace or remove those series.
- **Done when:** every series on the ticker has been checked.

### L8. Failure handling and alerts 🟡 S

- **Exists:** source and ticker problems are printed in the workflow log.
- **Built (2026-11-05):** Today says when an edition is two or more days old, when feeds couldn't be read and when a story was corrected.
- **Decided (2026-11-13, D5):** on a day the pipeline fails, the last good edition stays up, with a "This edition is out of date" banner above the stories.
- **Gaps:** nobody is told when a run fails or half the sources go quiet. It matters more once the job runs unattended.
- **Done when:** a failed or thin run sends the maintainer an alert.

### L9. Launch legal check 🟡 S

- **Exists:** summaries only, with links out, and a rule against republishing full articles.
- **Gaps:** each outlet's feed terms haven't been read. The README and `LICENSES/` specify documentation licensing and third-party boundaries. The About page has a contact section with public issues, and shows a private address once `BN_CONTACT_EMAIL` is set, but the mailbox is on hold for now, so public issues are the only route.
- **Needs a person:** review the terms, take legal advice if in doubt, and decide when to set up the mailbox.
- **Done when:** each outlet's terms have been checked, and the site has a contact route.

### L10. Launch page basics 🟡 S

- **Exists:** the reader page, RSS, and a local demo.
- **Built (2026-11-05):** a footer, story pages, a favicon, social preview tags, a skip link, focus and page titles that follow each tab, a ticker that holds still on touch screens, notes for failed feeds and old editions, and tested empty states. Checked by keyboard at desktop width, and at 320px, 375px and 1440px wide.
- **Gaps:** nobody has tested it with a real screen reader, no outside reader has tried it, and link previews can't be tested until the site is live.
- **Done when:** a link previews properly when shared, and the page passes a real screen-reader check.

### L11. About page 🟡 S

A new About tab: why this exists, in plain language, for someone who has never heard of it. How it works stays the method. About is the reason, and the people behind it.

- **Built (2026-11-05):** an About us tab with the mission, thesis, principles, funding and an FAQ, using only facts already public in this repo.
- **Exists:** the principles in the README ("What we believe"), the method in How it works, and the ledger.
- **The thesis to state:** gather enough reporting from across the spectrum, and what the sources have in common points toward what's true. The page should also say where this falls short: outlets repeating one wire report count as one source, and every outlet can miss the same thing.
- **Gaps:** the legal form. A private contact address (L9). The FAQ should answer the hard questions directly: Is this written by AI? Who pays for it? Are you biased? Why is this outlet labeled that way? Why was a story left out? How do I challenge a decision? Does this tell me what's true? Some answers depend on D6 and D7.
- **Needs a person:** the words on why it exists. The page names Sean Manuel once, under who runs it, and nowhere else. "Organization, not a company" should only appear once the legal form is settled. A `.org` address doesn't show that by itself.
- **Done when:** the tab is live, every FAQ answer links to its evidence (ledger, source list, code), and an outside reader can explain the project after reading it.

### L12. Two editions a day 🟡 M

- **Built (2026-11-15):** the job is scheduled at 11:17 and 21:17 UTC. The second run updates the first: a published story keeps its number and link, a story with no new reports isn't written again, and a story the second run would drop stays. [The decision record](decisions/0001-two-editions-a-day.md) has the reasoning.
- **Gaps:** it hasn't run on live feeds, because the scheduled job is still off. The page doesn't say when it was last updated. An edition file's token totals cover its latest run only.
- **Done when:** two runs a day publish for a week, and no published story changes its link.

### L13. Put the first edition in the archive ✅ S

- **Built (2026-11-15):** `archive/2026-11-13.json` is the file served on the live site. Restoring from it and exporting gives the same page data as the live site.

---

## Trust: labels and selection

Goal: when someone asks "why is this outlet labeled that?" or "why wasn't this story here?", there's a good, public answer.

### T1. One-sided stories survive to be written 🟡 S to M

The most important gap in the product. The thesis says a story only one side covers is "information in itself", but the pipeline only writes up stories that pass the broad threshold (0.30). With the current source list:

| One-sided story | Score | Written? |
| --- | --- | --- |
| 2 left outlets | 0.27 | No |
| 3 left outlets | 0.30 (0.297) | No |
| 2 right outlets | 0.29 | No |
| 3 right outlets | 0.32 | Yes |
| 2 center outlets | 0.29 to 0.32 | Depends on the pair |

Two things cause this:
- Every left outlet on the list is `national`, so left stories score low on diversity.
- Left outlets count 0.83 each and right outlets 1.11, because the list has four left and three right. That balances each side's total, but it means three left outlets count for less than three right outlets.

So today a three-outlet story on the left is dropped and the same story on the right is kept.

- **Options tested (2026-11-05):**
  - **A, separate blind-spot lane (recommended):** write any story with 2+ rated outlets on one side and keep it out of the main list. Adds 4 stories that day, under a cent a day, and treats all sides alike because it counts outlets, not weights. Needs a third lane in `rubric.py` and `core.js`, and a new rubric version.
  - **B, lower the broad threshold:** 0.28 still drops every left pair. 0.26 is even but by a thin margin, and it changes what "broad" means for everyone.
  - **C, drop weights from the write-up test:** adds nothing that day.
  - **D, balance the list:** adds nothing by itself, and adding outlets can unwrite stories through reweighting.
- **Conditions for A:** word labels as a fact about our list ("Among the outlets we read, only right outlets ran this"), withhold them if any side's feeds failed that day, and fetch more than once a day. Decide what happens if a reader's weights lift one into the main list.
- **Built (2026-11-05, option A, rubric v0.5):** the blind-spot lane, wording as a fact about our list, no claim when a feed on a missing side failed, and a reader setting (`blindspots=0`). With the new grouping, the one tested day has 7 blind spots: 5 left, 2 right.
- **Still open:** fetching more than once a day, so shallow feeds don't make stories look one-sided. Two runs a day (L12) do this once the job is on.
- **Done when:** fetching is fixed, and the labels hold up on a normal week.

### T2. Cited ratings for every outlet ⬜ M

- **Exists:** `ratings` support in `sources.yaml`, the averaging rule in `docs/labeling.md`, and the site showing raters.
- **Gaps:** no outlet has a `ratings` entry. Every label is a hand-set starting assumption.
- **Needs a person:** D4 is decided (AllSides first). Open each AllSides link noted in `sources.yaml` in a browser, confirm the label, then move it into `ratings` with the URL and the date checked. The original 10 outlets need the same check. Add Ad Fontes and Media Bias/Fact Check once they give permission.
- **Done when:** every outlet has cited ratings, and disagreements between raters show on the site.

### T3. A larger, balanced source list 🟡 M

- **Exists (2026-11-13):** 25 outlets: 8 left, 8 center, 7 right, 2 unrated. Types: 17 national, 4 international, 3 regional, 1 wire. Added: Washington Post, Politico, Axios, LA Times (left); UPI, Christian Science Monitor, NewsNation, Reason, The Oregonian (center); Washington Examiner, The Dispatch, National Review, The Center Square (right); DW (center) and France 24 (unrated) as international. Each passed `check-feeds` that day. Leans follow AllSides as reported by search results; each rating page still needs opening in a browser (AllSides refuses automated requests) before it moves into `ratings` (T2). The LA Times has no AllSides page found, so its lean is hand-set. NewsNation and The Hill have the same owner (T7).
- **Shortlist (2026-11-05):** UPI (center wire, a new type), NewsNation (center, both raters agree; check whether its owner also owns The Hill), The Oregonian (center regional). Straight Arrow News is the alternative on coverage gain. All have working feeds. AllSides ratings came from search summaries and need checking before citing, and feed terms aren't confirmed.
- **Balance:** adding only center outlets widens the gap between sides, to left 1.08, center 0.72 and right 1.44 with those three, so pair them with right outlets. The only non-national right option found is The Center Square, rated by AllSides only.
- **WSJ:** the feed moved to `feeds.content.dowjones.io` and works, but Dow Jones's terms may limit RSS to personal use. That needs a yes or no before using it.
- **Ratings:** Ad Fontes labels aren't in `RATING_SCALE`, and its "Middle" spans -5.30 to +5.50, so T2 needs a mapping rule first.
- **Gaps:** the right has 7 outlets against 8 on the left and in the center, and only one wire service is read, because Reuters and AP don't offer public feeds.
- **Next step (2026-11-15):** grow to 100 or more outlets, in batches of 20 to 30. Each batch needs a cited rating for every outlet (T2), a feed check, and a before-and-after comparison like the one in PR #9. Hold a batch if grouping gets worse (L6). Regional outlets come first, because every side is short of them.
- **Limits on growth:** grouping hasn't been checked at this volume, model cost rises with the number of stories, and each outlet's feed terms need reading (L9). Thousands of outlets isn't the aim: a few hundred with cited labels says more than thousands without.
- **Done when:** the list has 100 or more outlets, each side has national, regional and international outlets, every label is cited, and each addition follows the process in `docs/labeling.md`.

### T4. A public way to challenge decisions 🟡 S

- **Exists:** issue forms for proposing a source, challenging a label, reporting a wrong story and suggesting a rubric change, linked from How it works.
- **Gaps:** the `source`, `label`, `correction` and `rubric` labels need creating on GitHub. Filing an issue needs a GitHub account. No written review schedule beyond "quarterly".
- **Done when:** the labels exist and there's a written review schedule, and readers without a GitHub account have a way in. This is the first practical step on the open question about becoming a gatekeeper.

### T5. Checkable summaries 🟡 M

- **Built:** the number check, the model check, a log of removed bullets, and original headlines under each story. Since 2026-11-12, each claim in a summary lists the outlets that support it, with the sentence quoted from each.
- **Gaps:** nothing shows what a summary left out. Decision D7.
- **Done when:** a reader can see what the sources said that the summary didn't. This addresses the open question "summaries are choices too".

### T6. Grouping audit view ⬜ M

- **Exists:** grouping recorded in each edition file.
- **Gaps:** it's only readable as raw JSON. Readers can't see stories that didn't make it, or which articles went unused.
- **Done when:** the site can show everything read that day and what happened to it.

### T7. Independent agreement 🟡 M

The thesis rests on sources agreeing independently, so agreement should only count when the sources are separate.

- **Exists:** a fact is stated plainly when two outlets agree, and the outlets' leans are counted across the spectrum.
- **Built (2026-11-05):** `boringnews/reposts.py` finds articles that repeat another outlet's report. The story page says so, each edition file records it, and the writer is told a repeat isn't a second source.
- **Gaps:** repeats still count toward a story's score, because changing that is a rubric change. Detection only compares headlines and feed snippets, and it hasn't been measured on real wire copy. Outlets with the same owner still count separately: The Hill and NewsNation are both owned by Nexstar. That needs ownership data (T8).
- **Done when:** a fact repeated from one wire report counts as one source in the score, and so do two outlets with one owner.

### T8. Who owns each outlet ⬜ M

Readers of commercial comparison sites can see who owns an outlet. It also fixes a gap here: two outlets with one owner aren't two independent sources (T7).

- **Exists:** nothing. `sources.yaml` has no owner field.
- **Gaps:** an `owner` field for each outlet, with a source and the date checked, as labels have. Wikidata publishes ownership under an open license and is the likely first source, but its entries need checking by hand. Then the Outlets tab and each story page can show the owner, and a story can say when its outlets share one.
- **Rule:** ownership is shown as a fact with its source. It never changes an outlet's lean label.
- **Done when:** every outlet shows its owner and where that came from, and a story says when two of its outlets share an owner.

### T9. Write with an open-source model ⬜ M

Decided on 2026-11-15 (D16): an open-source model fits the project better than a closed one, because readers could then inspect and run every part of the edition.

- **Exists:** summaries and fact checks use Claude Haiku 5.5. The pipeline already accepts any OpenAI-compatible server (`BN_WRITER_URL`, `BN_WRITER_MODEL`), so a local model needs no new code to try.
- **Gaps:** which model, and where it runs. A model has to follow the style guide, return the structured reply, and quote sources accurately for the fact check. The scheduled job runs on GitHub's hosted runners, which have no GPU, so the model needs either a hosted open-model service or a small model that runs on a CPU in reasonable time. Cost goes in the ledger either way.
- **How to compare:** write the same week of editions with both models, and read them against their sources, as in L5.
- **Done when:** an open-source model writes and checks the published edition, and the comparison is published.

---

## Phase 2: Reader control

Goal: "the reader owns the algorithm" is true in practice, not just for four switches.

### R1. Blind-spot page and feed 🟡 M

Stories that one side covered and the others didn't.

- **Built (rubric v0.5):** Today has an "Only one side covered" list. A story with two or more rated outlets on one side and none on the others is written up and kept out of the main list (T1). The wording is a fact about our list, and it's withheld when a missing side's feeds failed. Every story's scale marks a side that ran nothing, and the Outlets tab shows what each outlet skipped.
- **Gaps:** blind spots have no page or feed of their own, and no history, though Research holds 30 days. There's no rule yet for a story one side covered heavily and another barely. More outlets (T3) and a second daily fetch (L12) should come first, so fewer stories look one-sided by accident.
- **Done when:** the rule is published, blind spots have their own page and feed, and a reader can look back over past days.

### R2. Adjustable rubric weights ✅ M

- **Built:** `weights=60,20,10,10` (breadth, coverage, diversity, record), counted as shares of their total, with sliders on Your feed. It works on the page and in feeds.
- **Limit:** weights only re-rank stories that were written, so they can't bring back a story the default rule dropped. The page says so. T1 would widen what readers can reach.

### R3. Feed recipes ✅ S to M

- **Built:** a recipe is a named settings link (`recipe=`), with a copy control and four built-in examples. No accounts, and nothing leaves the browser. Whoever made a link chose its name, and the page says so.
- **Limit:** there's no saved list; saving means bookmarking the link. Opening a recipe replaces the reader's saved settings in that browser, as any settings link does.

### R4. Show what's filtered out ✅ S

- **Built:** Today and All stories list every story a reader's settings hide, grouped by reason.
- **Limit:** this only covers stories that were written. Seeing everything that was read is T6.

### R5. Developing stories ✅ S to M

- **Built:** Day 2+ stories have an "Earlier days of this story" button, which loads the research index on click.
- **Limit:** it reaches back 30 days, older editions have no page of their own, and RSS items don't link to earlier days.

### R7. What each side reported 🟡 M

- **Built (2026-11-05):** when two or more sides covered a story, the writer adds one or two sentences per side, using only that side's outlets. Each is fact-checked against those outlets alone, and the story page shows them above each side's headlines.
- **Gaps:** the real model has never written these, so the sample text is hand-written. Each side adds a fact-check call, so an edition costs more. Few stories will qualify until the source list grows (T3).
- **Rule:** facts and who said them only. No framing comparison, for the same reason we don't highlight words.
- **Done when:** a person has read a week of them against their sources and found them fair.

### R6. Past editions 🟡 M

- **Built (2026-11-12):** every edition has its own dated page, and so does every story. They can be read without scripts, and story links keep working after the 30-day research window.
- **Gaps:** nothing on the page picks a day. A reader has to know the address.
- **Done when:** a reader can open any published day from the site.

### R8. A site that installs like an app ⬜ S

- **Exists:** a static site with its own fonts and no runtime dependencies, which already loads quickly on a phone.
- **Gaps:** a web app manifest and icons, so a phone or desktop can add the site to its home screen, and a small offline cache so the last edition opens without a connection. No push notifications: they're out of scope.
- **Done when:** the site can be installed on iOS, Android and desktop, and the last edition opens offline.

### R9. Email edition ⬜ M

- **Exists:** RSS for any combination of settings, which already works in feed readers and many email tools.
- **Gaps:** sending email means holding readers' addresses. That would be the first reader data the project stores, so it needs decision D12 first. If the answer is yes: sign-up with confirmation, one-click removal, no open or click tracking, a provider whose cost goes in the ledger, and a privacy note in plain language.
- **Needs a person:** D12.
- **Done when:** a reader can get each edition by email and leave with one click, and the site says exactly what's stored.

---

## Phase 3: Federal records

Goal: the claim that records sit next to the reporting holds for all three branches.

### F1. Federal court opinions ⬜ M

- **Exists:** GovInfo as a source type. The README notes it publishes about 250 feeds.
- **Gaps:** which courts to include, given the volume. Courts publish many routine opinions, so `max_items` won't be enough: this needs a rule for what matters.
- **Done when:** opinions appear without flooding the edition, and the selection rule is public.

### F2. Agency reports (GAO and others) ⬜ S to M

- **Gaps:** choosing sources and their record or statement role. Decide whether an audit report is a record.
- **Done when:** the chosen sources run, with roles explained.

### F3. Supreme Court opinions ⬜ M

- **Gaps:** there's no public RSS feed, so this needs another route, and any scraper will be fragile.
- **Done when:** opinions appear on the day they're issued, with a failure alert if the route breaks.

### F4. Roll-call votes ⬜ M

- **Exists:** Congress.gov bills that passed a chamber, went to the President, were signed or vetoed.
- **Gaps:** the README promises votes beside the coverage, but individual roll-call votes aren't read. The Congress.gov API has `/house-vote`, in beta, covering legislation-linked votes in the 118th and 119th Congresses. It has no Senate equivalent, so Senate votes need another source, and showing only one chamber isn't a neutral default.
- **Needs a person:** `CONGRESS_API_KEY`.
- **Done when:** a story about a vote in either chamber links to the vote record itself.

### F5. Presenting official framing ⬜ M

- **Gaps:** the open question of how to show an agency's own framing of a record. Today a record counts as neutral once it's labeled a record.
- **Done when:** a written policy exists in `docs/`, applied in the style guide.

### More from the Congress.gov API

We read only `/bill` today. The [API](https://github.com/LibraryOfCongress/api.congress.gov/) has about 20 areas, allows 5,000 requests an hour, and is free. Everything below needs `CONGRESS_API_KEY`, the same key the bills source needs. Each new source needs the same care as public laws: count real events, not routine record updates.

### F6. Bill summaries from the Congressional Research Service ✅ S to M

- **Built:** a bill the edition keeps now carries its newest summary, labeled with the bill version it describes, so the writer and the fact check have real source material.
- **Limit:** a summary may describe an older version of the bill. A bill with no summary, or a failed call, stays a record with its title and latest action. Not yet tried with a real model.

### F7. Laws from Congress.gov ✅ S

- **Built:** the GovInfo laws source is gone. Congress.gov gives real dates and showed laws GovInfo's feed hadn't posted, and the bills source already catches each signing on its real date.
- **Limit:** an action only counts if Congress.gov shows it within the edition's window. If it posts an action late, that action is missed. Check this over a week in session.

### F8. Nominations ⬜ S to M

- **Gaps:** `/nomination` covers cabinet and judicial nominations. Needs a rule for which actions count, since most nominations are routine.
- **Done when:** significant nominations appear as records, with the rule public.

### F9. Treaties ⬜ S

- **Gaps:** `/treaty` covers treaties sent to the Senate. They're rare, and they stay active across Congresses, so only real events should count, such as a treaty being sent or ratified. Its update date alone isn't an event.
- **Done when:** treaties appear as records on those events only.

### F10. Hearings and committee activity ⬜ M

- **Gaps:** `/hearing`, `/committee-meeting` and `/committee-report` show what's coming up. That could fill the "Next" line with a scheduled date. Needs a rule for matching them to stories.
- **Done when:** a story can cite a scheduled hearing or report as its next step.

### F11. Research reports ⬜ S to M

- **Gaps:** `/crsreport` has nonpartisan background reports, which suit the Research tab more than the edition.
- **Done when:** Research can show relevant reports beside coverage.

---

## Phase 4: State and local

Goal: one place, done properly. The pilot is San Mateo County, California, and nearby cities.

This is the phase with the most unknowns. It should start with a small research spike, S1, before any build.

### S1. Pilot research ⬜ M

- **Gaps:** an inventory of what actually exists: which cities and boards publish agendas, in what format, how reliably, and which local outlets have feeds.
- **Done when:** there's a written list of sources, formats and gaps, and a decision on which cities are in the pilot.

### S2. The place model ⬜ M

- **Exists:** a `states` topic. A `region` field is still stored and guessed, but nothing reads it, and the region setting was removed.
- **Gaps:** there's no concept of where a story belongs or where a reader lives. A reader's place must stay in the browser and feed address, with no accounts. The spotlight, Today page and feeds all assume one national edition.
- **Done when:** a reader can pick a place, and the page and feed follow it.

### S3. State legislature ⬜ M

- **Gaps:** an adapter for California bills and votes, and a rule for which bills matter.
- **Done when:** California bills that pass a chamber appear as records.

### S4. City and board agendas ⬜ L

- **Gaps:** usually PDFs on inconsistent vendor sites, with no feed. Needs document parsing, and a decision on how summaries of agendas meet the fact-check rules.
- **Done when:** the pilot's councils and school boards appear reliably.

### S5. Ranking without a national spectrum ⬜ L

- **Gaps:** the score rewards coverage across left, center and right, and local stories may have one outlet or none. Most local outlets have no published lean rating. Under today's rule, nearly every local story would fail. This needs its own published rule, likely built around records.
- **Done when:** local stories have a rule that's as public and explainable as the national one.

### S6. A guide to add your own city ⬜ M

- **Done when:** someone outside the project adds a city by following it, with a pull request.

### S7. Expansion ⬜ L

- **Gaps:** cost and maintenance grow with every source. Needs per-place failure reporting, and likely volunteer maintainers.
- **Done when:** a second state runs with no new core code.

---

## Phase 5: Open data

Goal: journalists and researchers can use the data without asking.

### O1. Downloads ✅ S

- **Built:** `api/v1/` has an index of editions, one file per edition, and monthly zip downloads. See [`api.md`](api.md).
- **Limit:** no CSV.

### O2. Public API and MCP server 🟡 M

- **Built:** a versioned static JSON API, and a read-only remote MCP server (`functions/mcp.js`) with `get_edition`, `search_coverage`, `search_records` and `list_sources`. No accounts or keys. Documented in [`api.md`](api.md).
- **Deployed:** the API and the MCP server answer on the live domain (checked 2026-11-15).
- **Gaps:** no real MCP client has been tried against it. There's no rate limit, which the MCP spec requires and which needs a Cloudflare rule on the live domain. The free plan's 100,000 daily requests are shared with `/feed.xml`, so heavy MCP use could stop custom feeds.
- **Done when:** a real client works against the live server, and a rate limit is in place.

### O3. Research beyond 30 days ⬜ M

- **Exists:** coverage lookup and records search over the last 30 days, in the browser.
- **Gaps:** the index grows with every day, and all of it is downloaded to the page. Longer history needs a different approach. Word matching also misses paraphrased claims. The MCP function's first search on a fresh copy costs far more than the free plan's 10 ms CPU limit, because it parses and tokenizes the whole index, so it needs a smaller or pre-tokenized index.
- **Done when:** a reader can search the whole archive at a sensible download size.

### O4. Better grouping 🟡 M

- **Exists:** sentence embeddings with a shared-name check and average linkage, with a word-based fallback. `BN_EMBEDDING_SIMILARITY` and `BN_WORD_SIMILARITY` configure the two methods.
- **Tested (2026-11-05):** sentence embeddings with a shared-name check and average linkage, at 0.60, gave no wrong multi-outlet groups and 16 clean ones, against 4 that would publish wrongly and 9 clean today. Embeddings alone are worse, merging by topic. They find about the same number of matches as word matching, so the gain is fewer wrong stories.
- **Cost:** about 110 MB of packages, a 90 MB model to cache in CI, and seconds to run. If that's too much, average linkage on word matching at 0.14 needs no new dependency and separates the Johnson and Jeffries stories, but it leaves wrong multi-outlet groups.
- **Gaps:** 0.60 was picked on one unusual day, so test it on a normal week first. It also won't link stories with no shared name, and same-official-source rules were barely exercised.
- **Done when:** real editions measurably improve, on the week of checks from L6. A wrong merge publishes a false story, so this should come before launch.

---

## Phase 6: Open books

### B1. A true ledger 🟡 S

- **Exists:** `LEDGER.md`, with the domain recorded, and a Ledger page on the site, linked from the footer, that reads the same file, so readers don't need GitHub. Totals are added up from the rows.
- **Gaps:** hosting and API costs appear from L1 and L5 onward. The ledger's rule is to record every transaction within a week.
- **Done when:** the domain, API and hosting costs are listed, and updated as a routine.

### B2. Donations ⬜ M

- **Exists:** the rules in `LEDGER.md`.
- **Gaps:** a payment route with no tracking, and legal and tax questions about taking donations. Depends on real, recurring costs.
- **Needs a person:** the legal and tax decisions.
- **Done when:** a donation appears in the ledger within a week, by a written routine.

---

## Later: Beyond the US

Starts only once US coverage is solid. Each country gets its own spectrum, sources and government feeds rather than inheriting American labels. The work in S5, on ranking without a national spectrum, should inform this.

Goal: anyone, in their own language, can see what each country's outlets and records said, including people whose local news is restricted. Location and language are separate choices: someone in Texas may want the US edition in Spanish, and someone in Toronto may want the Mexico edition in English.

### I1. Location picker ⬜ S to M

A small flag and country code in the corner of the masthead (US, Canada, Mexico) that sets whose news the page follows. The control is designed in `DESIGN.md`, and it stays off the page until the features behind it exist, because a control that does nothing breaks trust. The same goes for the language picker (I2).

- **Exists:** reader settings that travel in the page and feed address, declared in `SETTINGS` in `web/core.js`. A stored `region` field that nothing reads (see S2).
- **Gaps:** an `edition` setting, and a page and feeds that follow it. Depends on S2 and on a second edition existing (I4). Before then, a country that isn't ready can only be shown as planned.
- **Rules:** the choice stays in the browser and feed address, like every other setting. No location detection from the reader's IP address. Flags appear only here, never on the language picker. Blue for left and red for right follow the US convention, so review the scale's colors for each new country.
- **Done when:** a reader can switch editions, and the page, feeds and API follow.

### I2. Interface language ⬜ M

The site's own words: navigation, settings, How it works, Research.

- **Exists:** English only, written directly into `web/index.html` and `web/app.js`. Dates are fixed to `en-US`.
- **Gaps:** a `lang` setting, words moved into per-language files, right-to-left layout for Arabic and Hebrew, and fonts for each script. Blackletter is used only in the logo, which stays the same in every language. The political scale keeps left, center and right in the same order in every language, including right-to-left ones.
- **Needs a person:** which languages come first, and a fluent reader for each.
- **Done when:** the whole site works in one left-to-right and one right-to-left language, chosen in a language's own name (Español, العربية), and the first visit follows the browser's language.

### I3. Translated stories ⬜ L

The day's headlines and summaries in each language. Separate from I2, because this is editorial work and not just interface work.

- **Exists:** English summaries, checked by the banned-word linter and the number and fact checks.
- **Gaps:** the banned-word list and checks are English only, so a translation could bring back loaded language or change a number with nothing to catch it. Translating once at build time keeps it cheap and the same for every reader. Edition files, RSS and the API need to carry each language. Costs go in the ledger (D6), and translated text falls under D7's AI disclosure question.
- **Needs a person:** a loaded-word list and a review by a fluent reader for each language before it launches.
- **Done when:** one language publishes daily with its own checks, and a reader can compare any translated story with the English.

### I4. Editions for other countries ⬜ L each

- **Exists:** nothing outside the US. S5 will show how ranking works without a national left, center and right.
- **Gaps:** for each country, a source list, a spectrum that fits its politics, its government records and a feed audit like L4. Canada and Mexico are the first candidates.
- **Needs a person:** someone who knows each country's media to review the labels.
- **Done when:** one non-US edition passes the same checks as the US edition (L5, L6), read by a person from that country.

### I5. Reach where news is restricted ⬜ M

The goal: a reader under censorship has the same access as a reader in the US. Standard Edition shows who covered what and what the records say, so a reader can get as close to the truth as the evidence allows. It doesn't declare what's true.

- **Exists:** a helpful base. The site is static, needs no account and sets no tracking, and it has RSS, downloadable edition files and a public API.
- **Gaps:** mirrors on other domains, a Tor address, a low-bandwidth page, and email delivery. Blocking one domain shouldn't cut anyone off. Also a written risk review, because reading a blocked site can put a reader in danger, so equal access doesn't mean equal safety.
- **Needs a person:** the open part of D10, and advice from people who work on censorship and reader safety.
- **Done when:** the chosen routes are live, and a plain-language page explains what they do and don't protect against.

### I6. Editions where the press isn't free ⬜ L each

The aggregated view for places like these needs a different method, not just more sources. The US rubric would mislead here.

- **Exists:** nothing. The rubric assumes a free domestic press split across left, center and right, and it gives extra score to government records.
- **Gaps:** in a censored country, most domestic outlets repeat one line, so several of them agreeing proves little, and a score boost for government records would reward the censor. Each edition needs its own groups instead, such as state-aligned, independent, exile and international outlets. Silence means something different too: a story missing from domestic outlets may have been suppressed. Government sources should appear as claims and earn no score.
- **First step:** an outside view of one country, from international and exile outlets alone. It needs no sources inside the country and already gives readers something they can't get locally.
- **Needs a person:** a reviewer who knows that country's media. Their safety matters as much as a reader's.
- **Done when:** one edition runs on its own published rubric, and the rule for government sources is explained on the page.

## Later: Signals beyond the press

The idea: prediction markets get close to the truth by pooling what many people know. These two features test how far that idea can help, without letting attention decide what's news. README principle 7 rules out engagement metrics deciding what you see, so both stay outside the score (D11).

### X1. Social trends ⬜ L (on hold)

On hold as of 2026-11-05, by the maintainer's decision. Nothing here should start until it's lifted.

A separate list of what people are talking about that the outlets we read aren't covering. It's a place to look closer, and never evidence that something is true.

- **Why it needs care:** a market works because people lose money when they're wrong, and it settles on a real outcome. A trend has neither. It rewards attention, and bots and coordinated campaigns can buy it, especially in the censored countries where it would matter most.
- **Why it's still worth doing:** where the press is restricted, people often post what outlets can't print, so a gap between social talk and coverage can be a real signal (I6).
- **Gaps:** a research spike comes first: what each platform allows and costs, and how to spot coordinated activity. Wikipedia page views are a free, harder-to-fake place to start. Bluesky and Mastodon are open. X and Reddit APIs are paid or restricted, and Telegram matters in many restricted countries.
- **Rules:** a labeled list of its own, no effect on any score, topics rather than named private people, more than one platform before anything appears, and an off switch in reader settings.
- **Done when:** the list has run privately for a month, and we've published how often its topics later proved real.

### X2. Prediction market odds ⬜ M

Where a story has an open question ("Will the bill be signed?"), show the market's odds beside it, like the market ticker.

- **Gaps:** which markets, and whether their terms allow it. Thin markets are easy to push around, so each needs a minimum amount of trading before it's shown. Showing odds could look like an endorsement of betting, or of the outcome.
- **Rules:** the odds are always labeled as a market's price, with a link to the market and no effect on any score.
- **Needs a person:** a legal check, and D11.
- **Done when:** odds appear on matching stories with their source and trading volume, and past odds can be checked against what happened.

---

## Appendix: first check on real news (2026-11-05)

One local run on the live feeds, with no model and nothing published. It's a single day just after the midterms, and without a Congress key, so government records are undercounted. Local runs also stored feed times 8 hours late until a bug was fixed afterward, so the window was slightly off. A recount of the one-sided stories with a true 36-hour window matched.

| Measure | Result |
| --- | --- |
| Articles in the 36-hour window | 234 |
| Groups, at similarity 0.15 | 192 |
| Groups with 2 or more outlets | 15 |
| Stories that would be written | 14 before fixing reposted laws, 10 after |
| Stories in the main list at the standard threshold | 9 |
| Stories covered by left, center and right | **1** |

What this showed:

- **Three-sided coverage is rare, partly because of the list.** The WSJ feed had moved, leaving The Hill and the BBC as the only working center outlets (L4, T3). The list had 11 outlets then. The strict setting would show almost nothing.
- **Grouping publishes wrong merges (O4).** A test on 232 hand-labeled articles found 4 groups that would have published a wrong story, including the day's only three-sided story, which merged separate events. Better grouping mostly prevents those. It doesn't find many more matches, so it won't raise three-sided coverage by itself.
- **One-sided stories are being lost (T1).** All six one-lean stories were dropped at the current setting. Four of them had 2 or more rated outlets on one side.
- **Feeds are shallow.** One fetch reached back 1.6 hours for the NY Post and 4.2 for The Hill, against 131 for the Guardian. A once-a-day fetch can make a story look one-sided when it isn't, and it tilts against center and right.
- **Sports reached the edition.** Decided: no sports for now. `docs/ranking.md` has the rule, and each edition file lists what it left out.
- **Reposted laws looked new.** GovInfo reposted old laws with fresh dates, so 2021 laws appeared as today's records, and it was weeks behind on real ones. Fixed by F7.

With the Congress key added, the same check found no bills with a significant action in the window, so records didn't change the result that day. Congress was just past an election, so this needs a week in session to judge. A rerun later that day gave 8 stories rather than 10, because the feeds had moved on, so treat these counts as rough.

## Change log

| Date | Change |
| --- | --- |
| 2026-11-15 | Split into a short [roadmap](roadmap.md) and these notes. Updated statuses after the first live edition. Added L12, L13, T8, T9, R8, R9 and decisions D12 to D16. Open data items renamed from D1 to D4 to O1 to O4, because they clashed with decision numbers |
| 2026-11-13 | 14 outlets added. Decisions D4, D5, D6 and D9 settled |
| 2026-11-12 | Contributor, tooling and grouping descriptions updated for the prelaunch review |
| 2026-11-05 | First version, with the first check on real news |
