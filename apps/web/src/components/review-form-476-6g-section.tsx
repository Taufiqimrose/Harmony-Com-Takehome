import type { Dispatch, SetStateAction } from "react";
import {
  BooleanYesNoField,
  ConfidencePill,
  FormReviewSection,
  YesNoField,
} from "@/components/review-form-widgets";
import type { ScoredField } from "@/hooks/use-job-stream";
import type { BuyerDraft } from "@/hooks/use-review-form";
import { HCD_PACKET_FORMS } from "@/lib/hcd-forms";
import { cn } from "@/lib/utils";

export function ReviewForm4766GSection({
  ext,
  setExt,
  buyer,
  setBuyer,
  scored,
}: {
  ext: Record<string, string>;
  setExt: Dispatch<SetStateAction<Record<string, string>>>;
  buyer: BuyerDraft;
  setBuyer: Dispatch<SetStateAction<BuyerDraft>>;
  scored: Record<string, ScoredField>;
}) {
  return (
    <FormReviewSection form={HCD_PACKET_FORMS[0]}>
      <div className="grid grid-cols-1 gap-3">
        {[
          ["decal", "Decal (License) No.(s) (page 1):"],
          ["serial", "Serial No.(s) (page 1):"],
          ["make", "Make:"],
          ["registered_owner", "Registered owner name:"],
          ["site_address", "Site address:"],
        ].map(([key, label]) => {
          const sc = scored[key];
          return (
            <label
              key={key}
              className="grid grid-cols-1 gap-2 md:grid-cols-[minmax(0,220px)_1fr] md:items-center md:gap-x-4"
            >
              <span className="text-[13px] text-[var(--color-muted)]">{label}</span>
              <div className="flex min-w-0 items-center gap-2">
                <input
                  className={cn(
                    "min-w-0 flex-1 rounded-md border-2 bg-white px-3 py-2 text-[15px] outline-none focus:ring-2 focus:ring-[var(--color-primary-600)]",
                    sc ? "border-[var(--color-border)]" : "border-[var(--color-border)]",
                  )}
                  type="text"
                  value={ext[key] ?? ""}
                  onChange={(e) => setExt((s) => ({ ...s, [key]: e.target.value }))}
                />
                <ConfidencePill fieldKey={key} scored={sc} />
              </div>
            </label>
          );
        })}
      </div>
      <div className="mt-6 grid gap-3">
        <BooleanYesNoField
          name="g6-smoke-co"
          label="I/We, the undersigned, hereby state that the manufactured home, mobilehome, or multifamily manufactured home described above is equipped with a properly working, operable smoke detector in accordance with California Health and Safety Code Section 18029.6 and a carbon monoxide detector in accordance to California Residential Code Section R315"
          value={buyer.g6_smoke_detector_confirmed}
          onChange={(v) => setBuyer((s) => ({ ...s, g6_smoke_detector_confirmed: v }))}
        />
        <BooleanYesNoField
          name="g6-own-home"
          label="Do you (the registered owner) own your manufactured home/mobilehome?"
          value={buyer.g6_own_home_confirmed}
          onChange={(v) => setBuyer((s) => ({ ...s, g6_own_home_confirmed: v }))}
        />
        <YesNoField
          name="g6-own-land"
          label="Do you (the registered owner) own the land your manufactured home/mobilehome is located on?"
          required
          value={buyer.g6_own_land_answer}
          onChange={(v) => setBuyer((s) => ({ ...s, g6_own_land_answer: v }))}
        />
        <BooleanYesNoField
          name="g6-water-heater"
          label="I/We the undersigned hereby state that all fuel gas-burning water heater appliances in the manufactured home, mobilehome, or multifamily manufactured housing described above are seismically braced, anchored, or strapped in accordance with Health and Safety Co"
          value={buyer.g6_water_heater_confirmed}
          onChange={(v) => setBuyer((s) => ({ ...s, g6_water_heater_confirmed: v }))}
        />
      </div>
    </FormReviewSection>
  );
}
