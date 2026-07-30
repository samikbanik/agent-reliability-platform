export type Step = {
  id: string;
  role: string;
  status: string;
  position: number;
  error_message: string | null;
  output_payload: Record<string, unknown>;
  started_at: string | null;
  completed_at: string | null;
};

export type Artifact = {
  id: string;
  kind: string;
  storage_path: string;
  content_type: string;
};

export type Job = {
  id: string;
  goal: string;
  status: string;
  error_message: string | null;
  final_report: string | null;
  created_at: string;
  updated_at: string;
  steps: Step[];
  artifacts: Artifact[];
};

export type JobSummary = {
  id: string;
  goal: string;
  status: string;
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function createJob(goal: string): Promise<Job> {
  return request<Job>("/jobs", {
    method: "POST",
    body: JSON.stringify({ goal }),
  });
}

export function listJobs(): Promise<JobSummary[]> {
  return request<JobSummary[]>("/jobs");
}

export function getJob(jobId: string): Promise<Job> {
  return request<Job>(`/jobs/${jobId}`);
}
