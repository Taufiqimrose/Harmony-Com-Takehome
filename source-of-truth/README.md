# Title Transfer Agent

**Demo (local):** `npm install && npm run install:all && pip install -e "apps/api[dev]" && npm run dev` → open [http://localhost:5173](http://localhost:5173), upload the sample title, review, click *Confirm & generate packet*, download `packet.zip`. A pre-generated sample packet (the three filled HCD PDFs from the provided sample title) is included with this submission so the reviewer can inspect output without running the system.

## What it does

This project turns a scanned California manufactured/mobile home title into a reviewable transfer packet.

Current flow:

1. Upload the title PDF
2. Extract title-derived values
3. Score the extracted values
4. Review one form at a time
5. Fill all three HCD PDFs
6. Download the completed packet

## Current product behavior

- Single-page Vite + React frontend
- FastAPI backend with SSE event streaming
- Review screen organized by form, not by raw data group
- Exact PDF wording in manual questions
- Type-specific inputs for text, date, number, and yes/no values
- Deterministic PDF filling with real HCD templates
- Zip download containing the three generated forms

## Forms in the packet

- `476.6G`
- `476.6`
- `480.5`

## Data sources

The packet is built from three sources:

1. Title-derived values extracted from the uploaded PDF
2. Manual answers entered during review
3. Fixed or derived values handled in code

Examples of deterministic values:

- `480.5` total price = base unit + unattached accessories
- `480.5` executed at = `Stockton, CA`
- `480.5` Section 5 values = `No`

## Review experience

The review step is intentionally the center of the product.

- The terminal shows progress up to review
- The review panel replaces the terminal as the primary focus
- Only one form is shown at a time
- The user can move forward and backward across forms
- Labels match the PDF so the reviewer is not translating internal field names

## Running locally

### Prerequisites

- Node 24+ (Krypton LTS)
- Python 3.13+
- `npm`

API keys currently used by the backend:

- `LANDINGAI_API_KEY`

Keep secrets in `apps/api/.env` only (copy from `apps/api/.env.example`). That file is gitignored; rotate keys in the provider dashboards if a real `.env` was ever committed or shared.

### Start the project

```bash
npm install
npm run install:all
pip install -e "apps/api[dev]"
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173).

### Windows shortcut

Run `dev-install-and-start.bat` from the repo root. It installs dependencies, clears ports `5173` and `8000`, and starts both dev servers.

## Tech summary

- frontend: Vite + React + TypeScript
- styling: Tailwind CSS 4
- backend: FastAPI + Python
- extraction: LandingAI ADE
- verification scoring: ADE confidence + deterministic rules (see `verify.py`)
- PDF output: pypdf + PyMuPDF

## Why this stack (with code citations)

- **FastAPI + native SSE over `httpx` instead of an agent framework.** The workflow is a 5-step linear pipeline (`ingest → extract → verify → review → fill`), not a planner/tool-loop. A framework would add ceremony without value here. The end-to-end orchestration lives in one ~~80-line file: `[apps/api/src/pipeline/run.py](apps/api/src/pipeline/run.py)`. User-perceived latency is dominated by the LandingAI parse call (~~5–15s), so the pipeline streams `extract.field` events as they arrive instead of blocking — see the per-field broadcast loop in `[apps/api/src/pipeline/extract.py](apps/api/src/pipeline/extract.py)`.
- **LandingAI ADE for extraction; local verify combines ADE + rules.** ADE returns structured field values with optional per-field confidences against `ExtractSchema`. The verify stage in `[apps/api/src/pipeline/verify.py](apps/api/src/pipeline/verify.py)` merges those with lightweight format heuristics (regex, length) into a single confidence and HIGH/MEDIUM/LOW band — no extra model calls.
- **Deterministic AcroForm fill with `pypdf`, not generated PDFs.** The deliverable is a signature-ready legal packet, so the field-name mapping is hand-curated against the real HCD PDFs in `[apps/api/src/pipeline/form_maps.py](apps/api/src/pipeline/form_maps.py)`, and HCD's inconsistent radio-export states (`/Yes`, `/Y`, `/1`, `/On`, `/Off`…) are normalized in `[apps/api/src/pipeline/fill_acro.py](apps/api/src/pipeline/fill_acro.py)`. Nothing from an LLM is written into the PDF bytes.

## What I'd harden next

1. **Real persistence + multi-worker safety.** The `JOBS` registry in `apps/api/src/pipeline/state.py` is an in-process dict. Move to SQLite (single node) or Postgres + an object store for `data/jobs/`, so `uvicorn --workers N` and restarts don't drop in-flight work.
2. **Sample-title fixture tests.** Commit the provided sample title as a fixture and add a `TestClient` round-trip that uploads it, drains SSE to `awaiting_review`, posts a canned `confirm` body, and asserts the resulting zip contains 3 nonzero PDFs with the expected AcroForm values.
3. **OpenAPI → TypeScript codegen for `BuyerInfo`.** Today `BuyerInfo` (Pydantic) and `BuyerDraft` (TS interface) are maintained in two places and will drift. Wire `openapi-typescript` against FastAPI's schema and regenerate on build.
4. **Deploy target.** Containerize (one Dockerfile per app), push the API to Fly/Render and the SPA to Vercel/Cloudflare Pages. Move blank HCD templates to object storage so the warm-cache step doesn't hit `hcd.ca.gov` from production.
5. **Observability + idempotency.** Add structured logging with a `job_id` correlation field, emit timing metrics for each pipeline stage, and put an idempotency key on `POST /jobs/{id}/confirm` so a double-click can't race the state-machine check.

## Repo map

```text
apps/
├── web/
└── api/
```

Supporting project docs (this folder):

- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`TECH_STACK.md`](TECH_STACK.md)
- [`UX.md`](UX.md)
- [`DESIGN.md`](DESIGN.md)
- [`STANDARDS.md`](STANDARDS.md)
- [`AI_WORKFLOW.md`](AI_WORKFLOW.md)

App-specific:

- [`apps/web/README.md`](apps/web/README.md)
- [`apps/api/README.md`](apps/api/README.md)

