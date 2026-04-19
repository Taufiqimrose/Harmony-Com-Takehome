import { CheckCircle } from "@phosphor-icons/react";
import { useState } from "react";
import { packetUrl } from "@/lib/api";
import { HCD_PACKET_FORMS } from "@/lib/hcd-forms";

export function DownloadPanel({ visible, jobId }: { visible: boolean; jobId: string | null }) {
  const [downloaded, setDownloaded] = useState(false);

  if (!visible || !jobId) return null;

  return (
    <div
      className="mx-auto mt-6 w-full max-w-4xl rounded-[12px] border border-[var(--color-border)] bg-[var(--color-surface)] p-10 text-center shadow-lg"
      data-testid="download-panel"
    >
      <div className="mx-auto mb-4 flex justify-center">
        <CheckCircle aria-hidden className="h-10 w-10 text-[var(--color-success-500)]" />
      </div>
      <h2 className="text-[24px] font-bold">Packet ready</h2>
      <p className="mt-2 text-[15px] text-[var(--color-muted)]">
        Three HCD forms, signature-ready.
      </p>

      <div className="mx-auto mt-8 max-w-xl space-y-2 text-left font-mono text-[14px]">
        {HCD_PACKET_FORMS.map((f) => (
          <div key={f.formId} className="flex justify-between gap-6">
            <span>{f.fileName}</span>
            <span className="text-[var(--color-muted)]">generated</span>
          </div>
        ))}
      </div>

      <div className="mt-8 flex flex-col items-center gap-3">
        <button
          type="button"
          className="h-12 w-80 max-w-full rounded-md bg-[var(--color-primary-600)] px-6 text-[15px] font-semibold text-white shadow-md hover:bg-[var(--color-primary-700)]"
          onClick={() => {
            window.location.assign(packetUrl(jobId));
            setDownloaded(true);
          }}
        >
          Download packet{downloaded ? " ✓" : ""}
        </button>
        <button
          type="button"
          className="text-[13px] text-[var(--color-primary-600)] underline-offset-4 hover:underline"
          onClick={() => window.location.reload()}
        >
          Start new transfer
        </button>
      </div>
    </div>
  );
}
