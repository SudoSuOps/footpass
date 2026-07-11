import type { ReactNode } from "react";

// Reusable, high-contrast, large-touch-target primitives.

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-xl2 bg-card shadow-sm ring-1 ring-black/5 p-5 ${className}`}>
      {children}
    </div>
  );
}

export function BigButton({
  children,
  onClick,
  variant = "primary",
  disabled,
}: {
  children: ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary";
  disabled?: boolean;
}) {
  const styles =
    variant === "primary"
      ? "bg-brand text-white hover:bg-ink active:scale-[0.99]"
      : "bg-white text-ink ring-2 ring-brand/30 hover:ring-brand";
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`w-full rounded-xl2 px-6 py-5 text-xl font-semibold shadow-sm transition
        disabled:opacity-50 disabled:cursor-not-allowed ${styles}`}
    >
      {children}
    </button>
  );
}

export function StatusPill({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium
        ${ok ? "bg-brand/10 text-brand" : "bg-muted/10 text-muted"}`}
    >
      <span className={`h-2.5 w-2.5 rounded-full ${ok ? "bg-brand" : "bg-muted"}`} />
      {label}
    </span>
  );
}

export function Freddy({ children }: { children: ReactNode }) {
  return (
    <div className="flex items-start gap-3 rounded-xl2 bg-white/70 p-4 ring-1 ring-black/5">
      <div className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-brand/10 text-2xl" aria-hidden>
        🐝
      </div>
      <p className="text-base leading-relaxed text-ink/90">
        <span className="font-semibold">Freddy:</span> {children}
      </p>
    </div>
  );
}
