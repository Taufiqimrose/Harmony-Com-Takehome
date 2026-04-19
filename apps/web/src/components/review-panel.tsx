import { useState } from "react";
import { ReviewForm4766Section } from "@/components/review-form-476-6-section";
import { ReviewForm4766GSection } from "@/components/review-form-476-6g-section";
import { ReviewForm4805Section } from "@/components/review-form-480-5-section";
import type { ScoredField } from "@/hooks/use-job-stream";
import { useReviewForm } from "@/hooks/use-review-form";
import { HCD_FORM_REVIEW_ORDER, HCD_PACKET_FORMS } from "@/lib/hcd-forms";
import { cn } from "@/lib/utils";

export interface ReviewPanelProps {
  visible: boolean;
  extracted: Record<string, string>;
  scored: Record<string, ScoredField>;
  onConfirm: (payload: {
    extracted_overrides: Record<string, string>;
    buyer: Record<string, string | boolean>;
  }) => void;
}

export function ReviewPanel({
  visible,
  extracted,
  scored,
  onConfirm,
}: ReviewPanelProps) {
  const { ext, setExt, buyer, setBuyer, canSubmit, ALL_EXTRACTED_ORDER } = useReviewForm(extracted);
  const [activeFormId, setActiveFormId] = useState<(typeof HCD_FORM_REVIEW_ORDER)[number]>(
    HCD_FORM_REVIEW_ORDER[0],
  );

  const activeIndex = HCD_FORM_REVIEW_ORDER.indexOf(activeFormId);
  const isFirstForm = activeIndex === 0;
  const isLastForm = activeIndex === HCD_FORM_REVIEW_ORDER.length - 1;

  if (!visible) return null;

  return (
    <div
      className="mx-auto mt-6 w-full max-w-4xl rounded-[12px] border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-lg transition-all duration-300 data-[visible=false]:opacity-0"
      data-testid="review-panel"
      data-visible={visible ? "true" : "false"}
    >
      <div className="mb-6">
        <h2 className="text-[24px] font-bold leading-tight">Review and confirm</h2>
        <p className="mt-1 text-[15px] text-[var(--color-muted)]">
          Data is grouped by HCD form name so you can match each PDF in the packet.
        </p>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-2 sm:grid-cols-3">
        {HCD_FORM_REVIEW_ORDER.map((formId) => {
          const meta = HCD_PACKET_FORMS.find((f) => f.formId === formId);
          return (
            <button
              key={formId}
              type="button"
              className={cn(
                "rounded-md border px-3 py-2 text-left text-[13px] font-semibold",
                activeFormId === formId
                  ? "border-[var(--color-primary-600)] bg-[var(--color-primary-50)] text-[var(--color-primary-700)]"
                  : "border-[var(--color-border)] bg-white text-[var(--color-muted)]",
              )}
              onClick={() => setActiveFormId(formId)}
            >
              {meta?.title ?? formId}
            </button>
          );
        })}
      </div>

      <div className="flex flex-col gap-6">
        {activeFormId === "476-6g" ? (
          <ReviewForm4766GSection
            ext={ext}
            setExt={setExt}
            buyer={buyer}
            setBuyer={setBuyer}
            scored={scored}
          />
        ) : null}

        {activeFormId === "480-5" ? (
          <ReviewForm4805Section
            ext={ext}
            setExt={setExt}
            buyer={buyer}
            setBuyer={setBuyer}
            scored={scored}
          />
        ) : null}

        {activeFormId === "476-6" ? (
          <ReviewForm4766Section buyer={buyer} setBuyer={setBuyer} />
        ) : null}
      </div>

      <div className="mt-6 flex items-center justify-between gap-3">
        <button
          type="button"
          disabled={isFirstForm}
          className={cn(
            "rounded-md border px-4 py-2 text-[14px] font-medium",
            isFirstForm
              ? "cursor-not-allowed border-[var(--color-border)] text-[var(--color-muted)]"
              : "border-[var(--color-border)] bg-white text-[var(--color-fg)] hover:bg-[var(--color-bg)]",
          )}
          onClick={() => setActiveFormId(HCD_FORM_REVIEW_ORDER[Math.max(0, activeIndex - 1)])}
        >
          ← Previous form
        </button>
        <button
          type="button"
          disabled={isLastForm}
          className={cn(
            "rounded-md border px-4 py-2 text-[14px] font-medium",
            isLastForm
              ? "cursor-not-allowed border-[var(--color-border)] text-[var(--color-muted)]"
              : "border-[var(--color-border)] bg-white text-[var(--color-fg)] hover:bg-[var(--color-bg)]",
          )}
          onClick={() =>
            setActiveFormId(
              HCD_FORM_REVIEW_ORDER[Math.min(HCD_FORM_REVIEW_ORDER.length - 1, activeIndex + 1)],
            )
          }
        >
          Next form →
        </button>
      </div>

      <button
        type="button"
        disabled={!canSubmit}
        className={cn(
          "mt-8 w-full rounded-md py-3 text-[15px] font-semibold text-white shadow-md",
          canSubmit
            ? "bg-[var(--color-primary-600)] hover:bg-[var(--color-primary-700)]"
            : "bg-[var(--color-primary-300)]",
        )}
        onClick={() =>
          onConfirm({
            extracted_overrides: Object.fromEntries(
              ALL_EXTRACTED_ORDER.map(([k]) => [k, ext[k] ?? ""]),
            ),
            buyer: { ...buyer },
          })
        }
      >
        Confirm & generate packet →
      </button>
    </div>
  );
}
