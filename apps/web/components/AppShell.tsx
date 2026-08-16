"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const nav = [["⌂", "Home", "/dashboard"], ["◫", "Finance", "/finance"], ["◒", "Investments", "/investments"], ["↗", "Career", "/career"], ["◇", "Travel", "/travel"], ["◉", "Real-time News", "/news"], ["◎", "Goals", "/goals"], ["✦", "AI Advisor", "/advisor"], ["▱", "Documents", "/documents"], ["○", "Notifications", "/notifications"], ["⚙", "Settings", "/settings"]];

export function AppShell({ children }: { children: React.ReactNode }) {
  const path = usePathname(); const [open, setOpen] = useState(false);
  return <div className="shell">
    <aside className={open ? "sidebar open" : "sidebar"}><div className="logo"><span>✦</span> PathWell<small>One life. Many goals.<br/>One clear path.</small></div><button className="close" onClick={() => setOpen(false)}>×</button><nav>{nav.map(([icon, label, href]) => <Link key={href} href={href} onClick={() => setOpen(false)} className={path === href ? "active" : ""}><i>{icon}</i>{label}</Link>)}</nav><div className="side-foot"><div className="avatar">AM</div><div><b>Alex Morgan</b><small>Demo workspace</small></div></div></aside>
    <div className="main"><header className="topbar"><button className="menu" onClick={() => setOpen(true)}>☰</button><label className="search">⌕ <input aria-label="Global search" placeholder="Search goals, documents, plans…" /></label><Link className="quick" href="/advisor">✦ Ask PathWell</Link><button className="icon-button" aria-label="Notifications">◌<span/></button><div className="avatar">AM</div></header>{children}</div>
  </div>;
}
