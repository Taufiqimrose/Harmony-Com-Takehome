export const CORE_EXTRACTED_ORDER = [
  ["serial", "Serial number"],
  ["decal", "Decal number"],
  ["make", "Make"],
  ["registered_owner", "Registered owner name"],
  ["site_address", "Site address"],
] as const;

export const TITLE_4805_EXTRACTED_ORDER = [
  ["manufacturer_name", "Name of Manufacturer:"],
  ["trade_name", "Trade Name:"],
  ["date_of_manufacture", "Date of Manufacture:"],
  ["model_name_or_number", "Model Name or #:"],
  ["date_first_sold_new", "Date First Sold New:"],
  ["hud_label_or_hcd_insignia", "HUD LABEL OR HCD INSIGNIA # (1)"],
  ["length_inches", "LENGTH (Inches) (1):"],
  ["width_inches", "WIDTH (Inches) (1):"],
] as const;

export const ALL_EXTRACTED_ORDER = [
  ...CORE_EXTRACTED_ORDER,
  ...TITLE_4805_EXTRACTED_ORDER,
] as const;

export function toInputDate(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) return "";
  if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
    return trimmed;
  }
  const mdy = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(trimmed);
  if (!mdy) return "";
  const [, mm, dd, yyyy] = mdy;
  return `${yyyy}-${mm.padStart(2, "0")}-${dd.padStart(2, "0")}`;
}

export function fromInputDate(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) return "";
  const ymd = /^(\d{4})-(\d{2})-(\d{2})$/.exec(trimmed);
  if (!ymd) return trimmed;
  const [, yyyy, mm, dd] = ymd;
  return `${mm}/${dd}/${yyyy}`;
}

export function splitRegisteredOwner(value: string): {
  f4805_ro1_last: string;
  f4805_ro1_first: string;
  f4805_ro1_middle: string;
} {
  const text = value.trim();
  if (!text) {
    return {
      f4805_ro1_last: "",
      f4805_ro1_first: "",
      f4805_ro1_middle: "",
    };
  }

  const companyHint = /\b(llc|inc|corp|co|company|sales|hub|homes?|housing)\b/i.test(text);
  if (companyHint) {
    return {
      f4805_ro1_last: text,
      f4805_ro1_first: "",
      f4805_ro1_middle: "",
    };
  }

  if (text.includes(",")) {
    const [last, rest = ""] = text.split(",", 2).map((part) => part.trim());
    const parts = rest.split(/\s+/).filter(Boolean);
    return {
      f4805_ro1_last: last,
      f4805_ro1_first: parts[0] ?? "",
      f4805_ro1_middle: parts.slice(1).join(" "),
    };
  }

  const parts = text.split(/\s+/).filter(Boolean);
  if (parts.length === 1) {
    return {
      f4805_ro1_last: parts[0],
      f4805_ro1_first: "",
      f4805_ro1_middle: "",
    };
  }

  return {
    f4805_ro1_last: parts.at(-1) ?? "",
    f4805_ro1_first: parts[0] ?? "",
    f4805_ro1_middle: parts.slice(1, -1).join(" "),
  };
}
