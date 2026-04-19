import { useMemo, useState } from "react";
import { DownloadPanel } from "@/components/download-panel";
import { DropZone, type DropZoneFile } from "@/components/drop-zone";
import { ErrorScreen } from "@/components/error-screen";
import { ReviewPanel } from "@/components/review-panel";
import { deriveStepperStates, Stepper } from "@/components/stepper";
import { Terminal } from "@/components/terminal";
import { useJobStream } from "@/hooks/use-job-stream";
import { confirmJob, createJob } from "@/lib/api";
import { cn } from "@/lib/utils";

function formatBytes(n: number) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

export default function App() {
  const [file, setFile] = useState<DropZoneFile | null>(null);
  const [busy, setBusy] = useState(false);
  const stream = useJobStream();

  const stepper = useMemo(
    () =>
      deriveStepperStates({
        phase: stream.phase,
        ingestDone: stream.ingestDone,
        verifyDone: stream.verifyDone,
        confirmSent: stream.confirmSent,
        packetDone: stream.packetDone,
        errorPhase: stream.phase === "error",
      }),
    [stream.phase, stream.ingestDone, stream.verifyDone, stream.confirmSent, stream.packetDone],
  );

  const [uploadHint, setUploadHint] = useState<string | null>(null);

  const isReview = stream.phase === "review";
  const hideTerminal = isReview || stream.phase === "done";
  const showPacketReady = stream.phase === "done" && stream.jobId != null;

  async function onChooseUpload(f: File) {
    setUploadHint(null);
    if (f.type !== "application/pdf") {
      setUploadHint("Please upload a PDF file.");
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setUploadHint("File too large (max 10MB).");
      return;
    }
    stream.reset();
    setBusy(true);
    setFile({ file: f, sizeLabel: formatBytes(f.size) });
    try {
      const { job_id } = await createJob(f);
      stream.pushLine(`$ upload ${f.name}`);
      stream.startStream(job_id);
    } catch (e) {
      stream.pushLine(`✕ upload failed ${e instanceof Error ? e.message : String(e)}`);
      setBusy(false);
      return;
    }
    setBusy(false);
  }

  function onClear() {
    stream.reset();
    setFile(null);
    setBusy(false);
  }

  async function onConfirm(payload: {
    extracted_overrides: Record<string, string>;
    buyer: Record<string, string | boolean>;
  }) {
    if (!stream.jobId) return;
    setBusy(true);
    stream.markConfirmSent();
    stream.pushLine("$ confirm & generate packet");
    try {
      await confirmJob(stream.jobId, {
        extracted_overrides: payload.extracted_overrides,
        buyer: payload.buyer,
      });
    } catch (e) {
      stream.pushLine(`✕ confirm failed ${e instanceof Error ? e.message : String(e)}`);
    }
    setBusy(false);
  }

  if (stream.phase === "error" && stream.error) {
    return (
      <div className="min-h-screen bg-[var(--color-bg)] px-4 py-10">
        <Header />
        <ErrorScreen
          message={stream.error}
          onRetry={() => window.location.reload()}
          onReset={() => window.location.reload()}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--color-bg)] px-4 py-10">
      <Header />

      <Stepper states={stepper.states} errorIndex={stepper.errorIndex} />

      <DropZone
        disabled={busy || stream.phase === "running" || stream.phase === "filling"}
        file={file}
        onFile={onChooseUpload}
        onClear={onClear}
      />
      {uploadHint ? (
        <p className="mx-auto mt-3 max-w-4xl text-center text-[14px] text-[var(--color-danger-500)]">
          {uploadHint}
        </p>
      ) : null}

      <div className="relative mx-auto w-full max-w-4xl">
        <div
          className={cn(
            "transition-[opacity,transform] duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]",
            hideTerminal
              ? "pointer-events-none absolute inset-x-0 top-0 z-0 opacity-0"
              : "relative z-10 opacity-100",
          )}
          aria-hidden={hideTerminal}
        >
          <Terminal lines={stream.lines} />
        </div>

        {isReview ? (
          <div className="animate-review-in relative z-20">
            <ReviewPanel
              visible
              extracted={stream.extracted}
              scored={stream.scored}
              onConfirm={(p) => void onConfirm(p)}
            />
          </div>
        ) : null}

        {showPacketReady ? (
          <div className="animate-packet-in relative z-20">
            <DownloadPanel visible jobId={stream.jobId} />
          </div>
        ) : null}
      </div>
    </div>
  );
}

function Header() {
  return (
    <div className="mx-auto mb-8 max-w-4xl text-center">
      <h1 className="text-[24px] font-bold text-[var(--color-fg)]">Title Transfer Agent</h1>
      <p className="mt-2 text-[13px] text-[var(--color-muted)]">by Mohammad imrose</p>
    </div>
  );
}
