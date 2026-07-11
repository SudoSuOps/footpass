import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";

const NAV = [
  { to: "/", label: "Today", icon: "🦶", end: true },
  { to: "/passport", label: "Passport", icon: "📖" },
  { to: "/compare", label: "Compare", icon: "🔍" },
  { to: "/export", label: "Export", icon: "📤" },
  { to: "/settings", label: "Settings", icon: "⚙️" },
];

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="mx-auto flex min-h-full max-w-2xl flex-col">
      <header className="flex items-center gap-3 px-5 pt-6 pb-3">
        <span className="text-3xl" aria-hidden>
          🐝
        </span>
        <div>
          <h1 className="text-xl font-bold tracking-tight">FootPass</h1>
          <p className="text-xs text-muted">Your private foot passport</p>
        </div>
      </header>

      <main className="flex-1 px-5 pb-28">{children}</main>

      <nav className="fixed inset-x-0 bottom-0 z-10 border-t border-black/5 bg-white/95 backdrop-blur">
        <ul className="mx-auto flex max-w-2xl">
          {NAV.map((item) => (
            <li key={item.to} className="flex-1">
              <NavLink
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  `flex flex-col items-center gap-0.5 py-3 text-xs font-medium
                   ${isActive ? "text-brand" : "text-muted"}`
                }
              >
                <span className="text-2xl" aria-hidden>
                  {item.icon}
                </span>
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
