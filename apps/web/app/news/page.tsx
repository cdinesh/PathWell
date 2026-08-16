"use client";

import { useCallback, useEffect, useState } from "react";
import { AppShell } from "../../components/AppShell";
import { PageHeader } from "../../components/Cards";
import { api } from "../../lib/api";

const categories = ["breaking", "ai", "technology", "health", "business", "finance", "politics"] as const;
type Category = (typeof categories)[number];
type Article = { title: string; description?: string; url: string; image_url?: string; source: string; published_at?: string };
type Feed = { category: Category; retrieved_at: string; articles: Article[] };

export default function NewsPage() {
  const [category, setCategory] = useState<Category>("breaking");
  const [feed, setFeed] = useState<Feed | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const load = useCallback(async () => { setLoading(true); setError(""); try { setFeed(await api<Feed>(`/news/headlines?category=${category}`)); } catch (caught) { setFeed(null); setError(caught instanceof Error ? caught.message : "Unable to retrieve news"); } finally { setLoading(false); } }, [category]);
  useEffect(() => { void load(); }, [load]);
  return <AppShell><main className="page"><PageHeader eyebrow="LIVE INTELLIGENCE" title="Real-time News" description="Choose the topics that matter to you. Headlines come directly from the configured provider and include source and publication time." action={<button className="secondary" onClick={load} disabled={loading}>↻ Refresh</button>}/><div className="news-tabs" role="tablist" aria-label="News categories">{categories.map(item => <button role="tab" aria-selected={category === item} className={category === item ? "active" : ""} key={item} onClick={() => setCategory(item)}>{item === "ai" ? "AI" : item[0].toUpperCase() + item.slice(1)}</button>)}</div>{loading && <section className="news-grid" aria-label="Loading headlines">{Array.from({length:6}).map((_, index) => <article className="news-card skeleton" key={index}><div/><span/><span/><span/></article>)}</section>}{error && <section className="news-error"><h2>Real-time news isn’t available yet</h2><p>{error}</p><code>NEWS_API_KEY=your_key_here</code><p>Add the key to <code>.env</code>, restart the API, and try again. PathWell will not display invented or stale fallback headlines.</p><button className="primary" onClick={load}>Try again</button></section>}{feed && !loading && <><div className="news-meta"><span>● Live provider</span><span>Retrieved {new Date(feed.retrieved_at).toLocaleString()}</span><span>{feed.articles.length} headlines</span></div>{feed.articles.length ? <section className="news-grid">{feed.articles.map(article => <a className="news-card" href={article.url} target="_blank" rel="noopener noreferrer" key={`${article.url}-${article.title}`}><div className="news-image">{article.image_url ? <img src={article.image_url} alt=""/> : <span>PATHWELL NEWS</span>}</div><div className="news-body"><div><b>{article.source}</b><time>{article.published_at ? new Date(article.published_at).toLocaleString() : "Time unavailable"}</time></div><h2>{article.title}</h2>{article.description && <p>{article.description}</p>}<span className="read">Read original story ↗</span></div></a>)}</section> : <section className="news-error"><h2>No current headlines found</h2><p>Try another category or refresh later.</p></section>}</>}</main></AppShell>;
}
