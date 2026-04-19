# Design Tokens

## Purpose

This file describes the visual constants that show up across the current UI:

- page surface
- terminal window
- stepper
- review panel
- download panel
- inputs and buttons

## Principles

1. Keep the layout clean and readable.
2. Let the terminal and form flow do the heavy lifting.
3. Use a small set of colors and spacing rules consistently.

## Color roles

The main token groups used in `apps/web/src/styles/globals.css` are:

- `--color-primary-*` for active states and main actions
- `--color-success-500`, `--color-warning-500`, `--color-danger-500` for status
- `--color-bg`, `--color-surface`, `--color-border`, `--color-muted`, `--color-fg` for page and panel surfaces
- terminal-specific colors for the titlebar, body, prompt, arrow, and cursor

## Typography

Two font roles are used:

- Satoshi for the app interface
- JetBrains Mono for terminal output

Typical sizes:

- headings around `24px`
- panel titles around `18px`
- body text around `15px`
- labels and helper text around `13px`
- pills and compact metadata around `11px`

## Shared component shapes


| Element                | Shape                   |
| ---------------------- | ----------------------- |
| Terminal window        | rounded large container |
| Review/download panels | rounded large container |
| Inputs and buttons     | medium rounded corners  |
| Confidence pills       | small rounded corners   |
| Stepper circles        | full round              |


## Spacing

The UI follows a simple 8px rhythm:

- `8px` for tight gaps
- `12px` for field spacing
- `16px` for component padding
- `24px` for card padding
- `32px` for larger section spacing

## Current component styling notes

- The terminal is the main visual anchor on the page.
- The review panel sits below it and shows one form at a time.
- Confidence pills use semantic colors but stay compact.
- Inputs stay neutral and readable rather than decorative.
- Buttons emphasize clarity over visual flair.