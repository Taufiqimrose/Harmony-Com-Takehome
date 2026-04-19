import type { Dispatch, SetStateAction } from "react";
import {
  ConfidencePill,
  DateField,
  Field,
  FormReviewSection,
  SelectField,
  YesNoField,
} from "@/components/review-form-widgets";
import type { ScoredField } from "@/hooks/use-job-stream";
import type { BuyerDraft } from "@/hooks/use-review-form";
import { HCD_PACKET_FORMS } from "@/lib/hcd-forms";
import { TITLE_4805_EXTRACTED_ORDER } from "@/lib/review-form-utils";
import { HCD_NO, HCD_YES } from "@/lib/yes-no";

export function ReviewForm4805Section({
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
    <FormReviewSection form={HCD_PACKET_FORMS[2]}>
      <h4 className="mb-3 text-[13px] font-semibold uppercase tracking-wide text-[var(--color-muted)]">
        Title-derived fields
      </h4>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {TITLE_4805_EXTRACTED_ORDER.map(([key, label]) => (
          <Field
            key={key}
            label={label}
            required
            value={ext[key] ?? ""}
            onChange={(v) => setExt((s) => ({ ...s, [key]: v }))}
            suffix={<ConfidencePill fieldKey={key} scored={scored[key]} />}
          />
        ))}
      </div>

      <h4 className="mb-3 mt-6 text-[13px] font-semibold uppercase tracking-wide text-[var(--color-muted)]">
        Registered Owner(s)
      </h4>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        <Field
          label="Last name of Registered Owner(s) (1):"
          required
          value={buyer.f4805_ro1_last}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_ro1_last: v }))}
        />
        <Field
          label="First name of Registered Owner(s) (1):"
          value={buyer.f4805_ro1_first}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_ro1_first: v }))}
        />
        <Field
          label="Middle name of Registered Owner(s) (1):"
          value={buyer.f4805_ro1_middle}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_ro1_middle: v }))}
        />
        <Field
          label="Last name of Registered Owner(s) (2):"
          value={buyer.f4805_ro2_last}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_ro2_last: v }))}
        />
        <Field
          label="First name of Registered Owner(s) (2):"
          value={buyer.f4805_ro2_first}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_ro2_first: v }))}
        />
        <Field
          label="Middle name of Registered Owner(s) (2):"
          value={buyer.f4805_ro2_middle}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_ro2_middle: v }))}
        />
        <Field
          label="Last name of Registered Owner(s) (3):"
          value={buyer.f4805_ro3_last}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_ro3_last: v }))}
        />
        <Field
          label="First name of Registered Owner(s) (3):"
          value={buyer.f4805_ro3_first}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_ro3_first: v }))}
        />
        <Field
          label="Middle name of Registered Owner(s) (3):"
          value={buyer.f4805_ro3_middle}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_ro3_middle: v }))}
        />
      </div>

      <h4 className="mb-3 mt-6 text-[13px] font-semibold uppercase tracking-wide text-[var(--color-muted)]">
        Current Mailing Address for Registered Owner(s)
      </h4>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <Field
          label="Street of Current Mailing Address for Registered Owner(s):"
          required
          value={buyer.f4805_current_mailing_street}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_current_mailing_street: v }))}
        />
        <Field
          label="City of Current Mailing Address for Registered Owner(s):"
          required
          value={buyer.f4805_current_mailing_city}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_current_mailing_city: v }))}
        />
        <Field
          label="County of Current Mailing Address for Registered Owner(s):"
          required
          value={buyer.f4805_current_mailing_county}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_current_mailing_county: v }))}
        />
        <Field
          label="State of Current Mailing Address for Registered Owner(s):"
          required
          value={buyer.f4805_current_mailing_state}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_current_mailing_state: v }))}
        />
        <Field
          label="Zip of Current Mailing Address for Registered Owner(s):"
          required
          value={buyer.f4805_current_mailing_zip}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_current_mailing_zip: v }))}
        />
      </div>

      <h4 className="mb-3 mt-6 text-[13px] font-semibold uppercase tracking-wide text-[var(--color-muted)]">
        480.5 side 2 manual inputs (Section 4 + Section 2 A-E)
      </h4>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        <SelectField
          label="This unit was purchased from"
          required
          value={buyer.f4805_section2_purchased_from}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_section2_purchased_from: v }))}
          options={["dealer", "manufacturer", "individual"]}
        />
        <DateField
          label="Enter the date of sale:"
          required
          value={buyer.f4805_s4_date_of_sale}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_s4_date_of_sale: v }))}
        />
        <YesNoField
          name="f4805-s2-new-unit"
          label="Is this a new unit?"
          required
          value={buyer.f4805_s2_is_new_unit}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_s2_is_new_unit: v }))}
        />
        <DateField
          label='If "NO", enter the date the unit was first sold new:'
          required={buyer.f4805_s2_is_new_unit === HCD_NO}
          disabled={buyer.f4805_s2_is_new_unit !== HCD_NO}
          value={buyer.f4805_s2_first_sold_new_date}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_s2_first_sold_new_date: v }))}
        />
        <YesNoField
          name="f4805-s2-registered"
          label="Has this unit been registered in California or any other State?"
          required
          value={buyer.f4805_s2_registered_in_ca_or_other_state}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_s2_registered_in_ca_or_other_state: v }))}
        />
        <Field
          label='If "YES", enter the state and the date the unit was last registered in:'
          required={buyer.f4805_s2_registered_in_ca_or_other_state === HCD_YES}
          disabled={buyer.f4805_s2_registered_in_ca_or_other_state !== HCD_YES}
          value={buyer.f4805_s2_last_registered_state_and_date}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_s2_last_registered_state_and_date: v }))}
        />
        <DateField
          label="Enter the month, day, and year the unit entered California:"
          required
          value={buyer.f4805_s2_entered_california_date}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_s2_entered_california_date: v }))}
        />
        <Field
          label="When the unit was last licensed, what state were you a resident of?:"
          required
          value={buyer.f4805_s2_last_licensed_resident_state}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_s2_last_licensed_resident_state: v }))}
        />
        <YesNoField
          name="f4805-s2-ca-resident"
          label="Are you a resident of California"
          required
          value={buyer.f4805_s2_resident_of_california}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_s2_resident_of_california: v }))}
        />
        <DateField
          label='If "YES", when did you become a resident?:'
          required={buyer.f4805_s2_resident_of_california === HCD_YES}
          disabled={buyer.f4805_s2_resident_of_california !== HCD_YES}
          value={buyer.f4805_s2_became_resident_when}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_s2_became_resident_when: v }))}
        />
        <YesNoField
          name="f4805-s3-outstanding-titles"
          label="Except for any accompanying titles, are there any outstanding titles for this unit issued by any state?"
          required
          value={buyer.f4805_s3_outstanding_titles}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_s3_outstanding_titles: v }))}
        />
        <YesNoField
          name="f4805-s3-security-lien"
          label="Is this unit now being used as security for any lien(s) other than the lien(s) shown (if any) on the reverse side of this application?"
          required
          value={buyer.f4805_s3_security_lien}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_s3_security_lien: v }))}
        />
        <Field
          label="Base unit (do not include sales tax, finance charges, transportation or installation charges) ($):"
          required
          inputType="number"
          value={buyer.f4805_4a_base_unit_price}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_4a_base_unit_price: v }))}
        />
        <Field
          label="Unattached accessories (skirting, awning, refrigerator, etc.) ($):"
          required
          inputType="number"
          value={buyer.f4805_4b_unattached_accessories_price}
          onChange={(v) => setBuyer((s) => ({ ...s, f4805_4b_unattached_accessories_price: v }))}
        />
      </div>
      <p className="mt-3 text-[12px] text-[var(--color-muted)]">
        Section 5 exemption yes/no fields are hardcoded to <strong>No</strong>.
      </p>
    </FormReviewSection>
  );
}
