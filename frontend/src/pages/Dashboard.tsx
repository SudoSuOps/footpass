import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, type Check, type StatusCardData, type SystemInfo } from "../lib/api";
import { BigButton, Card, StatusPill } from "../components/ui";

function todayLong(): string {
  return new Date().toLocaleDateString(undefined, {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function computeStreak(checks: Check[]): number {
  const done = new Set(checks.filter((c) => c.status === "completed").map((c) => c.check_date));
  let streak = 0;
  const d = new Date();
  for (;;) {
    const iso = d.toISOString().slice(0, 10);
    if (done.has(iso)) {
      streak += 1;
      d.setDate(d.getDate() - 1);
    } else break;
  }
  return streak;
}

export default function Dashboard() {
  const [name, setName] = useState<string>("");
  const [checks, setChecks] = useState<Check[]>([]);
  const [camera, setCamera] = useState<StatusCardData | null>(null);
  const [backup, setBackup] = useState<StatusCardData | null>(null);
  const [system, setSystem] = useState<SystemInfo | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.settings().then((s) => {
      const n = s.find((x) => x.setting_key === "display_name")?.setting_value;
      if (n) setName(n);
    }).catch(() => {});
    api.checks().then(setChecks).catch(() => {});
    api.cameraStatus().then(setCamera).catch(() => {});
    api.backupStatus().then(setBackup).catch(() => {});
    api.system().then(setSystem).catch(() => {});
  }, []);

  const lastCompleted = checks.find((c) => c.status === "completed");
  const streak = computeStreak(checks);
  const greeting = name ? `Hello, ${name}.` : "Hello.";

  async function startCheck() {
    try {
      const check = await api.createCheck();
      navigate(`/capture?check=${check.id}`);
    } catch {
      navigate("/capture");
    }
  }

  return (
    <div className="space-y-5">
      {!name && (
        <Link
          to="/welcome"
          className="block rounded-xl2 bg-brand/10 px-4 py-3 text-center text-sm font-semibold text-brand"
        >
          👋 Finish quick setup →
        </Link>
      )}

      <div>
        <h2 className="text-2xl font-bold">{greeting}</h2>
        <p className="text-muted">{todayLong()}</p>
      </div>

      <Card className="space-y-4">
        <div>
          <p className="text-lg font-semibold">Take five minutes for your feet.</p>
          <p className="text-muted">Freddy will guide you through today’s photos.</p>
        </div>
        <BigButton onClick={startCheck}>▶ Start Today’s Check</BigButton>
      </Card>

      <div className="grid grid-cols-2 gap-4">
        <Card>
          <p className="text-sm text-muted">Last check</p>
          <p className="text-lg font-semibold">
            {lastCompleted ? lastCompleted.check_date : "None yet"}
          </p>
        </Card>
        <Card>
          <p className="text-sm text-muted">Current streak</p>
          <p className="text-lg font-semibold">
            {streak} {streak === 1 ? "day" : "days"}
          </p>
        </Card>
      </div>

      <Card className="space-y-3">
        <p className="text-sm font-semibold text-muted">Appliance status</p>
        <div className="flex flex-wrap gap-2">
          <StatusPill
            ok={!!system && system.disk.free_gb > 2}
            label={system ? `Storage ${system.disk.free_gb} GB free` : "Storage…"}
          />
          <StatusPill ok={!!camera?.available} label={camera?.available ? "Camera ready" : "Camera not set up"} />
          <StatusPill ok={!!backup?.available} label={backup?.available ? "Backup on" : "Backup off"} />
          <StatusPill ok={system?.database === "ok"} label={system?.database === "ok" ? "Database ok" : "Database…"} />
        </div>
        <Link to="/system" className="inline-block text-sm font-semibold text-brand">
          View system health →
        </Link>
      </Card>

      <p className="px-1 text-xs leading-relaxed text-muted">
        FootPass helps you organize and compare images. It does not diagnose medical conditions.
        Contact your clinician if you notice a new or concerning change.
      </p>
    </div>
  );
}
