# Repository organisation

| Path | Purpose |
|---|---|
| `api/` | Flask API, services, persistence models and PayPal integration |
| `frontend/` | Browser application and styles |
| `model/`, `data/`, `utils/` | ML implementation, synthetic training data and original helpers |
| `scripts/`, `migrations/` | Local operations and schema setup |
| `tests/` | Automated tests and synthetic fixtures |
| `docs/` | Product, architecture, security, setup and historical documentation |
| `docs/original-project/` | Original GHCI 2025 PDF artefacts |
| `docs/assets/original-diagrams/` | Original architecture and pipeline diagrams |
| `docs/specifications/` | Archived Phase 0 requirements, design and tasks |
| `tools/` | Optional Figma construction and local QA utilities |
| `reports/` | QA evidence, screenshots and completion reports |
| `submission/` | Devpost copy and demo-video preparation |

Runtime modules remain in stable locations. Original assets are preserved with attribution. QA inputs are synthetic and live under `tests/fixtures/`. Figma and QA utilities are separated from runtime code. Temporary browser drivers, scratch workspaces, databases, credentials and generated exports must not be committed.
