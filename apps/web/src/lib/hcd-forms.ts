/**
 * Packet forms — aligned with `apps/api/src/pipeline/fill.FORMS` (order + filenames).
 * Review UI groups fields under these names so the demo matches the zip contents.
 */
export const HCD_PACKET_FORMS = [
  {
    formId: "476-6g",
    shortLabel: "476.6G",
    title: "HCD RT 476.6G",
    fileName: "hcd-rt-476-6g.pdf",
    reviewHint: "Fields taken from the scanned title (ADE extraction + your edits).",
  },
  {
    formId: "476-6",
    shortLabel: "476.6",
    title: "HCD RT 476.6",
    fileName: "hcd-rt-476-6.pdf",
    reviewHint: "Buyer / transferee and sale details for the transfer.",
  },
  {
    formId: "480-5",
    shortLabel: "480.5",
    title: "HCD RT 480.5",
    fileName: "hcd-rt-480-5.pdf",
    reviewHint: "Typed signatures and date merged into the packet for this demo.",
  },
] as const;

export type HcdFormId = (typeof HCD_PACKET_FORMS)[number]["formId"];

/** Tab order on the review screen (differs from zip generation order). See `HCD_FORM_REVIEW_ORDER` in `apps/api/src/schema/forms.py`. */
export const HCD_FORM_REVIEW_ORDER = [
  "476-6g",
  "480-5",
  "476-6",
] as const satisfies readonly HcdFormId[];
