import Link from "next/link";

export function MetricCard({ label, value, detail }: { label: string; value: string; detail: string }) { return <article className="metric"><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>; }

export function GoalCard({ title, category, current, target, color }: { title: string; category: string; current: number; target: number; color: string }) {
  const progress = Math.min(Math.round(current / target * 100), 100);
  return <article className="goal-card"><div className="goal-head"><span className={`goal-icon ${color}`}>◎</span><small>{category}</small><b>{progress}%</b></div><h3>{title}</h3><div className="progress"><span style={{ width: `${progress}%` }} /></div><p>${current.toLocaleString()} <span>of ${target.toLocaleString()}</span></p></article>;
}

export function PageHeader({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: React.ReactNode }) { return <header className="page-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{description}</p></div>{action}</header>; }

export function AdvisorStrip({ prompt }: { prompt: string }) { return <section className="advisor-strip"><div className="spark">✦</div><div><small>ASK THRIVEOS</small><h3>{prompt}</h3></div><Link href={`/advisor?prompt=${encodeURIComponent(prompt)}`}>Ask advisor →</Link></section>; }
