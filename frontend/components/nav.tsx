import Link from "next/link";
import { Activity, Github } from "lucide-react";

const links = [
  ["Chat", "/chat"],
  ["Dashboard", "/dashboard"],
  ["Architecture", "/architecture"],
];

export function Nav() {
  return (
    <header className="sticky top-0 z-20 border-b border-white/10 bg-ink/85 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
        <Link href="/" className="flex items-center gap-3 font-semibold tracking-wide text-white">
          <span className="grid size-9 place-items-center rounded-md bg-mint/15 text-mint">
            <Activity size={19} />
          </span>
          QueuePulse
        </Link>
        <nav className="flex items-center gap-1 text-sm text-slate-300">
          {links.map(([label, href]) => (
            <Link key={href} href={href} className="rounded-md px-3 py-2 hover:bg-white/10 hover:text-white">
              {label}
            </Link>
          ))}
          <a className="rounded-md px-3 py-2 hover:bg-white/10 hover:text-white" href="https://github.com" aria-label="GitHub">
            <Github size={18} />
          </a>
        </nav>
      </div>
    </header>
  );
}
