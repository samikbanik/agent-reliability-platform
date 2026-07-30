"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react";

import {
  createJob,
  getJob,
  listJobs,
  type Job,
  type JobSummary,
} from "../lib/api";

const DEFAULT_GOAL =
  "Analyze the UK EV charging market, compare leading operators, and produce a 2-page investment brief.";

const TERMINAL = new Set(["completed", "failed"]);

export default function Home() {
  const [goal, setGoal] = useState(DEFAULT_GOAL);
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [selected, setSelected] = useState<Job | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshList = useCallback(async () => {
    const items = await listJobs();
    setJobs(items);
  }, []);

  const loadJob = useCallback(async (jobId: string) => {
    const job = await getJob(jobId);
    setSelected(job);
    return job;
  }, []);

  useEffect(() => {
    refreshList().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : "Failed to load jobs");
    });
  }, [refreshList]);

  useEffect(() => {
    if (!selected || TERMINAL.has(selected.status)) {
      return;
    }
    const timer = window.setInterval(() => {
      loadJob(selected.id)
        .then(() => refreshList())
        .catch((err: unknown) => {
          setError(
            err instanceof Error ? err.message : "Failed to refresh job",
          );
        });
    }, 1500);
    return () => window.clearInterval(timer);
  }, [selected, loadJob, refreshList]);

  const statusClass = useMemo(() => {
    if (!selected) {
      return "";
    }
    if (selected.status === "completed") {
      return "status-ok";
    }
    if (selected.status === "failed") {
      return "status-bad";
    }
    return "";
  }, [selected]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const job = await createJob(goal.trim());
      setSelected(job);
      await refreshList();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create job");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <section className="hero">
        <h1>Agent Reliability Platform</h1>
        <p>
          Submit a research goal. The platform plans, researches, synthesizes,
          and verifies the result through async workers backed by Postgres and
          RabbitMQ.
        </p>
      </section>

      <section className="panel">
        <form onSubmit={onSubmit}>
          <label htmlFor="goal">Research goal</label>
          <textarea
            id="goal"
            value={goal}
            onChange={(event) => setGoal(event.target.value)}
            required
            minLength={8}
          />
          <div className="actions">
            <button type="submit" disabled={busy || goal.trim().length < 8}>
              {busy ? "Submitting..." : "Start research job"}
            </button>
            <button
              type="button"
              className="secondary"
              onClick={() => {
                refreshList().catch((err: unknown) => {
                  setError(
                    err instanceof Error ? err.message : "Failed to refresh",
                  );
                });
              }}
            >
              Refresh jobs
            </button>
          </div>
        </form>
        {error ? <p className="error">{error}</p> : null}
      </section>

      <section className="panel">
        <h2>Recent jobs</h2>
        {jobs.length === 0 ? (
          <p className="muted">No jobs yet.</p>
        ) : (
          <div className="job-list">
            {jobs.map((job) => (
              <button
                key={job.id}
                type="button"
                onClick={() => {
                  loadJob(job.id).catch((err: unknown) => {
                    setError(
                      err instanceof Error ? err.message : "Failed to load job",
                    );
                  });
                }}
              >
                <strong>{job.status}</strong>
                <span className="muted">{job.goal}</span>
              </button>
            ))}
          </div>
        )}
      </section>

      {selected ? (
        <section className="panel">
          <h2>Job detail</h2>
          <div className="meta">
            <div>
              <span>Status</span>
              <strong className={statusClass}>{selected.status}</strong>
            </div>
            <div>
              <span>Job ID</span>
              <strong>{selected.id}</strong>
            </div>
            <div>
              <span>Updated</span>
              <strong>{new Date(selected.updated_at).toLocaleString()}</strong>
            </div>
          </div>

          {selected.error_message ? (
            <p className="error">{selected.error_message}</p>
          ) : null}

          <h3>Steps</h3>
          <ul className="steps">
            {selected.steps.map((step) => (
              <li key={step.id}>
                <strong>{step.role}</strong>
                <div>
                  <div>{step.status}</div>
                  {step.error_message ? (
                    <div className="error">{step.error_message}</div>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>

          {selected.final_report ? (
            <>
              <h3>Final report</h3>
              <pre className="report">{selected.final_report}</pre>
            </>
          ) : null}
        </section>
      ) : null}
    </main>
  );
}
