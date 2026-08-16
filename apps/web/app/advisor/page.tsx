"use client";

import { FormEvent, useEffect, useState } from "react";

import { AppShell } from "../../components/AppShell";
import { PageHeader } from "../../components/Cards";
import { api } from "../../lib/api";

type Result = {
  activities: string[];
  tasks: { agent: string; status: string }[];
  result: {
    summary: string;
    what_i_found: string[];
    recommendation: string;
    trade_offs: string[];
    next_steps: string[];
    assumptions: string[];
    alternatives: {
      label: string;
      budget?: number;
      estimated_delay_months?: number;
      funding?: string;
    }[];
    confidence: number;
    disclaimer: string;
  };
};

const demoPrompt =
  "Can I afford a $3,000 trip to Italy this year without delaying my emergency-fund goal?";

export default function Advisor() {
  const [message, setMessage] = useState(demoPrompt);
  const [loading, setLoading] = useState(false);
  const [activity, setActivity] = useState(0);
  const [response, setResponse] = useState<Result | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const prompt = new URLSearchParams(window.location.search).get("prompt");
    if (prompt) setMessage(prompt);
  }, []);

  useEffect(() => {
    if (!loading) return;
    const timer = setInterval(() => setActivity((value) => Math.min(value + 1, 4)), 450);
    return () => clearInterval(timer);
  }, [loading]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setActivity(0);
    setError("");
    setResponse(null);
    try {
      setResponse(
        await api<Result>("/ai/chat", {
          method: "POST",
          body: JSON.stringify({ message }),
        }),
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Advisor unavailable");
    } finally {
      setLoading(false);
    }
  }

  const preview = activityPreview(message);
  const activities = response?.activities ?? preview.activities;

  return (
    <AppShell>
      <main className="page advisor-page">
        <PageHeader
          eyebrow="CROSS-DOMAIN INTELLIGENCE"
          title="AI Advisor"
          description="Ask about money, investing, career, travel—or how they affect each other."
        />
        <section className="advisor-workspace">
          <div className="conversation">
            <div className="welcome">
              <span className="spark">✦</span>
              <h2>What can we work through?</h2>
              <p>I’ll coordinate only the agents and data needed, then show assumptions and trade-offs.</p>
            </div>
            {response && (
              <div className="answer">
                <p className="eyebrow">SUMMARY</p>
                <h2>{response.result.summary}</h2>
                <ResultSection title="What I found" items={response.result.what_i_found} />
                <div className="recommendation">
                  <p className="eyebrow">RECOMMENDATION</p>
                  <p>{response.result.recommendation}</p>
                </div>
                <h3>Options</h3>
                <div className="scenarios">
                  {response.result.alternatives.map((option) => (
                    <article key={option.label}>
                      <b>{option.label}</b>
                      <strong>
                        {option.budget ? `$${option.budget.toLocaleString()}` : option.funding}
                      </strong>
                      {option.estimated_delay_months !== undefined && (
                        <small>~{option.estimated_delay_months} month goal delay</small>
                      )}
                    </article>
                  ))}
                </div>
                <ResultSection title="Trade-offs" items={response.result.trade_offs} />
                <ResultSection title="Next steps" items={response.result.next_steps} />
                <details>
                  <summary>
                    Assumptions · {Math.round(response.result.confidence * 100)}% confidence
                  </summary>
                  {response.result.assumptions.map((assumption) => (
                    <p key={assumption}>{assumption}</p>
                  ))}
                </details>
                <p className="disclaimer">{response.result.disclaimer}</p>
              </div>
            )}
            {error && <div className="error-box">{error}. Start the FastAPI server on port 8000.</div>}
          </div>
          <aside className="agent-panel">
            <p className="eyebrow">AGENT ACTIVITY</p>
            {activities.map((item, index) => (
              <div className={response || activity >= index ? "activity done" : "activity"} key={item}>
                <span>{response || activity > index ? "✓" : activity === index && loading ? "⋯" : "○"}</span>
                {item}
              </div>
            ))}
            <hr />
            <small>Approval level</small>
            <p><b>Level 0 · Read only</b><br />No money, bookings, or messages can be sent.</p>
          </aside>
        </section>
        <form className="composer" onSubmit={submit}>
          <textarea aria-label="Ask PathWell" value={message} onChange={(event) => setMessage(event.target.value)} />
          <div>
            <span>{preview.context}</span>
            <button className="primary" disabled={loading || message.length < 3}>
              {loading ? "Agents working…" : "Send →"}
            </button>
          </div>
        </form>
      </main>
    </AppShell>
  );
}

function ResultSection({ title, items }: { title: string; items: string[] }) {
  return <section className="result-section"><h3>{title}</h3>{items.map((item) => <p key={item}><span>•</span>{item}</p>)}</section>;
}

function activityPreview(message: string) {
  const text = message.toLowerCase();
  if (["career", "learn", "skill", "resume", "job", "interview", "product manager"].some((word) => text.includes(word))) {
    return { context: "Career profile context available", activities: ["Reviewing your career goal", "Mapping your existing strengths", "Identifying the highest-value skill gap", "Building a focused learning sequence", "Preparing your next actions"] };
  }
  if (["portfolio", "stock", "invest", "etf", "allocation"].some((word) => text.includes(word))) {
    return { context: "Investment profile context available", activities: ["Reviewing your portfolio", "Checking allocation", "Evaluating concentration", "Comparing risk factors", "Preparing research guidance"] };
  }
  if (["trip", "travel", "flight", "hotel", "italy"].some((word) => text.includes(word))) {
    return { context: "Finance + Travel context available", activities: ["Reviewing your financial goals", "Estimating a trip budget", "Comparing scenarios", "Evaluating goal impact", "Preparing your recommendation"] };
  }
  return { context: "Personalized profile context available", activities: ["Understanding your request", "Reviewing your profile", "Selecting relevant context", "Building a plan", "Preparing next steps"] };
}
