import type { Dispatch, SetStateAction } from "react";
import { Field, FormReviewSection } from "@/components/review-form-widgets";
import type { BuyerDraft } from "@/hooks/use-review-form";
import { HCD_PACKET_FORMS } from "@/lib/hcd-forms";

export function ReviewForm4766Section({
  buyer,
  setBuyer,
}: {
  buyer: BuyerDraft;
  setBuyer: Dispatch<SetStateAction<BuyerDraft>>;
}) {
  return (
    <FormReviewSection form={HCD_PACKET_FORMS[1]}>
      <div className="grid grid-cols-1 gap-3">
        <Field
          label="Statement"
          required
          value={buyer.f4766_statement}
          onChange={(v) => setBuyer((s) => ({ ...s, f4766_statement: v }))}
        />
        <p className="text-[12px] text-[var(--color-muted)]">
          Decal (License) Number and Trade Name are auto-filled from title extraction.
        </p>
      </div>
    </FormReviewSection>
  );
}
