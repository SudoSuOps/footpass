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

export interface CaptureResult {
  ok: boolean;
  width: number;
  height: number;
  device_index: number;
  quality: { brightness: number; sharpness: number; status: string; reasons: string[] };
  image_b64: string;
}

export interface FootImage {
  id: number;
  daily_check_id: number;
  side: string;
  view: string;
  sha256: string;
  width: number;
  height: number;
  quality_status: string;
  sharpness_score: number | null;
  brightness_score: number | null;
  captured_at: string | null;
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
  cameraStatus: () => req<StatusCardData>("/camera/status"),
  backupStatus: () => req<StatusCardData>("/api/backup/status"),

  // Camera capture (a fresh oriented frame from the server-side camera)
  capture: (flipH: boolean) =>
    req<CaptureResult>(`/camera/capture${flipH ? "?flip=h" : ""}`),
  streamUrl: (flipH: boolean) => `/camera/stream${flipH ? "?flip=h" : ""}`,

  // Save an approved frame into a check
  saveImage: (checkId: number, side: string, view: string, image_b64: string, quality: object) =>
    req<FootImage>(`/api/checks/${checkId}/images`, {
      method: "POST",
      body: JSON.stringify({ side, view, image_b64, quality }),
    }),
  checkImages: (checkId: number) => req<FootImage[]>(`/api/checks/${checkId}/images`),
  completeCheck: (checkId: number) =>
    req<Check>(`/api/checks/${checkId}/complete`, { method: "POST", body: "{}" }),
  imageUrl: (id: number) => `/api/images/${id}`,
  thumbUrl: (id: number) => `/api/images/${id}/thumb`,
};
