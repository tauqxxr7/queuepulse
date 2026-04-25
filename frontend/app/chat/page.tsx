"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Send, Wifi } from "lucide-react";
import { api, Message, Room, WS_URL } from "@/lib/api";

export default function ChatPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [roomId, setRoomId] = useState("");
  const [username, setUsername] = useState("demo-user");
  const [content, setContent] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState("");
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    api<Room[]>("/api/rooms")
      .then(async (existing) => {
        if (existing.length) return existing;
        const created = await api<Room>("/api/rooms", { method: "POST", body: JSON.stringify({ name: "general" }) });
        return [created];
      })
      .then((data) => {
        setRooms(data);
        setRoomId(data[0]?.id ?? "");
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!roomId) return;
    api<Message[]>(`/api/messages/${roomId}`).then(setMessages).catch((err) => setError(err.message));
    socketRef.current?.close();
    const socket = new WebSocket(`${WS_URL}/${roomId}/${encodeURIComponent(username)}`);
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === "message.delivered") {
        setMessages((current) => {
          const without = current.filter((message) => message.id !== payload.message.id);
          return [...without, payload.message].sort((a, b) => a.sequence_number - b.sequence_number);
        });
      }
      if (payload.type === "message.status") {
        setMessages((current) => current.map((message) => message.id === payload.message_id ? { ...message, status: payload.status, retry_count: payload.retry_count ?? message.retry_count } : message));
      }
    };
    socketRef.current = socket;
    return () => socket.close();
  }, [roomId, username]);

  const currentRoom = useMemo(() => rooms.find((room) => room.id === roomId), [rooms, roomId]);

  async function sendMessage(event: FormEvent) {
    event.preventDefault();
    if (!content.trim() || !roomId) return;
    setError("");
    try {
      const message = await api<Message>("/api/messages", {
        method: "POST",
        body: JSON.stringify({ room_id: roomId, username, content, client_message_id: crypto.randomUUID() }),
      });
      setMessages((current) => [...current.filter((item) => item.id !== message.id), message].sort((a, b) => a.sequence_number - b.sequence_number));
      setContent("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to send message");
    }
  }

  return (
    <main className="mx-auto grid max-w-7xl gap-5 px-5 py-8 lg:grid-cols-[280px_1fr]">
      <aside className="surface rounded-lg p-5">
        <h1 className="mb-5 text-xl font-semibold text-white">Realtime Chat</h1>
        <label className="text-sm text-slate-400">User</label>
        <input value={username} onChange={(event) => setUsername(event.target.value)} className="mt-2 w-full rounded-md border border-white/10 bg-ink px-3 py-2 text-white outline-none focus:border-mint" />
        <label className="mt-5 block text-sm text-slate-400">Room</label>
        <select value={roomId} onChange={(event) => setRoomId(event.target.value)} className="mt-2 w-full rounded-md border border-white/10 bg-ink px-3 py-2 text-white outline-none focus:border-mint">
          {rooms.map((room) => <option key={room.id} value={room.id}>{room.name}</option>)}
        </select>
        <div className="mt-5 flex items-center gap-2 text-sm text-mint"><Wifi size={16} /> Live WebSocket session</div>
      </aside>
      <section className="surface flex min-h-[70vh] flex-col rounded-lg">
        <div className="border-b border-white/10 p-5">
          <h2 className="text-lg font-semibold text-white">{currentRoom?.name ?? "Room"}</h2>
          <p className="text-sm text-slate-400">Messages are queued, persisted, delivered, and updated in real time.</p>
        </div>
        <div className="flex-1 space-y-3 overflow-auto p-5">
          {messages.map((message) => (
            <div key={message.id} className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <span className="font-medium text-white">#{message.sequence_number} {message.username}</span>
                <span className="rounded-md bg-white/10 px-2 py-1 text-xs text-mint">{message.status}</span>
              </div>
              <p className="mt-2 text-slate-200">{message.content}</p>
              {message.failure_reason && <p className="mt-2 text-sm text-coral">{message.failure_reason}</p>}
            </div>
          ))}
        </div>
        <form onSubmit={sendMessage} className="border-t border-white/10 p-5">
          {error && <p className="mb-3 rounded-md border border-coral/30 bg-coral/10 px-3 py-2 text-sm text-coral">{error}</p>}
          <div className="flex gap-3">
            <input value={content} onChange={(event) => setContent(event.target.value)} placeholder="Send a message through the queue..." className="min-w-0 flex-1 rounded-md border border-white/10 bg-ink px-4 py-3 text-white outline-none focus:border-mint" />
            <button className="inline-flex items-center gap-2 rounded-md bg-mint px-4 py-3 font-semibold text-ink"><Send size={18} /> Send</button>
          </div>
        </form>
      </section>
    </main>
  );
}
