# AI Workflow

The brief asks to *show* the workflow, not just claim AI was used. This file logs the prompts that actually moved the build forward, what the model produced, and what I kept vs. rewrote.

## Tools

- **Cursor** (Composer mode, GPT-5 / Claude Sonnet 4.6) for in-editor edits and multi-file refactors.
- **Claude Code** for one-shot scaffolding and the harder PDF-internals reasoning.
- **LandingAI ADE** as a *runtime* AI dependency (extraction); not part of the build loop.

## How I worked

I treat AI as a **fast first draft + a skeptical pair**, not an oracle. The loop:

1. Write the prompt with concrete I/O examples and the file path I want changed.
2. Read the diff. Reject anything that hallucinates an API or invents a field name.
3. Run it. If it fails, paste the failure back with the offending line numbered.
4. Once green, hand-edit for naming, types, and removing dead branches.

The PDF-fill subsystem (`fill_acro.py`, `form_maps.py`) was ~70% AI-drafted and ~30% hand-rewritten after I opened the actual HCD PDFs in a hex editor and saw the export-state mess. The frontend was ~50/50. The pipeline glue (`run.py`, `events.py`, `state.py`) is mostly hand-written; AI was only used to clean it up.

---

## Representative prompts

### 1. Scaffolding the monorepo

> *"set me up a monorepo with two apps. apps/api is fastapi on python 3.13, give it pyproject.toml ruff mypy strict pydantic v2. apps/web is vite + react 19 + ts strict + tailwind 4 + biome. one `npm run dev` at the root that boots both with concurrently. no docker no db keep it simple"*

**Got:** the directory layout, `pyproject.toml`, `vite.config.ts`, `biome.json`, root `package.json` with `concurrently`. Largely usable.
**Edited:** removed an invented `eslint` config, switched the suggested `python-dotenv` dep to `pydantic-settings`, added `pythonpath = ["."]` to the pytest config so `from src...` imports work without `src/` being a package on sys.path twice.

### 2. LandingAI ADE integration

> *"write extract.py. two landingai calls back to back. first hit POST /v1/ade/parse with the pdf as multipart and a model form field, then POST /v1/ade/extract with the markdown that comes back plus a json schema built from my pydantic model ExtractSchema. use httpx asyncclient, 90s read 20s connect, no retries. return a dict keyed by my field names with ExtractedField values. per field confidence is sometimes missing, when its missing return None not 0.0"*

**Got:** the two-call flow and the `dict[str, dict[str, str]]` schema builder.
**Edited:** the original draft assumed every cell was a string; the real ADE response wraps cells as `{"value": ..., "confidence": ...}` *sometimes*. I wrote `_cell_value_and_confidence` by hand after one debug run printed an unexpected dict shape. Also clamped confidence to `[0, 1]` because LandingAI returned `1.0000000002` once.

### 3. PDF AcroForm field discovery

> *"i have a blank hcd pdf (hcd-rt-480-5.pdf). write me a quick script that just prints every acroform field name in order so i can copy paste them into a python dict. nothing fancy"*

**Got:** the script (now shipped as `python -m src.pipeline.form_maps <pdf>`).
**Edited:** nothing. This is the unsexy boring tool that made the rest of the build tractable. The output of running this against the three blank HCD PDFs **is** `ACRO_FIELD_MAPS`. Every key in that dict was copy-pasted from real PDF metadata, not invented. This is the most important prompt in the whole project.

### 4. Radio-button export-state coercion (the hard one)

> *"pypdf is silently doing nothing when i call update_page_form_field_values on the radios in hcd-rt-480-5.pdf. /AS still says /Off after fill. these radios dont use /Yes /No, ive seen /Y /N /1 /0 and lowercase versions in the wild. write a function that takes a widget's /AP /N keys and a desired value (Yes No on or empty) and returns the right export state, or None if nothing matches. also when /Kids exists the export state is on the kids not the parent, handle that too"*

**Got:** a first cut of `choose_button_state` that handled `/Yes` / `/No` only.
**Edited:** rewrote it to iterate `clean_keys = [k.lstrip("/").strip().lower() for k in candidate_keys]` and added the `yes_like` / `no_like` allow-lists after I dumped the widget AP keys for all three forms and saw `/1`, `/0`, `/On` in the wild. Also added `apply_button_widgets` because `update_page_form_field_values` *does not* descend into `/Kids` on grouped radios. The model didn't know that, and it took me 30 minutes of `pypdf` source reading to confirm.

### 5. Verify-stage composite scoring

> *"i have two confidence signals per field. ade (can be None) and a regex/length rule. combine 50/50 when ade exists, otherwise rule only. bands: HIGH if >= 0.85, MEDIUM if >= 0.6 else LOW. pure helpers for unit tests"*

**Got:** `_composite_no_llm_optional_ade`, `_band`, and rule helpers.
**Edited:** dropped a third LLM-based signal and any external verify API; scoring is ADE + rules only.

### 6. SSE without a framework

> *"need an sse pattern in fastapi. each job keeps an append only list of pre formatted sse chunks. the /events endpoint reads from index 0 with its own cursor per connection and uses an asyncio.Event to wake when new stuff is appended. heads up the pipeline often emits before the EventSource even connects, those events cannot be dropped. ping every 15s when idle (`: ping\\n\\n`). close the stream after packet.ready, extract.failed, fill.failed, or stage.error"*

**Got:** the cursor + `asyncio.Event` pattern (`routes/jobs.py:_sse_stream`).
**Edited:** the model's first version closed the stream on the *outer* `wait_for` timeout. I moved the close logic into `_should_close_stream(msg)` so termination is decided per-event by name, not per-tick. Also added `X-Accel-Buffering: no` because nginx will otherwise buffer SSE for 4KB before flushing.

### 7. One-form-at-a-time review UX

> *"the review screen is one big flat form right now, kill it. replace with three tabs, one per hcd form (476.6G, 480.5, 476.6) in that visual order. inside each tab group fields by the section header from the actual pdf and use the exact pdf wording as the label. type specific inputs: text, date, number, yes/no radio that maps to my HCD_YES/HCD_NO constants. show a colored confidence pill next to each field that came from the title. disable the submit button until every required field across all three tabs is filled"*

**Got:** the tab structure, the `Field` / `DateField` / `YesNoField` / `SelectField` widgets in `review-form-widgets.tsx`, and the `canSubmit` boolean.
**Edited:** the AI's `canSubmit` was a `useMemo` with a 30-line dependency array. I flattened it into the explicit conjunction in `useReviewForm.ts:142-176`. It's ugly but it's auditable; when QA says *"why is the button disabled?"*, you can read the condition top-to-bottom.

### 8. Situs and registered-owner parsing

> *"write split_site_address and split_registered_owner as pure regex functions. addresses look like '520 Pine Ave #55, Santa Barbara, CA 93117' or '1 Main St, Fresno, Fresno County, CA 93701'. owners look like 'DOE, JANE M' or 'Jane M Doe' or just one token, sometimes company names like 'ACME HOMES LLC'. dont try to be clever, if its ambiguous return empty strings rather than guessing wrong"*

**Got:** the regex skeletons.
**Edited:** added the company-name allow-list `(llc|inc|corp|co|company|sales|hub|homes?|housing)` after the AI's first cut split `"ACME HOMES LLC"` into `first="ACME"`, `last="LLC"`. Also tightened `split_site_address` to strip the trailing `STATE ZIP` *before* doing the comma split, since the AI's version did them in the wrong order and `'CA 93701'` ended up in `city`.

### 9. Failure-mode terminal events

> *"go through the pipeline and find every failure path then emit a typed sse event for each. extraction http fail, extraction empty result, verify preconditions missing, merge payload error, fill error per form, generic stage error. every event payload needs at least `error` and `retry_hint` (string). server side log with logger.exception"*

**Got:** the event taxonomy now in `ARCHITECTURE.md` and the `extract.failed` / `verify.failed` / `fill.failed` / `stage.error` emissions.
**Edited:** removed three "telemetry" events the model invented that nothing on the frontend was listening to. *Lesson: AI loves to add observability nobody asked for.*

---

## Where I deliberately did not use AI

- **Field-name mapping in `form_maps.py`.** AI cannot guess the exact AcroForm label strings; only the PDF can tell you. I dumped them with the script from prompt #3 and pasted them in by hand.
- **The `JOBS` registry + TTL eviction logic.** I wrote this myself because the failure modes (lost wakeups, leaking IP map, eviction during iteration) are exactly the kind of thing an LLM gets confidently wrong.
- **The brief itself.** I read the PDF carefully before prompting anything, and the architecture choices (one-form-at-a-time review, deterministic Section 5 defaults, `Stockton, CA` execution location) came from the *brief's intent*, not from the model.

## What I'd change about the workflow next time

1. **Snapshot prompts in-repo as I go.** This file is reconstructed from memory and chat history; I should have piped each Composer session into `WORKFLOW_LOG.md` automatically.
2. **Use a smaller model for boilerplate, a frontier model for the hard parts.** I used Sonnet 4.6 for everything; Haiku would have been fine for prompts #1, #3, #6, and #8 at a fraction of the cost.
3. **Run the linter inside the prompt loop.** Several `ruff` and `mypy --strict` errors only surfaced after I'd already accepted the diff. A `just lint` in the loop would have caught them while context was hot.