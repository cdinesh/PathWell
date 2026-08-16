"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";

const steps = ["Financial", "Investing", "Career", "Lifestyle"];
export default function Onboarding() {
  const router = useRouter(); const [step, setStep] = useState(0); const [saving, setSaving] = useState(false); const [data, setData] = useState<Record<string, string>>({});
  const fields = [
    [["income", "Annual income", "112000"], ["monthly_take_home", "Monthly take-home", "6700"], ["savings", "Current savings", "17500"], ["financial_goal", "Primary financial goal", "Build a six-month emergency fund"]],
    [["investment_experience", "Experience", "Intermediate"], ["risk_tolerance", "Risk tolerance", "Moderate"], ["investment_horizon", "Time horizon", "5–10 years"]],
    [["current_role", "Current role", "Senior Financial Analyst"], ["desired_role", "Desired role", "AI Product Manager"], ["skills", "Skills", "Financial analysis, SQL, strategy"]],
    [["travel_style", "Travel style", "Comfortable budget"], ["travel_interests", "Travel interests", "International, food, culture"]],
  ];
  async function finish() { setSaving(true); const user = localStorage.getItem("pathwell_user_id") ?? localStorage.getItem("thrive_user_id"); const payload = { ...data, income: Number(data.income) || undefined, monthly_take_home: Number(data.monthly_take_home) || undefined, savings: Number(data.savings) || undefined, skills: data.skills?.split(",").map(x => x.trim()) ?? [], travel_interests: data.travel_interests?.split(",").map(x => x.trim()) ?? [] }; try { if (user) await api("/me/profile", { method: "PATCH", headers: { "x-user-id": user }, body: JSON.stringify(payload) }); router.push("/dashboard"); } finally { setSaving(false); } }
  return <main className="onboarding"><div className="logo"><span>✦</span> PathWell</div><section><div className="stepper">{steps.map((label, index) => <div className={index <= step ? "done" : ""} key={label}><span>{index + 1}</span><small>{label}</small></div>)}</div><p className="eyebrow">STEP {step + 1} OF 4</p><h1>{steps[step]} profile</h1><p>Share what is useful now. Every field is optional and editable later.</p><div className="onboarding-grid">{fields[step].map(([name, label, placeholder]) => <label className="field" key={name}><span>{label}</span><input value={data[name] ?? ""} placeholder={placeholder} onChange={e => setData({ ...data, [name]: e.target.value })}/></label>)}</div><div className="form-actions"><button className="ghost" onClick={() => step ? setStep(step - 1) : router.push("/dashboard")}>{step ? "← Back" : "Skip onboarding"}</button>{step < 3 ? <button className="primary" onClick={() => setStep(step + 1)}>Continue →</button> : <button className="primary" disabled={saving} onClick={finish}>{saving ? "Saving…" : "Finish →"}</button>}</div></section></main>;
}
