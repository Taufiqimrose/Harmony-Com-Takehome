set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

# Run API and web with npm workspaces (see root package.json `npm run dev`).
dev:
    npm run dev

install:
    npm install
    npm run install:all

lint:
    npm run lint
    python -m ruff check apps/api/src apps/api/tests
    python -m mypy --config-file apps/api/pyproject.toml apps/api/src

test:
    python -m pytest apps/api/tests -q
