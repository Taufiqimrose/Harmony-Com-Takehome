const API_BASE = import.meta.env.VITE_API_URL ?? "";

export async function createJob(file: File): Promise<{ job_id: string; sse_url: string }> {
  const body = new FormData();
  body.append("file", file);
  const res = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    body,
  });
  if (!res.ok) {
    throw new Error(`create job failed: ${res.status}`);
  }
  return res.json() as Promise<{ job_id: string; sse_url: string }>;
}

export async function confirmJob(
  jobId: string,
  payload: {
    extracted_overrides: Record<string, string>;
    buyer: Record<string, string | boolean>;
  },
): Promise<void> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error(`confirm failed: ${res.status}`);
  }
}

export function packetUrl(jobId: string): string {
  return `${API_BASE}/jobs/${jobId}/packet`;
}
