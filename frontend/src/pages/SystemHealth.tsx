import { useEffect, useState } from "react";
import { api, type SystemInfo } from "../lib/api";
import { Card } from "../components/ui";

function fmtUptime(s: number): string {
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between py-2 text-sm">
      <span className="text-muted">{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}

export default function SystemHealth() {
  const [sys, setSys] = useState<SystemInfo | null>(null);
  const [err, setErr] = useState(false);

  useEffect(() => {
    api.system().then(setSys).catch(() => setErr(true));
  }, []);

  if (err) return <Card>Could not reach the system service.</Card>;
  if (!sys) return <Card>Loading system health…</Card>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">System health</h2>

      <Card className="divide-y divide-black/5">
        <Row label="Version" value={sys.version} />
        <Row label="Environment" value={sys.environment} />
        <Row label="Hostname" value={sys.hostname} />
        <Row label="Uptime" value={fmtUptime(sys.uptime_seconds)} />
        <Row label="Database" value={sys.database} />
      </Card>

      <Card className="divide-y divide-black/5">
        <Row label="CPU" value={`${sys.cpu_count} cores · ${sys.cpu_percent}%`} />
        <Row label="Load (1m/5m/15m)" value={sys.load_average.join(" / ")} />
        <Row label="Memory" value={`${sys.memory.used_gb} / ${sys.memory.total_gb} GB (${sys.memory.percent_used}%)`} />
        <Row
          label="Disk (data)"
          value={`${sys.disk.free_gb} GB free of ${sys.disk.total_gb} GB`}
        />
        {sys.cpu_temp_c != null && <Row label="CPU temp" value={`${sys.cpu_temp_c} °C`} />}
      </Card>

      <Card>
        <p className="mb-2 text-sm font-semibold text-muted">GPU</p>
        {sys.gpu.length === 0 ? (
          <p className="text-sm text-muted">
            No GPU reported. Run <code className="rounded bg-black/5 px-1">make gpu-check</code> on the
            host to enrich this panel. A GPU is not required.
          </p>
        ) : (
          sys.gpu.map((g, i) => (
            <div key={i} className="text-sm">
              <span className="font-semibold">{g.name}</span>
              {g.memory_total_mb ? ` · ${g.memory_total_mb} MB` : ""}
              {g.temperature_c != null ? ` · ${g.temperature_c} °C` : ""}
            </div>
          ))
        )}
      </Card>
    </div>
  );
}
