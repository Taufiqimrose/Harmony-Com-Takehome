# Title Transfer API

FastAPI backend for the title-to-packet workflow.

## Responsibilities

- receive uploaded title PDFs
- stream job progress over SSE
- run extraction and verification scoring
- merge reviewed values
- fill the three HCD forms
- bundle the packet zip for download

## Local setup

From the repo root:

```bash
pip install -e "apps/api[dev]"
```

Or from this directory:

```bash
pip install -e ".[dev]"
```

## Run locally

```bash
uvicorn src.main:app --reload --port 8000
```

## Important folders

- `src/routes/` for API endpoints
- `src/pipeline/` for the job pipeline
- `src/schema/` for request and payload models
- `assets/forms/` for cached HCD templates
- `data/jobs/` for generated job output

