import { ArrowDown, Boxes, Database, Radio, RefreshCcw, Server, ShieldCheck } from "lucide-react";
import type { LucideIcon } from "lucide-react";

const flow: Array<[string, LucideIcon, string]> = [
  ["WebSocket clients", Radio, "Users publish messages and subscribe to room-level updates."],
  ["Message API", Server, "Validates payloads, applies rate limits, enforces idempotency, and assigns room sequence numbers."],
  ["RabbitMQ queues", Boxes, "Main queue buffers work; retry and DLQ paths isolate downstream failures."],
  ["Worker consumers", RefreshCcw, "Persist delivery attempts, apply exponential backoff, and emit status transitions."],
  ["PostgreSQL", Database, "Stores users, rooms, messages, status events, and delivery attempts."],
  ["Realtime delivery", ShieldCheck, "Broadcasts delivered, failed, read, and dead-lettered events to connected clients."],
];

export default function ArchitecturePage() {
  return (
    <main className="mx-auto max-w-6xl px-5 py-8">
      <h1 className="text-3xl font-semibold text-white">Architecture</h1>
      <p className="mt-3 max-w-3xl text-slate-300">
        QueuePulse models the backend mechanics behind large-scale messaging systems: asynchronous ingestion,
        durable persistence, retry isolation, room ordering, and operational feedback loops.
      </p>
      <section className="mt-8 grid gap-4">
        {flow.map(([title, Icon, text], index) => (
          <div key={title}>
            <div className="surface grid gap-4 rounded-lg p-5 md:grid-cols-[48px_1fr]">
              <span className="grid size-12 place-items-center rounded-md bg-mint/15 text-mint"><Icon size={22} /></span>
              <div>
                <h2 className="font-semibold text-white">{title}</h2>
                <p className="mt-1 text-slate-400">{text}</p>
              </div>
            </div>
            {index < flow.length - 1 && <ArrowDown className="mx-auto my-2 text-slate-500" />}
          </div>
        ))}
      </section>
    </main>
  );
}
