# Governance and editorial changes

The Standard Edition is maintained by Sean Manuel. The maintainer decides what merges and what is published, is responsible for correction decisions, and may delegate review explicitly. Open source makes decisions inspectable and contestable; it does not imply that every proposal will be accepted or decided by popularity.

## Decision process

Small implementation fixes can go directly to a pull request. Propose large features, new dependencies, coverage areas, architecture changes, and editorial rule changes in an issue first. Explain the problem, evidence, alternatives, costs, and expected reader effect. Record a substantial accepted architecture choice in `docs/decisions/` before or with its implementation.

Changes to sources, labels, grouping, ranking, or writing rules require a rationale and the corresponding documentation in the same PR. Review must consider inaccurate grouping, repeated wire reports, failed feeds, and effects on minority coverage, not only the number of stories selected. Tests protect implementation behavior; human evaluation remains necessary for editorial quality.

Uncited source labels are provisional. A label proposal should preserve the rating service, URL, observed label, observation date, and mapping to the site's categories. Disagreement is recorded rather than silently erased. Review labels quarterly when operational, recording the actual review date; do not present an intended review cadence as a completed review.

## Corrections and disagreement

Report an incorrect story through the wrong-story issue form. Include the edition, link, disputed text, and evidence. The maintainer determines the correction, records it in `corrections.yaml`, and publishes the correction with the relevant edition. Do not silently change historical claims or manufacture missing evidence.

If a proposal is declined, the maintainer should state the reason and what evidence could change the decision. Ask for reconsideration in the same discussion when there is new evidence. Political disagreement alone is not misconduct. Participants remain free to fork under the published licenses.

## Publication and funding

Only authorized maintainers operate production credentials and publication workflows. Contributions and donations do not buy favorable labels, coverage, or influence over ranking. Spending remains in `LEDGER.md`. Response times are best effort; this project has no guaranteed review or support SLA.
