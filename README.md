# Secure DevSecOps Pipeline

[![CI and Security](https://github.com/K4ROUI/devsecops-secure-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/K4ROUI/devsecops-secure-pipeline/actions/workflows/ci.yml)

A small FastAPI task API packaged in a hardened Docker image and protected by an automated DevSecOps pipeline. Every change is tested, linted, statically analyzed, audited for dependency vulnerabilities, and checked for critical container vulnerabilities before an image can be published to GHCR.

This repository is intended as a practical reference for securing the path from source code to container image. It is not a production-ready task-management service.

## Features

- FastAPI Task API with SQLite persistence
- Input validation, parameterized SQL statements, and task updates
- pytest unit/API tests
- Coverage enforcement
- Ruff linting
- Bandit Python security analysis
- pip-audit dependency vulnerability checks
- Docker image running as a non-root user
- Trivy image scan with a Critical-severity blocking threshold
- SPDX SBOM generation and keyless Cosign image signing
- GitHub Actions CI on pushes and pull requests
- GHCR publishing from `main` after checks pass
- Weekly dependency/security audit

## Architecture

See [docs/architecture.md](docs/architecture.md) for the Mermaid diagram and security boundary.

## Quick start

### Run with Docker Compose

```bash
docker compose up --build
```

The API is available at:

- API documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

The Compose configuration uses a persistent SQLite volume and applies container hardening including a read-only root filesystem, dropped Linux capabilities, a temporary `/tmp` filesystem, and `no-new-privileges`.

### Run locally with Python

Requires Python 3.12 or later, with Docker optional.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
uvicorn app.main:app --reload
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

The default SQLite database is `data/tasks.db`. Set `DATABASE_PATH` to use another location.

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Return service health |
| `GET` | `/tasks` | List tasks with pagination |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks/{task_id}` | Retrieve a task |
| `PATCH` | `/tasks/{task_id}` | Update a task |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

Create a task:

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Review security pipeline","description":"Run all checks"}'
```

List tasks:

```bash
curl http://127.0.0.1:8000/tasks
```

Update a task:

```bash
curl -X PATCH http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'
```

By default the SQLite database is `data/tasks.db`. Set `DATABASE_PATH` to change the location.

## Verification

Run the same checks used by CI from the repository root:

```bash
ruff check .
pytest --cov=app --cov-report=term-missing --cov-fail-under=85
bandit -c pyproject.toml -r app -ll
pip-audit -r requirements.txt
```

The test suite enforces a minimum coverage of 85%. Dependency findings should be reviewed and resolved by upgrading the pinned versions; security findings should not be suppressed without a documented rationale.

## CI/CD behavior

Workflow file: `.github/workflows/ci.yml`

1. Ruff, pytest, Bandit, and pip-audit run in the Python job.
2. The container job builds one image, scans it with Trivy, generates an SPDX SBOM, and publishes that same scanned image.
3. Trivy blocks the workflow for unresolved Critical findings; unfixed vulnerabilities are ignored by the blocking check but still deserve review.
4. GHCR publication and keyless Cosign signing run only for pushes to `main` and only after all checks succeed.
5. GHCR publication uses `GITHUB_TOKEN` with package-write permission scoped to the container job.
6. Third-party GitHub Actions are pinned to reviewed commit SHAs.

Branch protection should require the CI workflow before pull requests can be merged.

## Project layout

```text
app/                         FastAPI application and SQLite layer
tests/                       API and validation tests
.github/workflows/            CI, container scan, publish and scheduled audit
docs/architecture.md         Mermaid architecture diagram
docs/security-policy.md      Security gates and exception policy
Dockerfile                   Non-root container image
compose.yaml                 Hardened local Compose setup
requirements*.txt             Runtime and development dependencies
pyproject.toml                Ruff, pytest, Bandit configuration
```

## Limitations

- The API is a learning example, not a production-ready service.
- No authentication or per-user authorization is implemented.
- SQLite is suitable for a small demo, not a highly available multi-instance service.
- The pipeline does not perform dynamic application security testing (DAST), SBOM signing, or deployment to a cloud environment.
- The image is signed, but the SBOM is currently generated as a separate workflow artifact rather than signed and attached to the image.
- A clean scan is not proof of security.

## Roadmap

- Add secret scanning and Dependabot.
- Add authentication and authorization tests.
- Add a DAST stage against a disposable test deployment.
- Add a release/tag strategy and image digest tracking.

## Contributing

Changes should include appropriate tests and pass all local verification commands before opening a pull request. Do not commit credentials, production data, or intentionally vulnerable code.

## License

MIT — see [LICENSE](LICENSE).
