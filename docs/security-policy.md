# Security Policy

## Scope

This repository is a learning project demonstrating security checks in a CI/CD workflow. It is not a production security certification.

## Pipeline gates

- **Tests:** any failing test blocks downstream jobs.
- **Ruff:** configured lint violations block the workflow.
- **Bandit:** medium- and high-severity findings (Bandit `-ll`) block the workflow. Findings must be reviewed, not blindly suppressed.
- **pip-audit:** reported known vulnerabilities in the direct requirements block the workflow. Upgrade affected dependencies or document a time-bounded, reviewed exception.
- **Trivy:** unresolved Critical vulnerabilities in OS or library packages block container scanning. `ignore-unfixed` avoids blocking on vulnerabilities with no available fix; those findings should still be reviewed.
- **SBOM:** the scanned image produces an SPDX SBOM as a workflow artifact.
- **Publishing:** the same image that passed Trivy is published only from a push to `main` after required jobs pass.
- **Signing:** published image digests are signed with Cosign keyless signing using GitHub OIDC.
- **Action supply chain:** third-party GitHub Actions are pinned to reviewed commit SHAs.

These thresholds are project choices, not proof that an image or application is secure. Scanner databases and results change over time.

## Secrets

- Never commit credentials, access tokens, production data, or `.env` files.
- Use GitHub's `GITHUB_TOKEN` with job-scoped permissions for GHCR publishing.
- Do not expose publishing credentials to untrusted pull-request code.
- If a secret is accidentally committed, revoke/rotate it immediately; deleting it from the latest commit is not sufficient.

## Reporting

For a vulnerability in this repository, open a GitHub issue without including exploitable secrets or sensitive information. For a real production incident, use the affected organization's private reporting process.

## Exceptions

Any exception should record the finding, rationale, owner, mitigation, and review date. Do not suppress findings solely to make CI green.
