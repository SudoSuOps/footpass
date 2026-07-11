// Typed API client. Same-origin in production (behind Caddy); dev proxy in Vite.

export interface Health {
  status: string;
  version: string;
  environment: string;
  database: string;
}

export interface SystemInfo {
  version: string;
  environment: string;
  hostname: string;
  uptime_seconds: number;
  cpu_count: number;
  cpu_percent: number;
  load_average: number[];
  memory: { total_gb: number; used_gb: number; percent_used: number };
  disk: { path: string; total_gb: number; used_gb: number; free_gb: number; percent_used: number };
  database: string;
  gpu: Array<{ name: string; driver_version?: string; memory_total_mb?: number; temperature_c?: number }>;
  cpu_temp_c: number | null;
}

export interface Check {
  id: number;
  user_id: number;
  check_date: string;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  notes: string | null;
}

export interface Setting {
  setting_key: string;
  setting_value: string | null;
  updated_at?: string;
}

export interface StatusCardData {
  available: boolean;
  status: string;
  last_backup?: string | null;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { Accept: "application/json", ...(init?.body ? { "Content-Type": "application/json" } : {}) },
    ...init,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return (await res.json()) as T;
}

export const api = {
  health: () => req<Health>("/api/health"),
  system: () => req<SystemInfo>("/api/system"),
  checks: () => req<Check[]>("/api/checks"),
  createCheck: () => req<Check>("/api/checks", { method: "POST", body: JSON.stringify({}) }),
  settings: () => req<Setting[]>("/api/settings"),
  saveSetting: (setting_key: string, setting_value: string | null) =>
    req<Setting>("/api/settings", {
      method: "PATCH",
      body: JSON.stringify({ setting_key, setting_value }),
    }),
  cameraStatus: () => req<StatusCardData>("/api/camera/status"),
  backupStatus: () => req<StatusCardData>("/api/backup/status"),
};
