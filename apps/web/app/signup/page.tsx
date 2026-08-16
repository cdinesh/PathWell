"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import { signupSchema } from "../../lib/validation";

export default function SignupPage() {
  const router = useRouter(); const [show, setShow] = useState(false); const [loading, setLoading] = useState(false); const [errors, setErrors] = useState<Record<string, string>>({}); const [serverError, setServerError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setServerError(""); const form = new FormData(event.currentTarget); const data = Object.fromEntries(form); const parsed = signupSchema.safeParse({ ...data, terms_accepted: form.get("terms_accepted") === "on" });
    if (!parsed.success) { setErrors(Object.fromEntries(parsed.error.issues.map(issue => [String(issue.path[0]), issue.message]))); return; }
    setErrors({}); setLoading(true);
    try { const result = await api<{user_id:string}>("/auth/register", { method: "POST", body: JSON.stringify(parsed.data) }); localStorage.setItem("pathwell_user_id", result.user_id); router.push("/onboarding"); } catch (error) { setServerError(error instanceof Error ? error.message : "Registration failed"); } finally { setLoading(false); }
  }
  return <main className="auth-page"><section className="auth-brand"><div className="logo"><span>✦</span> PathWell<small>One life. Many goals. One clear path.</small></div><div><p className="eyebrow light">YOUR LIFE, IN FOCUS</p><h1>Build wealth.<br/>Grow with purpose.<br/>Live fully.</h1><p>One intelligent workspace for the decisions that shape your life.</p></div><blockquote>“Clarity comes from seeing the whole picture.”</blockquote></section><section className="auth-form"><div className="form-wrap"><p className="eyebrow">CREATE YOUR WORKSPACE</p><h2>Find your path forward</h2><p>Set up your secure personal intelligence workspace.</p><form onSubmit={submit} noValidate><div className="field-grid"><Field name="full_name" label="Full name" placeholder="Alex Morgan" error={errors.full_name}/><Field name="email" label="Email" type="email" placeholder="alex@example.com" error={errors.email}/><Field name="phone" label="Phone number" placeholder="+1 303 555 0147" error={errors.phone}/><Field name="date_of_birth" label="Date of birth" type="date" error={errors.date_of_birth}/><Field name="password" label="Password" type={show ? "text" : "password"} error={errors.password}/><Field name="confirm" label="Confirm password" type={show ? "text" : "password"} error={errors.confirm}/></div><label className="check"><input type="checkbox" onChange={() => setShow(v => !v)}/> Show passwords</label><label className="check"><input name="terms_accepted" type="checkbox"/> I agree to the <a href="#terms">Terms of Service</a> and <a href="#privacy">Privacy Policy</a>.</label>{errors.terms_accepted && <p className="field-error">{errors.terms_accepted}</p>}{serverError && <p className="error-box">{serverError}</p>}<button className="primary wide" disabled={loading}>{loading ? "Creating your workspace…" : "Create account →"}</button></form><div className="or"><span/>or<span/></div><button className="secondary wide" onClick={() => router.push("/dashboard")}>Use demo account</button><p className="secure">⌾ Passwords are securely hashed. PathWell never stores bank credentials.</p></div></section></main>;
}

function Field({ name, label, type = "text", placeholder, error }: { name: string; label: string; type?: string; placeholder?: string; error?: string }) { return <label className="field"><span>{label}</span><input name={name} type={type} placeholder={placeholder}/>{error && <small>{error}</small>}</label>; }
