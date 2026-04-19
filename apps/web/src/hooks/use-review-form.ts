import { useEffect, useMemo, useState } from "react";
import {
  ALL_EXTRACTED_ORDER,
  CORE_EXTRACTED_ORDER,
  splitRegisteredOwner,
  TITLE_4805_EXTRACTED_ORDER,
} from "@/lib/review-form-utils";
import { HCD_NO, HCD_YES } from "@/lib/yes-no";

export interface BuyerDraft {
  g6_smoke_detector_confirmed: boolean;
  g6_water_heater_confirmed: boolean;
  g6_own_home_confirmed: boolean;
  g6_own_land_answer: string;
  f4805_ro1_last: string;
  f4805_ro1_first: string;
  f4805_ro1_middle: string;
  f4805_ro2_last: string;
  f4805_ro2_first: string;
  f4805_ro2_middle: string;
  f4805_ro3_last: string;
  f4805_ro3_first: string;
  f4805_ro3_middle: string;
  f4805_current_mailing_street: string;
  f4805_current_mailing_city: string;
  f4805_current_mailing_county: string;
  f4805_current_mailing_state: string;
  f4805_current_mailing_zip: string;
  f4805_section2_purchased_from: string;
  f4805_s4_date_of_sale: string;
  f4805_s2_is_new_unit: string;
  f4805_s2_first_sold_new_date: string;
  f4805_s2_registered_in_ca_or_other_state: string;
  f4805_s2_last_registered_state_and_date: string;
  f4805_s2_entered_california_date: string;
  f4805_s2_last_licensed_resident_state: string;
  f4805_s2_resident_of_california: string;
  f4805_s2_became_resident_when: string;
  f4805_s3_outstanding_titles: string;
  f4805_s3_security_lien: string;
  f4805_4a_base_unit_price: string;
  f4805_4b_unattached_accessories_price: string;
  f4805_4d_sale_price: string;
  f4766_statement: string;
}

function initialBuyer(): BuyerDraft {
  return {
    g6_smoke_detector_confirmed: true,
    g6_water_heater_confirmed: true,
    g6_own_home_confirmed: true,
    g6_own_land_answer: "",
    f4805_ro1_last: "",
    f4805_ro1_first: "",
    f4805_ro1_middle: "",
    f4805_ro2_last: "",
    f4805_ro2_first: "",
    f4805_ro2_middle: "",
    f4805_ro3_last: "",
    f4805_ro3_first: "",
    f4805_ro3_middle: "",
    f4805_current_mailing_street: "",
    f4805_current_mailing_city: "",
    f4805_current_mailing_county: "",
    f4805_current_mailing_state: "CA",
    f4805_current_mailing_zip: "",
    f4805_section2_purchased_from: "",
    f4805_s4_date_of_sale: "",
    f4805_s2_is_new_unit: "",
    f4805_s2_first_sold_new_date: "",
    f4805_s2_registered_in_ca_or_other_state: "",
    f4805_s2_last_registered_state_and_date: "",
    f4805_s2_entered_california_date: "",
    f4805_s2_last_licensed_resident_state: "",
    f4805_s2_resident_of_california: "",
    f4805_s2_became_resident_when: "",
    f4805_s3_outstanding_titles: "",
    f4805_s3_security_lien: "",
    f4805_4a_base_unit_price: "",
    f4805_4b_unattached_accessories_price: "",
    f4805_4d_sale_price: "",
    f4766_statement: "",
  };
}

export function useReviewForm(extracted: Record<string, string>) {
  const [ext, setExt] = useState<Record<string, string>>({});
  const [buyer, setBuyer] = useState<BuyerDraft>(initialBuyer);

  useEffect(() => {
    setExt((prev) => {
      const next = { ...prev };
      for (const [k] of ALL_EXTRACTED_ORDER) {
        if (extracted[k] != null) next[k] = extracted[k];
      }
      return next;
    });
  }, [extracted]);

  useEffect(() => {
    const dfs = (ext.date_first_sold_new ?? "").trim();
    if (!dfs) return;
    setBuyer((prev) => {
      const next = { ...prev };
      if (!next.f4805_s2_is_new_unit.trim()) {
        next.f4805_s2_is_new_unit = HCD_NO;
      }
      if (!next.f4805_s2_first_sold_new_date.trim()) {
        next.f4805_s2_first_sold_new_date = dfs;
      }
      return next;
    });
  }, [ext.date_first_sold_new]);

  useEffect(() => {
    const owner = (ext.registered_owner ?? "").trim();
    if (!owner) return;
    setBuyer((prev) => {
      if (
        prev.f4805_ro1_last.trim() ||
        prev.f4805_ro1_first.trim() ||
        prev.f4805_ro1_middle.trim()
      ) {
        return prev;
      }
      return {
        ...prev,
        ...splitRegisteredOwner(owner),
      };
    });
  }, [ext.registered_owner]);

  const extractedComplete = useMemo(
    () => CORE_EXTRACTED_ORDER.every(([k]) => (ext[k] ?? "").trim().length > 0),
    [ext],
  );
  const title4805Complete = useMemo(
    () => TITLE_4805_EXTRACTED_ORDER.every(([k]) => (ext[k] ?? "").trim().length > 0),
    [ext],
  );
  const g6ConfirmComplete = buyer.g6_own_land_answer.trim().length > 0;
  const manual4805Complete =
    buyer.f4805_ro1_last.trim().length > 0 &&
    buyer.f4805_current_mailing_street.trim().length > 0 &&
    buyer.f4805_current_mailing_city.trim().length > 0 &&
    buyer.f4805_current_mailing_county.trim().length > 0 &&
    buyer.f4805_current_mailing_state.trim().length > 0 &&
    buyer.f4805_current_mailing_zip.trim().length > 0 &&
    buyer.f4805_section2_purchased_from.trim().length > 0 &&
    buyer.f4805_s4_date_of_sale.trim().length > 0 &&
    buyer.f4805_s2_is_new_unit.trim().length > 0 &&
    buyer.f4805_s2_registered_in_ca_or_other_state.trim().length > 0 &&
    buyer.f4805_s2_entered_california_date.trim().length > 0 &&
    buyer.f4805_s2_last_licensed_resident_state.trim().length > 0 &&
    buyer.f4805_s2_resident_of_california.trim().length > 0 &&
    buyer.f4805_s3_outstanding_titles.trim().length > 0 &&
    buyer.f4805_s3_security_lien.trim().length > 0 &&
    buyer.f4805_4a_base_unit_price.trim().length > 0 &&
    buyer.f4805_4b_unattached_accessories_price.trim().length > 0 &&
    (buyer.f4805_s2_is_new_unit === HCD_NO
      ? buyer.f4805_s2_first_sold_new_date.trim().length > 0
      : true) &&
    (buyer.f4805_s2_registered_in_ca_or_other_state === HCD_YES
      ? buyer.f4805_s2_last_registered_state_and_date.trim().length > 0
      : true) &&
    (buyer.f4805_s2_resident_of_california === HCD_YES
      ? buyer.f4805_s2_became_resident_when.trim().length > 0
      : true);
  const statementComplete = buyer.f4766_statement.trim().length > 0;

  const canSubmit =
    extractedComplete &&
    title4805Complete &&
    g6ConfirmComplete &&
    manual4805Complete &&
    statementComplete;

  return {
    ext,
    setExt,
    buyer,
    setBuyer,
    canSubmit,
    ALL_EXTRACTED_ORDER,
  };
}
