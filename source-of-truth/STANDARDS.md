# Code Standards

One doc covering both sides of the monorepo. Keep it practical and aligned with the current repo.

## Guiding principles

1. **Boring code in clever places.** Architecture can be unusual; individual functions should be obvious.
2. **Fewer layers, not more.** No abstract base classes unless there are ≥3 concrete implementations.
3. **Types are documentation.** Names carry intent; types enforce it.
4. **Colocate.** Hook tests next to hooks, component styles next to components.

---

## Python (`/apps/api`)

### Version and tooling

- Python 3.13+
- `uv` for everything (install, add, lock, run)
- `ruff` (>=0.15.11) for lint + format (no black, no isort, no flake8)
- `mypy --strict` (>=1.20.1) for type checking

### ruff config

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = [
  "E", "F", "W",   # pycodestyle, pyflakes
  "I",             # isort
  "N",             # pep8-naming
  "UP",            # pyupgrade
  "B",             # bugbear
  "SIM",           # simplify
  "TCH",           # type-checking block
  "RUF",           # ruff-specific
  "ASYNC",         # async antipatterns
  "S",             # security
]
ignore = ["S101"]  # allow assert in tests
```

### mypy config

```toml
[tool.mypy]
python_version = "3.13"
strict = true
warn_unreachable = true
disallow_untyped_decorators = false   # FastAPI decorators are loose
plugins = ["pydantic.mypy"]
```

### Naming

- `snake_case` for functions, variables.
- `PascalCase` for classes, Pydantic models, TypedDicts.
- `SCREAMING_SNAKE_CASE` for module-level constants.
- Private helpers: leading underscore.
- Async functions end in a verb: `extract_title` not `title_extractor`.

### Types

- Every function signature has full type hints, including `-> None`.
- Prefer Pydantic v2 models for request/response bodies.
- Prefer dataclasses (with `slots=True`) for internal data carriers.
- `Literal["a", "b"]` for enums of ≤5 values; otherwise `StrEnum`.
- No `Any`. Escape hatch: `object` and narrow.

### Canonical data shapes

These live in `src/pipeline/state.py` and `src/schema/*.py`.

```python
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

# src/schema/extracted.py
@dataclass(slots=True)
class ExtractedField:
    value: str
    bbox: tuple[float, float, float, float]
    ade_confidence: float | None  # None when ADE response has no per-field score

# src/schema/verified.py
@dataclass(slots=True)
class VerifiedField:
    value: str
    bbox: tuple[float, float, float, float]
    ade_confidence: float | None
    rule_confidence: float
    final_confidence: float
    flags: list[str]

# src/schema/buyer.py — HCD field names (G6, F4805, F4766); see file for full list
class BuyerInfo(BaseModel):
    g6_smoke_detector_confirmed: bool = True
    f4805_ro1_last: str = ""
    f4805_current_mailing_street: str = ""
    # ...
    model_config = {"populate_by_name": True, "extra": "ignore"}

class ConfirmBody(BaseModel):
    extracted_overrides: dict[str, str] = Field(default_factory=dict)
    buyer: BuyerInfo

# src/pipeline/state.py
@dataclass
class JobState:
    job_id: str
    status: Literal[
        "ingesting", "extracting", "verifying",
        "awaiting_review", "filling", "complete", "failed",
    ]
    title_path: Path
    title_image_path: Path | None
    extracted: dict[str, ExtractedField] | None
    verified: dict[str, VerifiedField] | None
    extracted_overrides: dict[str, str] | None
    buyer: BuyerInfo | None
    filled_paths: dict[str, Path]
    thumb_paths: dict[str, Path]
    zip_path: Path | None
    created_at: datetime
    event_chunks: list[str] = field(default_factory=list)
    sse_wake: asyncio.Event = field(default_factory=asyncio.Event)
    last_error: str | None = None
```

### Async patterns

- `asyncio.create_task` for fire-and-forget; always hold a reference (`tasks: set[asyncio.Task] = set()`).
- `httpx.AsyncClient` for outbound HTTP, never `requests`.
- Never mix `threading` with `asyncio`. Use `asyncio.to_thread(sync_fn)` for CPU-bound calls.
- Run independent async work in parallel when it makes the flow faster and clearer.

### Imports

Sorted by `ruff` isort. Standard → third-party → first-party. First-party alias is `src`:

```python
from collections.abc import AsyncIterator

from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from src.pipeline.events import emit
from src.schema.verified import VerifiedField
```

### Error handling

- Custom exceptions live in `src/errors.py`.
- Raise `HTTPException` only at route boundaries; business logic raises domain exceptions.
- Log with `logger.exception` inside except blocks, not `logger.error`.
- No bare `except:`. Always `except SpecificError:`.

### Docstrings

- Only on public module functions and route handlers. Private helpers don't need them.
- One-line summary + optional parameter notes. No Google/numpy format.

```python
def fill_packet(verified: dict[str, VerifiedField], buyer: BuyerInfo, out_dir: Path) -> list[Path]:
    """Fill all three HCD forms and return written paths, in form order."""
    ...
```

---

## TypeScript (`/apps/web`)

### Version and tooling

- Node 24 (Krypton LTS), npm
- TypeScript 6.0+ with `strict: true`
- Vite 8 (Rolldown bundler)
- Tailwind CSS 4.2+
- Biome 2.4+ for lint + format (no ESLint, no Prettier)

### Biome config

```json
{
  "$schema": "https://biomejs.dev/schemas/2.4.12/schema.json",
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "suspicious": { "noExplicitAny": "error" },
      "style": {
        "useConst": "error",
        "useTemplate": "warn",
        "noNonNullAssertion": "error"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100
  }
}
```

### tsconfig

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "esnext",
    "strict": true,
    "moduleResolution": "bundler",
    "jsx": "preserve",
    "paths": { "@/*": ["./src/*"] }
  }
}
```

### Naming

- `camelCase` variables, functions, hooks (with `use` prefix).
- `PascalCase` components, types, enums.
- `SCREAMING_SNAKE_CASE` module constants.
- Files: `kebab-case.tsx` for components, `kebab-case.ts` for modules.
- Hook files: `use-job-stream.ts` exports `useJobStream`.

### File layout

```
apps/web/src/
├── main.tsx                # Vite entry
├── App.tsx                 # single-page shell
├── components/
│   ├── terminal.tsx        # the mac-style terminal window
│   ├── terminal-line.tsx   # one SSE event as a line
│   ├── stepper.tsx
│   ├── drop-zone.tsx
│   ├── review-panel.tsx
│   ├── download-panel.tsx
│   └── error-screen.tsx
├── hooks/
│   └── use-job-stream.ts   # SSE subscription
├── lib/
│   ├── api.ts              # fetch wrappers
│   ├── types.ts            # shared UI types
│   └── utils.ts            # cn(), etc
└── styles/
    └── globals.css
```

### Components

- Vite bundles a client-only React app; interactive components use hooks as needed.
- Props type declared inline above component; no separate `Props` file.
- Named exports for components; default export only for `App.tsx` (Vite entry imports it).

```tsx
interface TerminalLineProps {
  event: SseEvent;
}

export function TerminalLine({ event }: TerminalLineProps) {
  return <div className="term-line">...</div>;
}
```

### Hooks

- One hook per file.
- SSE subscriptions always clean up on unmount.
- Return tuples when ≤3 values; return objects when more.

### Styling

- Tailwind 4 utility classes only. No CSS modules, no styled-components.
- `cn()` utility (from shadcn) for conditional classes.
- Custom tokens via `var(--color-primary-600)` syntax.
- Avoid arbitrary values `[]` except for one-offs.
- Terminal body uses `font-mono` class mapped to `--font-family-mono` (JetBrains Mono).

### Errors and async

- Every `fetch` call goes through `lib/api.ts` wrappers. No raw fetch in components.
- SSE errors should surface clearly in the UI and stop invalid downstream actions.

---

## Cross-cutting

### Environment variables

- Python: `.env` read via `pydantic-settings` into a `Settings` class. Never `os.getenv` directly.
- Vite: `VITE_*` for browser-visible (`import.meta.env`). Avoid putting secrets in the web bundle.
- Never commit `.env`. Commit `.env.example` with placeholders.

Required:

```bash
# apps/api/.env
LANDINGAI_API_KEY=
LANDINGAI_PARSE_MODEL=dpt-2
CORS_ORIGIN=http://localhost:5173
# optional — job registry / upload hardening (defaults shown)
JOBS_MAX_COUNT=200
JOB_TTL_SECONDS=86400
UPLOAD_RATE_LIMIT_PER_MINUTE=20
```

```bash
# apps/web/.env.local
VITE_API_URL=http://localhost:8000
```

### Git

- Conventional Commits: `type(scope?): message`.
- Types: `feat`, `fix`, `chore`, `docs`, `style`, `refactor`, `test`, `perf`, `build`.
- Subject line ≤72 chars, imperative mood, no period.
- Body optional but encouraged for nontrivial changes.

Examples:

```
feat(verify): composite ADE + rule scores without external verify API
fix(fill): regenerate radio appearance streams via PyMuPDF fallback
chore: drop framer-motion; CSS-only transitions
docs(architecture): add Verify stage SSE events
```

### File-per-concern

- One React component per file (trivial helper components in the same file are fine).
- One Python class per file is aspirational, not enforced.
- No file over 400 lines without a clear reason.

### No comment shouting

Comments explain *why*, not *what*.

```python
# bad
# iterate over fields
for field in fields: ...

# good
# Pace events 100ms apart server-side so the terminal log reads
# as real-time work rather than a flat dump of 6 lines.
await asyncio.sleep(0.1)
```

---

## Review checklist

Before merging:

1. `just lint` passes.
2. `npm run build --prefix apps/web` passes when frontend behavior changed.
3. API code type-checks and lints cleanly when backend behavior changed.
4. No stray `console.log`, no debug `print()`.
5. No `any`, no bare `except:`.
6. New REST routes or SSE events are reflected in `ARCHITECTURE.md`.
7. New dependencies are reflected in `TECH_STACK.md`.
8. If UX changed, `UX.md` reflects the current screen flow.
