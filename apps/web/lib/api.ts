const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, { ...options, headers: { "content-type": "application/json", ...(options?.headers ?? {}) } });
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail ?? `Request failed (${response.status})`); }
  return response.json();
}
