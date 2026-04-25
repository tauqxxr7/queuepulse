import Link from "next/link";
import { ArrowRight, Database, Gauge, RefreshCcw, ShieldCheck, Workflow, Zap } from "lucide-react";
import type { LucideIcon } from "lucide-react";

const features: Array<[string, LucideIcon]> = [
  ["At-least-once delivery", ShieldCheck],
  ["RabbitMQ retries and DLQ", RefreshCcw],
  ["PostgreSQL persistence", Database],
  ["Redis rate limiting", Zap],
  ["Live WebSocket fanout", Workflow],
  ["Operational dashboard", Gauge],
];

export default function Home() {
  return (
    <main>
      <section className="mx-auto grid min-h-[calc(100vh-73px)] max-w-7xl content-center gap-12 px-5 py-12 lg:grid-cols-[1fr_0.9fr]">
        <div className="flex flex-col justify-center">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.28em] text-mint">Distributed messaging simulator</p>
          <h1 className="max-w-4xl text-5xl font-semibold leading-tight text-white md:text-7xl">
            QueuePulse
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-300">
            A production-grade real-time messaging system that shows how WebSocket traffic moves through queues,
            workers, persistence, retries, dead-letter handling, and live operational analytics.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link href="/dashboard" className="inline-flex items-center gap-2 rounded-md bg-mint px-5 py-3 font-semibold text-ink">
              Open dashboard <ArrowRight size={18} />
            </Link>
            <Link href="/chat" className="inline-flex items-center gap-2 rounded-md border border-white/15 px-5 py-3 font-semibold text-white hover:bg-white/10">
              Try chat
            </Link>
          </div>
        </div>
        <div className="surface grid content-center rounded-lg p-5">
          <div className="grid gap-3">
            {["Client", "WebSocket Gateway", "Message API", "RabbitMQ", "Worker", "PostgreSQL", "Delivery Fanout"].map((step, index) => (
              <div key={step} className="flex items-center gap-4 rounded-md border border-white/10 bg-white/[0.03] p-4">
                <span className="grid size-9 place-items-center rounded-md bg-white/10 text-sm text-mint">{index + 1}</span>
                <span className="font-medium text-white">{step}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="mx-auto max-w-7xl px-5 pb-16">
        <div className="grid gap-4 md:grid-cols-3">
          {features.map(([label, Icon]) => (
            <div key={label} className="surface rounded-lg p-5">
              <Icon className="mb-4 text-amber" size={22} />
              <h2 className="font-semibold text-white">{label}</h2>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
