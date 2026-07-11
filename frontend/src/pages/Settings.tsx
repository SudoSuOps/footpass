import { useEffect, useState } from "react";
import { api, type Setting } from "../lib/api";
import { BigButton, Card } from "../components/ui";

export default function Settings() {
  const [name, setName] = useState("");
  const [voice, setVoice] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.settings().then((rows: Setting[]) => {
      setName(rows.find((r) => r.setting_key === "display_name")?.setting_value ?? "");
      setVoice(rows.find((r) => r.setting_key === "voice_guidance")?.setting_value === "true");
    }).catch(() => {});
  }, []);

  async function save() {
    await Promise.all([
      api.saveSetting("display_name", name.trim() || "friend"),
      api.saveSetting("voice_guidance", String(voice)),
    ]).catch(() => {});
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Settings</h2>

      <Card className="space-y-4">
        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-muted">Display name</span>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-xl2 border border-black/10 px-4 py-3 text-lg outline-none focus:border-brand"
          />
        </label>

        <label className="flex items-center justify-between gap-4">
          <span className="text-base font-medium">Spoken guidance (Freddy’s voice)</span>
          <input
            type="checkbox"
            checked={voice}
            onChange={(e) => setVoice(e.target.checked)}
            className="h-6 w-6 accent-brand"
          />
        </label>
        <p className="text-xs text-muted">
          Uses your browser’s built-in speech only. No cloud speech service. Off by default.
        </p>

        <BigButton onClick={save}>{saved ? "Saved ✓" : "Save settings"}</BigButton>
      </Card>

      <Card>
        <p className="text-sm font-semibold text-muted">Local PIN</p>
        <p className="text-sm text-muted">
          An optional local PIN to protect this passport arrives in the security phase. It will be
          stored only as a secure hash on this device.
        </p>
      </Card>

      <p className="px-1 text-xs leading-relaxed text-muted">
        FootPass helps you organize and compare images. It does not diagnose medical conditions.
      </p>
    </div>
  );
}
