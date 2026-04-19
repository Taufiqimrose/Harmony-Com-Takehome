# UX Specification

## Current product shape

The app is a single-page workflow:

1. Header
2. Five-step progress bar
3. Upload area
4. Terminal log
5. Review or download panel, depending on job state

Everything happens on one page. There are no route changes during a transfer.

## Header

The page header is:

- `Title Transfer Agent`
- `by Mohammad imrose`

No logo or extra branding is needed.

## Stepper

The stepper shows five states:

1. Scan
2. Extract
3. Review
4. Fill
5. Done

It advances from SSE-backed job state and gives the user a clear sense of progress without requiring extra screens.

## Upload area

The upload area accepts the source title PDF.

Current behavior:

- drag and drop or click to browse
- validates that the file is a PDF
- collapses to a compact file summary once selected

## Terminal

The terminal is the main live feedback surface.

It shows:

- upload start
- ingest completion
- extraction progress
- extraction provider
- verification scoring
- fill progress
- packet completion
- errors

The tone should feel operational and clear, not flashy.

## Review flow

When the job reaches review:

- the terminal transitions out
- the review panel becomes the primary surface
- the review panel shows one form at a time

Current form order:

1. `476.6G`
2. `480.5`
3. `476.6`

The user can move forward and backward between forms. Labels match the PDF wording instead of internal shorthand.

## Review inputs

The current review screen uses field-specific controls:

- text inputs
- date inputs
- number inputs
- yes/no selectors

The goal is to make manual completion feel like filling the actual packet, not editing a raw JSON payload.

## Download state

After fill succeeds, the review view is replaced by a packet-ready panel that:

- lists the generated PDFs
- exposes the packet download action
- lets the user start another transfer

## Error handling

Fatal job failures stop the normal flow and show an error state instead of letting the user continue with invalid output.

## UX priorities

The current UI is designed around:

- clarity over effects
- confidence over novelty
- fast manual correction
- obvious progress feedback
