export const dashboard = {
  user: { name: "Alex Morgan", role: "Senior Financial Analyst" },
  metrics: [
    { label: "Net worth", value: "$77,900", change: "+4.2% this quarter" },
    { label: "Monthly income", value: "$6,700", change: "Take-home" },
    { label: "Monthly spending", value: "$5,050", change: "$210 below plan" },
    { label: "Savings rate", value: "25%", change: "$1,650 this month" },
  ],
  goals: [
    { title: "Emergency Fund", category: "Finance", current: 17500, target: 25000, color: "green" },
    { title: "House Down Payment", category: "Finance", current: 28500, target: 80000, color: "blue" },
    { title: "Italy Trip", category: "Travel", current: 600, target: 3000, color: "gold" },
    { title: "AI Product Manager", category: "Career", current: 35, target: 100, color: "violet" },
  ],
  holdings: [{ ticker: "VOO", allocation: 28 }, { ticker: "QQQ", allocation: 19 }, { ticker: "MSFT", allocation: 16 }, { ticker: "NVDA", allocation: 14 }, { ticker: "BND", allocation: 12 }, { ticker: "AAPL", allocation: 11 }],
};

export const sectionContent: Record<string, { title: string; eyebrow: string; description: string; metrics: { label: string; value: string; detail: string }[]; prompt: string }> = {
  finance: { title: "Finance", eyebrow: "YOUR MONEY", description: "See cash flow, progress, and the decisions that matter next.", metrics: [{ label: "Available cash", value: "$25,900", detail: "Checking + savings" }, { label: "Debt", value: "$16,000", detail: "$14,800 student loan" }, { label: "Monthly capacity", value: "$1,650", detail: "After recurring spending" }], prompt: "Where did I overspend this month?" },
  investments: { title: "Investments", eyebrow: "PORTFOLIO INTELLIGENCE", description: "Understand allocation, concentration, and goal alignment.", metrics: [{ label: "Portfolio value", value: "$68,000", detail: "+0.74% seeded daily change" }, { label: "Equity allocation", value: "88%", detail: "12% bonds" }, { label: "Top risk", value: "60%", detail: "Technology exposure" }], prompt: "Explain my biggest portfolio risk." },
  career: { title: "Career", eyebrow: "GROWTH PLAN", description: "Turn your AI Product Manager ambition into evidence and momentum.", metrics: [{ label: "Goal progress", value: "35%", detail: "AI Product Manager" }, { label: "Next skill", value: "AI product evals", detail: "Highest-leverage gap" }, { label: "Role matches", value: "2", detail: "Mock opportunities" }], prompt: "What should I learn next?" },
  travel: { title: "Travel", eyebrow: "TRIP INTELLIGENCE", description: "Plan meaningful travel without losing sight of other goals.", metrics: [{ label: "Upcoming", value: "Italy", detail: "May 8–16, 2027" }, { label: "Trip budget", value: "$3,000", detail: "$600 saved" }, { label: "Funding gap", value: "$2,400", detail: "$600/month for 4 months" }], prompt: "Make my Italy trip $500 cheaper." },
  notifications: { title: "Notifications", eyebrow: "IMPORTANT CHANGES", description: "Only high-signal alerts, on your terms.", metrics: [{ label: "Goal alert", value: "On track", detail: "Emergency fund" }, { label: "Portfolio", value: "Review", detail: "Technology concentration" }, { label: "Career", value: "2 roles", detail: "New mock matches" }], prompt: "What changed this week?" },
  settings: { title: "Settings", eyebrow: "CONTROL CENTER", description: "Manage profile, privacy, memories, and notification preferences.", metrics: [{ label: "Memory", value: "Enabled", detail: "Structured profile only" }, { label: "Integrations", value: "Mock", detail: "No external accounts connected" }, { label: "Quiet hours", value: "9 PM–7 AM", detail: "Important alerts only" }], prompt: "Show what you remember about me." },
};
