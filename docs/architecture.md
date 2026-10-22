# Architecture

```mermaid
flowchart TD
    A[Push or Pull Request] --> B[GitHub Actions]
    B --> C[Ruff lint]
    B --> D[pytest]
    B --> E[Bandit SAST]
    B --> F[pip-audit]
    C --> G{All Python checks pass?}
    D --> G
    E --> G
    F --> G
    G -- No --> X[Fail workflow]
    G -- Yes --> H[Build Docker image]
    H --> I[Trivy image scan]
    I --> J[Generate SPDX SBOM]
    J --> K{Critical vulnerabilities?}
    K -- Yes --> X
    K -- No --> L{Push to main?}
    L -- No --> M[Checks complete]
    L -- Yes --> N[Publish and Cosign-sign image]
```

## Runtime

- FastAPI provides the REST endpoints.
- SQLite stores tasks in a persistent local database.
- Docker runs the application as a non-root user.
- Docker Compose adds a persistent volume and drops Linux capabilities where supported.

## CI security boundary

Pull requests can run tests and build/scan the image, but only pushes to `main` publish the already-scanned image to GHCR. The container job uses the short-lived `GITHUB_TOKEN` and requests package-write permission only for its publishing steps.
