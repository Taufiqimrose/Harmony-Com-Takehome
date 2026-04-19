import type { ReactNode } from "react";
import type { ScoredField } from "@/hooks/use-job-stream";
import type { HCD_PACKET_FORMS } from "@/lib/hcd-forms";
import { fromInputDate, toInputDate } from "@/lib/review-form-utils";
import { cn } from "@/lib/utils";
import { HCD_NO, HCD_YES } from "@/lib/yes-no";

export function FormReviewSection({
  form,
  children,
}: {
  form: (typeof HCD_PACKET_FORMS)[number];
  children: ReactNode;
}) {
  const { formId, shortLabel, title, fileName, reviewHint } = form;
  return (
    <section
      aria-labelledby={`review-form-${formId}`}
      className="rounded-[10px] border border-[var(--color-border)] bg-[var(--color-bg)]/40 p-5 shadow-sm"
      data-form-id={formId}
      data-testid={`review-form-${formId}`}
    >
      <header className="mb-4 border-b border-[var(--color-border)] pb-4">
        <p className="text-[12px] font-semibold uppercase tracking-wider text-[var(--color-primary-600)]">
          Form {shortLabel}
        </p>
        <h3 id={`review-form-${formId}`} className="mt-1 text-[18px] font-semibold leading-snug">
          {title}
        </h3>
        <p className="mt-1 font-mono text-[13px] text-[var(--color-muted)]">{fileName}</p>
        <p className="mt-2 text-[14px] text-[var(--color-muted)]">{reviewHint}</p>
      </header>
      {children}
    </section>
  );
}

export function BooleanYesNoField({
  name,
  label,
  value,
  onChange,
}: {
  name: string;
  label: string;
  value: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <fieldset className="m-0 grid gap-2 border-0 p-0">
      <legend className="text-[13px] text-[var(--color-muted)]">{label}</legend>
      <div className="flex items-center gap-4 text-[14px]">
        <label className="inline-flex items-center gap-2">
          <input
            type="radio"
            className="h-4 w-4 border border-[var(--color-border)]"
            name={name}
            checked={value}
            onChange={() => onChange(true)}
          />
          <span>Yes</span>
        </label>
        <label className="inline-flex items-center gap-2">
          <input
            type="radio"
            className="h-4 w-4 border border-[var(--color-border)]"
            name={name}
            checked={!value}
            onChange={() => onChange(false)}
          />
          <span>No</span>
        </label>
      </div>
    </fieldset>
  );
}

export function YesNoField({
  name,
  label,
  value,
  onChange,
  required,
}: {
  name: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
}) {
  return (
    <fieldset className="m-0 grid gap-2 border-0 p-0">
      <legend className="text-[13px] text-[var(--color-muted)]">
        {label}
        {required ? <span className="text-[var(--color-danger-500)]"> *</span> : null}
      </legend>
      <div className="flex items-center gap-4 text-[14px]">
        <label className="inline-flex items-center gap-2">
          <input
            type="radio"
            className="h-4 w-4 border border-[var(--color-border)]"
            name={name}
            checked={value === HCD_YES}
            onChange={() => onChange(HCD_YES)}
          />
          <span>Yes</span>
        </label>
        <label className="inline-flex items-center gap-2">
          <input
            type="radio"
            className="h-4 w-4 border border-[var(--color-border)]"
            name={name}
            checked={value === HCD_NO}
            onChange={() => onChange(HCD_NO)}
          />
          <span>No</span>
        </label>
      </div>
    </fieldset>
  );
}

export function DateField({
  label,
  value,
  onChange,
  required,
  disabled,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  disabled?: boolean;
}) {
  return (
    <Field
      label={label}
      value={toInputDate(value)}
      required={required}
      disabled={disabled}
      inputType="date"
      onChange={(next) => onChange(fromInputDate(next))}
    />
  );
}

export function Field({
  label,
  value,
  onChange,
  required,
  disabled,
  inputType = "text",
  suffix,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  disabled?: boolean;
  inputType?: "text" | "date" | "number";
  suffix?: ReactNode;
}) {
  return (
    <label className="grid gap-1">
      <span className="text-[13px] text-[var(--color-muted)]">
        {label}
        {required ? <span className="text-[var(--color-danger-500)]"> *</span> : null}
      </span>
      <div className="flex min-w-0 items-center gap-2">
        <input
          type={inputType}
          step={inputType === "number" ? "any" : undefined}
          inputMode={inputType === "number" ? "decimal" : undefined}
          className="min-w-0 flex-1 rounded-md border-2 border-[var(--color-border)] bg-white px-3 py-2 text-[15px] outline-none focus:ring-2 focus:ring-[var(--color-primary-600)]"
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
        />
        {suffix}
      </div>
    </label>
  );
}

export function SelectField({
  label,
  value,
  onChange,
  options,
  required,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: string[];
  required?: boolean;
}) {
  return (
    <label className="grid gap-1">
      <span className="text-[13px] text-[var(--color-muted)]">
        {label}
        {required ? <span className="text-[var(--color-danger-500)]"> *</span> : null}
      </span>
      <select
        className="rounded-md border-2 border-[var(--color-border)] bg-white px-3 py-2 text-[15px] outline-none focus:ring-2 focus:ring-[var(--color-primary-600)]"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">Select</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </label>
  );
}

export function ConfidencePill({ fieldKey, scored }: { fieldKey: string; scored?: ScoredField }) {
  if (!scored?.band) {
    return (
      <div
        data-testid={`confidence-pill-${fieldKey}`}
        className="shrink-0 whitespace-nowrap rounded-sm border border-[var(--color-border)] bg-[var(--color-surface)] px-2 py-1 text-[11px] font-semibold text-[var(--color-muted)]"
        title="Not scored yet"
      >
        —
      </div>
    );
  }
  const band = scored.band;
  const color =
    band === "HIGH"
      ? "text-[var(--color-success-500)]"
      : band === "MEDIUM"
        ? "text-[var(--color-warning-500)]"
        : "text-[var(--color-danger-500)]";

  return (
    <div
      data-testid={`confidence-pill-${fieldKey}`}
      className="shrink-0 whitespace-nowrap rounded-sm border border-[var(--color-border)] bg-[var(--color-surface)] px-2 py-1 text-[11px] font-semibold uppercase tracking-wide text-[var(--color-fg)]"
      title={`Final: ${scored.final.toFixed(2)}`}
    >
      <span className={cn("mr-1 inline-block h-2 w-2 rounded-full bg-current", color)} />
      {band}
    </div>
  );
}
