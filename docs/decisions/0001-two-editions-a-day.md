# 0001: Two editions a day

Date: 2026-11-15. Status: accepted.

## Context

The edition was built once a day. Two problems followed:

- A story that broke after the morning run waited a day.
- Some outlets' feeds only reach back a few hours. One fetch a day missed their reports, so a story could look one-sided when it wasn't.

Building twice a day fixes both. But a second run for the same date used to replace the first. Story numbers were handed out again, so a link shared in the morning could point to a different story by evening.

## Decision

The edition is built twice a day, at 11:17 and 21:17 UTC. Both runs build the edition for the same UTC date. The second run updates the first:

- **A published story keeps its number,** and so its link and its feed entry.
- **A story with no new reports isn't written again.** Its text stays exactly as published, and it costs nothing.
- **A story that gained reports is written again,** under the same number.
- **A story the second run would drop stays in the edition.** A published link never disappears.
- **A story the fallback writer wrote is written again** once a model is available.

Stories are matched between runs by the articles they share.

## Alternatives

- **Give each run its own edition** (a morning and an evening edition, each with its own pages). Every published text would stay fixed, but the archive, dated pages, feeds, API and story threads all name an edition by its date. It's a much larger change, and readers would see the same story twice a day.
- **Replace the edition on each run,** as before. Simple, but it breaks links.

## Consequences

- A story's text can change between the two runs, when new reports join it. The morning version stays in the repository's history, because each run commits the edition file to `archive/`.
- An edition file's token totals cover its latest run only.
- If two morning stories turn out to be one event, the evening run writes one merged story and keeps the other morning story as published.
- The second run is scheduled well before midnight UTC, so a late start doesn't fall on the next date.
- Model cost rises by the stories that gain reports, not by a whole second edition.
