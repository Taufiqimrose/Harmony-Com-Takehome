import { useCallback, useRef, useState } from "react";

export type UiPhase = "idle" | "running" | "review" | "filling" | "done" | "error";

export interface ScoredField {
  name: string;
  final: number;
  band?: string;
  components: { ade: number | null; rule: number };
  flags: string[];
}

export function useJobStream() {
  const [lines, setLines] = useState<string[]>([]);
  const [phase, setPhase] = useState<UiPhase>("idle");
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [extracted, setExtracted] = useState<Record<string, string>>({});
  const [scored, setScored] = useState<Record<string, ScoredField>>({});
  const [ingestDone, setIngestDone] = useState(false);
  const [verifyDone, setVerifyDone] = useState(false);
  const [confirmSent, setConfirmSent] = useState(false);
  const [packetDone, setPacketDone] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  const pushLine = useCallback((line: string) => {
    setLines((prev) => [...prev, line]);
  }, []);

  const closeStream = useCallback(() => {
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }
  }, []);

  const startStream = useCallback(
    (id: string) => {
      closeStream();
      setJobId(id);
      setError(null);
      setPhase("running");
      setExtracted({});
      setScored({});
      setIngestDone(false);
      setVerifyDone(false);
      setConfirmSent(false);
      setPacketDone(false);

      const url = `/jobs/${id}/events`;
      const es = new EventSource(url);
      esRef.current = es;

      const onFatal = (msg: string) => {
        setPhase("error");
        setError(msg);
        closeStream();
      };

      es.addEventListener("ingest.complete", (e) => {
        const _d = JSON.parse((e as MessageEvent).data as string);
        setIngestDone(true);
        pushLine(
          `→ ingest.complete     ${_d.filename} · ${_d.size_bytes} bytes · ${_d.page_count} page(s)`,
        );
      });

      es.addEventListener("extract.started", () => {
        pushLine("→ extract.started");
      });

      es.addEventListener("extract.provider", (e) => {
        const d = JSON.parse((e as MessageEvent).data as string) as {
          provider?: string;
          parse_model?: string;
        };
        const model = d.parse_model ? ` · ${d.parse_model}` : "";
        pushLine(`→ extract.provider    ${d.provider ?? "unknown"}${model}`);
      });

      es.addEventListener("extract.field", (e) => {
        const d = JSON.parse((e as MessageEvent).data as string) as {
          name: string;
          value: string;
        };
        setExtracted((prev) => ({ ...prev, [d.name]: d.value }));
        pushLine(`→ extract.field       ${d.name} = "${d.value}"`);
      });

      es.addEventListener("extract.complete", (e) => {
        const d = JSON.parse((e as MessageEvent).data as string) as {
          count: number;
          seconds?: number;
        };
        pushLine(
          `\u2713 extract.complete    ${d.count} fields${d.seconds != null ? ` in ${d.seconds}s` : ""}`,
        );
      });

      es.addEventListener("extract.failed", (e) => {
        const d = JSON.parse((e as MessageEvent).data as string) as { error: string };
        pushLine(`\u2715 extract.failed      ${d.error}`);
        onFatal(d.error);
      });

      es.addEventListener("verify.started", () => {
        pushLine("→ verify.started");
      });

      es.addEventListener("verify.field_scored", (e) => {
        const d = JSON.parse((e as MessageEvent).data as string) as {
          name: string;
          final_confidence: number;
          band?: string;
          components: { ade: number | null; rule: number };
          flags: string[];
        };
        setScored((prev) => ({
          ...prev,
          [d.name]: {
            name: d.name,
            final: d.final_confidence,
            band: d.band,
            components: d.components,
            flags: d.flags,
          },
        }));
        pushLine(
          `→ verify.field_scored ${d.name} · final=${d.final_confidence.toFixed(2)} · ${d.band ?? "?"}`,
        );
      });

      es.addEventListener("verify.failed", (e) => {
        const d = JSON.parse((e as MessageEvent).data as string) as { error?: string };
        const msg = d.error ?? "verify.failed";
        pushLine(`\u2715 verify.failed       ${msg}`);
        onFatal(msg);
      });

      es.addEventListener("verify.complete", () => {
        setVerifyDone(true);
        pushLine(`\u2713 verify.complete`);
      });

      es.addEventListener("awaiting_review", () => {
        pushLine("→ awaiting_review");
        setPhase("review");
      });

      es.addEventListener("fill.started", () => {
        pushLine("→ fill.started");
        setPhase("filling");
      });

      es.addEventListener("fill.form_complete", (e) => {
        const d = JSON.parse((e as MessageEvent).data as string) as {
          form_id: string;
          fill_mode?: "acroform" | "overlay" | "stub";
          fields_written?: number;
        };
        const mode = d.fill_mode ?? "unknown";
        const fields = d.fields_written ?? 0;
        pushLine(`→ fill.form_complete  ${d.form_id} · ${mode} · ${fields} fields`);
      });

      es.addEventListener("packet.ready", (e) => {
        const d = JSON.parse((e as MessageEvent).data as string) as { size_bytes: number };
        setPacketDone(true);
        pushLine(`→ packet.ready        zip · ${d.size_bytes} bytes`);
        setPhase("done");
        closeStream();
      });

      es.addEventListener("fill.failed", (e) => {
        const d = JSON.parse((e as MessageEvent).data as string) as { error: string };
        pushLine(`\u2715 fill.failed         ${d.error}`);
        onFatal(d.error);
      });

      es.addEventListener("stage.error", (e) => {
        const d = JSON.parse((e as MessageEvent).data as string) as {
          error?: string;
          stage?: string;
        };
        pushLine(`\u2715 stage.error         ${d.stage ?? "?"} · ${d.error ?? "error"}`);
        onFatal(d.error ?? "stage error");
      });

      es.onerror = () => {
        // EventSource will retry; if stream ended normally we already closed.
      };
    },
    [closeStream, pushLine],
  );

  const reset = useCallback(() => {
    closeStream();
    setLines([]);
    setPhase("idle");
    setJobId(null);
    setError(null);
    setExtracted({});
    setScored({});
    setIngestDone(false);
    setVerifyDone(false);
    setConfirmSent(false);
    setPacketDone(false);
  }, [closeStream]);

  const markConfirmSent = useCallback(() => {
    setConfirmSent(true);
  }, []);

  return {
    lines,
    phase,
    jobId,
    error,
    extracted,
    scored,
    ingestDone,
    verifyDone,
    confirmSent,
    packetDone,
    startStream,
    reset,
    pushLine,
    closeStream,
    markConfirmSent,
  };
}
