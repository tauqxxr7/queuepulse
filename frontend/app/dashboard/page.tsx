"use client";

import { useEffect, useState } from "react";
import { Activity, AlertTriangle, Gauge, Pause, Play, RefreshCcw, Zap } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, Room } from "@/lib/api";

type Metrics = {
  total_messages: number;
  messages_per_second: number;
  queue_depth: number;
  retry_queue_count: number;
  dead_letter_count: number;
  active_users: number;
  active_rooms: number;
  success_rate: number;
  average_delivery_latency_ms: number;
  failure_rate: number;
  recent_failed_messages: Array<{ id: string; status: string; retry_count: number; failure_reason?: string }>;
  throughput_series: Array<{ time: string; messages: number }>;
  latency_series: Array<{ time: string; latency_ms: number }>;
  queue_depth_series: Array<{ time: string; queue_depth: number }>;
  success_failed: Array<{ name: string; value: number }>;
};

const statKeys: Array<[keyof Metrics, string, LucideIcon]> = [
  ["total_messages", "Total messages", Activity],
  ["messages_per_second", "Messages/sec", Zap],
  ["queue_depth", "Queue depth", Gauge],
  ["retry_queue_count", "Retries", RefreshCcw],
  ["dead_letter_count", "Dead letters", AlertTriangle],
  ["success_rate", "Success rate", Play],
];

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [insights, setInsights] = useState<string[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [failureRate, setFailureRate] = useState(0);
  const [workerDelayMs, setWorkerDelayMs] = useState(100);

  async function refresh() {
    const [metricData, insightData, roomData] = await Promise.all([
      api<Metrics>("/api/metrics"),
      api<{ insights: string[] }>("/api/insights"),
      api<Room[]>("/api/rooms"),
    ]);
    setMetrics(metricData);
    setInsights(insightData.insights);
    setRooms(roomData);
  }

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 2500);
    return () => clearInterval(id);
  }, []);

  async function updateFailure() {
    await api("/api/simulate/failure-rate", { method: "POST", body: JSON.stringify({ failure_rate: failureRate }) });
    await refresh();
  }

  async function updateDelay() {
    await api("/api/simulate/worker-delay", { method: "POST", body: JSON.stringify({ worker_delay_ms: workerDelayMs }) });
    await refresh();
  }

  async function spike() {
    const room = rooms[0] ?? await api<Room>("/api/rooms", { method: "POST", body: JSON.stringify({ name: "dashboard-demo" }) });
    await api("/api/simulate/load-spike", { method: "POST", body: JSON.stringify({ room_id: room.id, messages: 100 }) });
    await refresh();
  }

  if (!metrics) return <main className="mx-auto max-w-7xl px-5 py-10 text-slate-300">Loading dashboard...</main>;

  return (
    <main className="mx-auto max-w-7xl space-y-5 px-5 py-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold text-white">Observability Dashboard</h1>
          <p className="mt-2 text-slate-400">Live view of queue pressure, retries, DLQ, latency, and delivery health.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button onClick={() => api("/api/simulate/consumer-pause", { method: "POST" })} className="inline-flex items-center gap-2 rounded-md border border-white/10 px-3 py-2 text-sm text-white hover:bg-white/10"><Pause size={16} /> Pause</button>
          <button onClick={() => api("/api/simulate/consumer-resume", { method: "POST" })} className="inline-flex items-center gap-2 rounded-md border border-white/10 px-3 py-2 text-sm text-white hover:bg-white/10"><Play size={16} /> Resume</button>
          <button onClick={spike} className="inline-flex items-center gap-2 rounded-md bg-amber px-3 py-2 text-sm font-semibold text-ink"><Zap size={16} /> Spike</button>
        </div>
      </div>

      <section className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
        {statKeys.map(([key, label, Icon]) => (
          <div key={key} className="surface rounded-lg p-4">
            <Icon className="mb-3 text-mint" size={19} />
            <p className="text-sm text-slate-400">{label}</p>
            <p className="mt-2 text-2xl font-semibold text-white">{String(metrics[key])}</p>
          </div>
        ))}
      </section>

      <section className="grid gap-5 lg:grid-cols-2">
        <Chart title="Throughput">
          <AreaChart data={metrics.throughput_series}><CartesianGrid stroke="#24343d" /><XAxis dataKey="time" /><YAxis /><Tooltip /><Area type="monotone" dataKey="messages" stroke="#5eead4" fill="#5eead433" /></AreaChart>
        </Chart>
        <Chart title="Delivery latency">
          <LineChart data={metrics.latency_series}><CartesianGrid stroke="#24343d" /><XAxis dataKey="time" /><YAxis /><Tooltip /><Line type="monotone" dataKey="latency_ms" stroke="#fbbf24" strokeWidth={2} /></LineChart>
        </Chart>
        <Chart title="Queue depth">
          <AreaChart data={metrics.queue_depth_series}><CartesianGrid stroke="#24343d" /><XAxis dataKey="time" /><YAxis /><Tooltip /><Area type="monotone" dataKey="queue_depth" stroke="#fb7185" fill="#fb718533" /></AreaChart>
        </Chart>
        <Chart title="Success vs failed">
          <BarChart data={metrics.success_failed}><CartesianGrid stroke="#24343d" /><XAxis dataKey="name" /><YAxis /><Tooltip /><Bar dataKey="value" fill="#5eead4" /></BarChart>
        </Chart>
      </section>

      <section className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="surface rounded-lg p-5">
          <h2 className="font-semibold text-white">Failure simulation</h2>
          <input type="range" min="0" max="100" value={failureRate} onChange={(event) => setFailureRate(Number(event.target.value))} className="mt-5 w-full" />
          <div className="mt-3 flex items-center justify-between text-sm text-slate-300"><span>{failureRate}% failure rate</span><button onClick={updateFailure} className="rounded-md bg-mint px-3 py-2 font-semibold text-ink">Apply</button></div>
          <input type="range" min="0" max="3000" step="100" value={workerDelayMs} onChange={(event) => setWorkerDelayMs(Number(event.target.value))} className="mt-6 w-full" />
          <div className="mt-3 flex items-center justify-between text-sm text-slate-300"><span>{workerDelayMs}ms worker delay</span><button onClick={updateDelay} className="rounded-md border border-white/15 px-3 py-2 font-semibold text-white hover:bg-white/10">Apply</button></div>
        </div>
        <div className="surface rounded-lg p-5">
          <h2 className="font-semibold text-white">AI operational insights</h2>
          <div className="mt-4 space-y-3">
            {insights.map((insight) => <p key={insight} className="rounded-md border border-white/10 bg-white/[0.03] p-3 text-slate-200">{insight}</p>)}
          </div>
        </div>
      </section>
    </main>
  );
}

function Chart({ title, children }: { title: string; children: React.ReactElement }) {
  return (
    <div className="surface rounded-lg p-5">
      <h2 className="mb-4 font-semibold text-white">{title}</h2>
      <div className="h-72"><ResponsiveContainer width="100%" height="100%">{children}</ResponsiveContainer></div>
    </div>
  );
}
