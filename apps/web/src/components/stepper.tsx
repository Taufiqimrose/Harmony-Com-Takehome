import { Check, X } from "@phosphor-icons/react";
import { Fragment } from "react";
import { cn } from "@/lib/utils";

const STEPS = [
  { id: "scan", label: "Scan" },
  { id: "extract", label: "Extract" },
  { id: "review", label: "Review" },
  { id: "fill", label: "Fill" },
  { id: "done", label: "Done" },
] as const;

type StepState = "pending" | "active" | "complete" | "error";

export interface StepperProps {
  states: StepState[];
  errorIndex?: number;
}

export function Stepper({ states, errorIndex }: StepperProps) {
  return (
    <div className="mx-auto mb-10 w-full max-w-4xl px-2 sm:px-4" data-testid="stepper">
      {/* items-start + connector mt so lines align with circle centers, not the label block */}
      <div className="flex w-full items-start">
        {STEPS.map((s, i) => {
          const st = states[i] ?? "pending";
          const err = errorIndex === i;

          const circle = err ? (
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--color-danger-500)] text-white shadow-sm">
              <X aria-hidden className="h-4 w-4" weight="bold" />
            </span>
          ) : st === "complete" ? (
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--color-primary-600)] text-white shadow-sm">
              <Check aria-hidden className="h-4 w-4" weight="bold" />
            </span>
          ) : (
            <span
              className={cn(
                "flex h-7 w-7 items-center justify-center rounded-full border-2 text-[12px] font-semibold shadow-sm",
                st === "active"
                  ? "border-[var(--color-primary-600)] bg-[var(--color-primary-50)] text-[var(--color-primary-600)]"
                  : "border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-muted)]",
              )}
            >
              {i + 1}
            </span>
          );

          /** Line segment between step i-1 and i: filled when the previous step is complete. */
          const connectorComplete = i > 0 && states[i - 1] === "complete" && errorIndex == null;

          const labelClass =
            err || st === "error"
              ? "text-[var(--color-danger-500)]"
              : st === "complete"
                ? "text-[var(--color-primary-800)]"
                : st === "active"
                  ? "text-[var(--color-primary-700)]"
                  : "text-[var(--color-muted)]";

          return (
            <Fragment key={s.id}>
              {i > 0 ? (
                <div
                  role="presentation"
                  className={cn(
                    "mt-[13px] h-0.5 min-w-[6px] flex-1 rounded-full transition-colors duration-300",
                    connectorComplete
                      ? "bg-[var(--color-primary-600)]"
                      : "bg-[var(--color-border)]",
                  )}
                />
              ) : null}
              <div className="flex w-[4.5rem] shrink-0 flex-col items-center gap-2 sm:w-[5.25rem]">
                {circle}
                <span
                  className={cn(
                    "max-w-[5.25rem] text-center text-[10px] font-semibold uppercase leading-tight tracking-wide sm:text-[11px]",
                    labelClass,
                  )}
                >
                  {s.label}
                </span>
              </div>
            </Fragment>
          );
        })}
      </div>
    </div>
  );
}

export function deriveStepperStates(input: {
  phase: string;
  ingestDone: boolean;
  verifyDone: boolean;
  confirmSent: boolean;
  packetDone: boolean;
  errorPhase: boolean;
}): { states: StepState[]; errorIndex?: number } {
  const { phase, ingestDone, verifyDone, confirmSent, packetDone, errorPhase } = input;
  const states: StepState[] = ["pending", "pending", "pending", "pending", "pending"];

  if (errorPhase) {
    const idx = !ingestDone ? 0 : !verifyDone ? 1 : !confirmSent ? 2 : !packetDone ? 3 : 4;
    for (let i = 0; i < idx; i++) states[i] = "complete";
    states[idx] = "error";
    return { states, errorIndex: idx };
  }

  if (phase === "idle") {
    states[0] = "active";
    return { states };
  }

  if (!ingestDone) {
    states[0] = "active";
    return { states };
  }
  states[0] = "complete";

  if (!verifyDone) {
    states[1] = "active";
    return { states };
  }
  states[1] = "complete";

  if (!confirmSent) {
    states[2] = "active";
    return { states };
  }
  states[2] = "complete";

  if (!packetDone) {
    states[3] = "active";
    return { states };
  }
  states[3] = "complete";

  if (phase === "done") {
    states[4] = "complete";
  } else {
    states[4] = "active";
  }
  return { states };
}
