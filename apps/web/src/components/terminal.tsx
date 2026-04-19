import type { ReactElement } from "react";
import { useEffect, useRef } from "react";

export function Terminal({ lines }: { lines: string[] }) {
  const ref = useRef<HTMLDivElement | null>(null);

  // biome-ignore lint/correctness/useExhaustiveDependencies: scroll follows appended log lines
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [lines]);

  return (
    <div
      className="mx-auto w-full max-w-4xl overflow-hidden rounded-[12px] bg-[var(--color-term-body)] shadow-xl"
      data-testid="terminal"
    >
      <div className="flex h-10 items-center border-b border-[var(--color-term-titlebar-border)] bg-[var(--color-term-titlebar)] px-3">
        <div className="flex gap-2 pl-2">
          <span className="h-3 w-3 rounded-full bg-[var(--color-traffic-close)]" />
          <span className="h-3 w-3 rounded-full bg-[var(--color-traffic-min)]" />
          <span className="h-3 w-3 rounded-full bg-[var(--color-traffic-max)]" />
        </div>
        <div className="flex-1 text-center text-[13px] font-medium text-[var(--color-fg)]">
          Title Transfer Agent
        </div>
      </div>
      <div
        ref={ref}
        className="h-[480px] overflow-y-auto p-6 font-mono text-[13px] leading-relaxed text-[var(--color-term-text)]"
      >
        {lines.length === 0 ? (
          <span className="text-[var(--color-muted)]">(waiting for upload)</span>
        ) : (
          lines.map((l, i) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: append-only log; index is stable for this list
            <TerminalLine key={`${i}-${l}`} line={l} />
          ))
        )}
        <span className="text-[var(--color-fg)]">█</span>
      </div>
    </div>
  );
}

function TerminalLine({ line }: { line: string }) {
  const isPrompt = line.startsWith("$");
  const isOk = line.startsWith("✓");
  const isWarn = line.startsWith("⚠");
  const isErr = line.startsWith("✕");

  let color = "text-[var(--color-term-text)]";
  if (isOk) color = "text-[var(--color-success-500)]";
  if (isWarn) color = "text-[var(--color-warning-500)]";
  if (isErr) color = "text-[var(--color-danger-500)]";

  return renderLine(color, isPrompt, line);
}

function renderLine(color: string, isPrompt: boolean, line: string): ReactElement {
  if (isPrompt) {
    return (
      <div className="mb-1">
        <span className="text-[var(--color-term-prompt)]">$</span>{" "}
        <span className="text-[var(--color-term-text)]">{line.slice(1).trimStart()}</span>
      </div>
    );
  }
  if (line.startsWith("→")) {
    const rest = line.slice(1).trimStart();
    const [ev, ...payload] = rest.split(/\s{2,}/);
    return (
      <div className="mb-1">
        <span className="text-[var(--color-term-arrow)]">→</span>{" "}
        <span className="text-[var(--color-term-text-muted)]">{pad(ev, 22)}</span>{" "}
        <span className="text-[var(--color-term-text)]">{payload.join("  ")}</span>
      </div>
    );
  }
  return <div className={`mb-1 ${color}`}>{line}</div>;
}

function pad(s: string, n: number) {
  return s.length >= n ? s.slice(0, n) : s + " ".repeat(n - s.length);
}
