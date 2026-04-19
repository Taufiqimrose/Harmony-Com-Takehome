/** Canonical HCD / PDF Yes–No answers (aligned with `apps/api/src/schema/yes_no.py`). */

export const HCD_YES = "Yes" as const;
export const HCD_NO = "No" as const;

export type HcdYesNo = typeof HCD_YES | typeof HCD_NO;
