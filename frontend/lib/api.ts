export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws";

export type Room = { id: string; name: string; created_at: string };
export type Message = {
  id: string;
  room_id: string;
  username: string;
  content: string;
  client_message_id: string;
  sequence_number: number;
  status: string;
  retry_count: number;
  failure_reason?: string | null;
  delivery_latency_ms?: number | null;
  created_at: string;
};

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail?.message ?? body.detail ?? response.statusText);
  }
  return response.json();
}
