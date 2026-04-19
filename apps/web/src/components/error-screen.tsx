import { XCircle } from "@phosphor-icons/react";

export function ErrorScreen({
  message,
  onRetry,
  onReset,
}: {
  message: string;
  onRetry: () => void;
  onReset: () => void;
}) {
  return (
    <div className="mx-auto w-full max-w-4xl overflow-hidden rounded-[12px] bg-[var(--color-term-body)] shadow-xl">
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

      <div className="flex min-h-[480px] flex-col items-center justify-center gap-4 px-8 py-12 text-center">
        <XCircle aria-hidden className="h-12 w-12 text-[var(--color-danger-500)]" />
        <div className="text-[24px] font-bold">Something went wrong</div>
        <div className="max-w-xl text-[15px] text-[var(--color-fg-muted)]">{message}</div>
        <details className="max-w-xl text-left text-[12px] text-[var(--color-fg-muted)]">
          <summary className="cursor-pointer">details</summary>
          <pre className="mt-2 whitespace-pre-wrap font-mono text-[11px]">{message}</pre>
        </details>
        <div className="mt-4 flex gap-3">
          <button
            type="button"
            className="rounded-md bg-[var(--color-primary-600)] px-4 py-2 text-[14px] font-semibold text-white"
            onClick={onRetry}
          >
            Try again
          </button>
          <button
            type="button"
            className="rounded-md border border-[var(--color-border)] px-4 py-2 text-[14px] font-semibold"
            onClick={onReset}
          >
            Start over
          </button>
        </div>
      </div>
    </div>
  );
}
