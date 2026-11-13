# Security policy

The maintained version is the current `main` branch. Older deployments should be updated before investigating a report. The public API and MCP endpoint are intentionally read-only and unauthenticated; that does not make unsafe input handling acceptable.

## Report privately

Use GitHub's [Report a vulnerability](https://github.com/SeanJayManuel/StandardEdition.org/security/advisories/new) flow. Private vulnerability reporting is enabled for this repository.

If that page is unavailable, open a public issue titled “Private security contact requested” without vulnerability details, credentials, affected private URLs, or reproduction payloads. Wait for a private channel from the maintainer before sharing sensitive details. No private mailbox or response-time guarantee is currently published.

A private report should include the affected commit, impact, prerequisites, a minimal reproduction, and suggested mitigation. Use synthetic data and redact secrets. Do not test against other people's systems or disrupt the public site.

The maintainer will coordinate investigation, a fix, and disclosure with the reporter. A leaked credential must be revoked or rotated; deleting it from a file is not sufficient. Corrections to news content belong in the ordinary wrong-story issue form, unless the report contains private information.
