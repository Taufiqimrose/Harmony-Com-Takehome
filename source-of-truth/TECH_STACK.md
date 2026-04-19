# Tech Stack

## Summary


| Layer          | Choice                    | Notes                                                               |
| -------------- | ------------------------- | ------------------------------------------------------------------- |
| Frontend       | Vite + React + TypeScript | Single-page UI with fast local iteration                            |
| Styling        | Tailwind CSS 4            | Utility-first styling with tokens in CSS                            |
| Icons          | Phosphor                  | Used across the stepper, drop zone, and status panels               |
| Backend        | FastAPI + Python          | Simple API + SSE + PDF pipeline                                     |
| HTTP client    | httpx                     | Used for external API calls                                         |
| Extraction     | LandingAI ADE             | Parse: **DPT-2** (`dpt-2`, overridable via `LANDINGAI_PARSE_MODEL`) |
| Verification   | Local (ADE + rules)      | Composite scores in `verify.py`; no external verify API              |
| PDF fill       | pypdf + PyMuPDF           | AcroForm fill when present; stub PDF otherwise                      |
| Web tooling    | Biome + TypeScript build  | Formatting, linting, and compile checks                             |
| Python tooling | ruff + mypy               | Linting and static typing                                           |


## Why this stack fits the project

- The app is a single flow, so a Vite SPA is enough.
- FastAPI keeps the backend straightforward for uploads, SSE, and file responses.
- LandingAI is used for the title extraction stage (ADE **parse** with DPT-2 by default, then schema **extract**).
- PDF work stays deterministic and code-driven.
- The whole system is easy to run locally without extra infrastructure.

## Versions (verified April 2026)

### Runtime


| Runtime | Version          | Source                 |
| ------- | ---------------- | ---------------------- |
| Node.js | 24 (Krypton LTS) | `package.json` engines |
| Python  | 3.13+            | `pyproject.toml`       |


### Frontend (`apps/web/package.json`)


| Package                 | Version   |
| ----------------------- | --------- |
| `react`, `react-dom`    | `19.2.5`  |
| `@types/react`          | `19.2.14` |
| `@types/react-dom`      | `19.2.3`  |
| `@types/node`           | `24.12.2` |
| `typescript`            | `6.0.2`   |
| `vite`                  | `8.0.8`   |
| `@vitejs/plugin-react`  | `6.0.1`   |
| `tailwindcss`           | `4.2.2`   |
| `@tailwindcss/vite`     | `4.2.2`   |
| `@biomejs/biome`        | `2.4.12`  |
| `@phosphor-icons/react` | `2.1.10`  |
| `clsx`                  | `2.1.1`   |
| `tailwind-merge`        | `3.5.0`   |


### Backend (`apps/api/pyproject.toml`)


| Package             | Version      |
| ------------------- | ------------ |
| `fastapi`           | `>=0.136.0`  |
| `uvicorn[standard]` | `>=0.44.0`   |
| `pydantic`          | `>=2.13.2`   |
| `pydantic-settings` | `>=2.13.1`   |
| `httpx`             | `>=0.28.1`   |
| `python-multipart`  | `>=0.0.26`   |
| `pypdf`             | `>=6.10.2`   |
| `pymupdf`           | `>=1.27.2.2` |
| `ruff` (dev)        | `>=0.15.11`  |
| `mypy` (dev)        | `>=1.20.1`   |


### Tooling


| Tool                        | Version    |
| --------------------------- | ---------- |
| `concurrently` (root)       | `^9.2.1`   |
| `astral-sh/ruff-pre-commit` | `v0.15.11` |


## Scaling limitation: bigger model ≠ better extraction

The brief asks for one scaling limitation we'd hit if we tried to improve AI quality solely by increasing model size. For **extraction**, the bottleneck is the **LandingAI parse + extract** calls: latency and cost scale with page complexity and chosen parse model (`LANDINGAI_PARSE_MODEL`, default DPT-2), not with anything in our verify stage. A larger or slower model may not improve field accuracy once the scan is legible; gains come from clearer source PDFs, schema tuning, and human review — not from stacking more parameters on the same raster.

## Verify stage

Verification in `apps/api/src/pipeline/verify.py` is **fully local**: it combines optional ADE per-field confidence with deterministic rule scores (format/length heuristics) into a final 0..1 value and HIGH/MEDIUM/LOW band. There is no second network call for scoring.

## Frontend packages in use

Core packages from `apps/web/package.json`:

- `react`
- `react-dom`
- `vite`
- `typescript`
- `tailwindcss`
- `@tailwindcss/vite`
- `@phosphor-icons/react`
- `clsx`
- `tailwind-merge`
- `@biomejs/biome`

## Backend packages in use

Core packages from `apps/api/pyproject.toml`:

- `fastapi`
- `uvicorn`
- `pydantic`
- `pydantic-settings`
- `httpx`
- `python-multipart`
- `pypdf`
- `pymupdf`
- `ruff`
- `mypy`

## Current operational notes

- Local web runs on `5173`
- Local API runs on `8000`
- State is in-memory
- Output files are written under `apps/api/data/jobs`
- The Windows helper script `dev-install-and-start.bat` is the quickest way to start the project on this machine

## What is intentionally not here

- No database
- No auth layer
- No queue system
- No orchestration framework
- No separate animation library
- No active automated test suite in the current repo flow