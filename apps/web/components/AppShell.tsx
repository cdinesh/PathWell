"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

const nav = [["⌂", "Home", "/dashboard"], ["◫", "Finance", "/finance"], ["◒", "Investments", "/investments"], ["↗", "Career", "/career"], ["◇", "Travel", "/travel"], ["◉", "Real-time News", "/news"], ["◎", "Goals", "/goals"], ["✦", "AI Advisor", "/advisor"], ["▱", "Documents", "/documents"], ["○", "Notifications", "/notifications"], ["⚙", "Settings", "/settings"]];

export function AppShell({ children }: { children: React.ReactNode }) {
  const path = usePathname(); const router = useRouter(); const [open, setOpen] = useState(false); const [accountOpen, setAccountOpen] = useState(false); const account = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function closeAccount(event: MouseEvent) {
      if (!account.current?.contains(event.target as Node)) setAccountOpen(false);
    }
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape") setAccountOpen(false);
    }
    document.addEventListener("mousedown", closeAccount);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("mousedown", closeAccount);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, []);

  function signOut() {
    localStorage.removeItem("pathwell_user_id");
    localStorage.removeItem("thrive_user_id");
    setAccountOpen(false);
    router.replace("/signup");
  }
  return <div className="shell">
    <aside className={open ? "sidebar open" : "sidebar"}><div className="logo"><span>✦</span> PathWell<small>One life. Many goals.<br/>One clear path.</small></div><button className="close" onClick={() => setOpen(false)}>×</button><nav>{nav.map(([icon, label, href]) => <Link key={href} href={href} onClick={() => setOpen(false)} className={path === href ? "active" : ""}><i>{icon}</i>{label}</Link>)}</nav><div className="side-foot"><div className="avatar">AM</div><div><b>Alex Morgan</b><small>Demo workspace</small></div></div></aside>
    <div className="main"><header className="topbar"><button className="menu" onClick={() => setOpen(true)}>☰</button><label className="search">⌕ <input aria-label="Global search" placeholder="Search goals, documents, plans…" /></label><Link className="quick" href="/advisor">✦ Ask PathWell</Link><button className="icon-button" aria-label="Notifications">◌<span/></button><div className="account-menu" ref={account}><button className="avatar account-trigger" aria-label="Open account menu" aria-expanded={accountOpen} aria-haspopup="menu" onClick={() => setAccountOpen(value => !value)}>AM</button>{accountOpen && <div className="account-dropdown" role="menu"><div><b>Alex Morgan</b><small>Demo workspace</small></div><button role="menuitem" onClick={signOut}>Sign out</button></div>}</div></header>{children}</div>
  </div>;
}
