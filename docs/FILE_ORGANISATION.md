# Repository organisation

| Path | Purpose |
|---|---|
| `api/` | Flask routes, services, persistence models and PayPal integration |
| `frontend/` | Same-origin browser application and styles |
| `model/` | Current model training/inference and preserved legacy trainer |
| `data/synthetic_training.csv` | Synthetic labelled data used by the current classifier |
| `data/legacy_merchant_dataset.csv` | Original seven-row GHCI merchant dataset, preserved for historical reproducibility |
| `data/taxonomy.json` | Preserved category and merchant-keyword reference |
| `data/archive/legacy_feedback.csv` | Empty historical feedback placeholder; not used by current feedback flow |
| `utils/` | Shared helpers and taxonomy loader |
| `scripts/`, `migrations/` | Local operations and database schema setup |
| `tests/` | Automated tests and synthetic fixtures |
| `docs/` | Product, architecture, security, setup and historical documentation |
| `docs/original-project/` | Original GHCI 2025 PDF artefacts |
| `docs/assets/original-diagrams/` | Original architecture and pipeline diagrams |
| `docs/specifications/` | Archived requirements, design and task records |
| `tools/` | Optional Figma construction and local QA utilities |
| `reports/` | QA evidence, screenshots and completion reports |
| `submission/` | Devpost copy and demo-video preparation |

Only repository metadata, configuration templates, runtime entry points and dependency manifests remain at the root. The current classifier reads `data/synthetic_training.csv`; legacy inputs are retained separately and are not mixed into the current training pipeline. Original assets are preserved with attribution. QA inputs are synthetic and live under `tests/fixtures/`. Figma and QA utilities are separated from runtime code. Temporary browser drivers, scratch workspaces, databases, credentials and generated exports must not be committed.
