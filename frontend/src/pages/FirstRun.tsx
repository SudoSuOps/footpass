import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { BigButton, Card, Freddy } from "../components/ui";

export default function FirstRun() {
  const [name, setName] = useState("");
  const [saving, setSaving] = useState(false);
  const nav = useNavigate();

  async function finish() {
    setSaving(true);
    try {
      await api.saveSetting("display_name", name.trim() || "friend");
      await api.saveSetting("setup_complete", "true");
    } catch {
      /* stays local-first; ignore */
    }
    nav("/");
  }

  return (
    <div className="space-y-5">
      <h2 className="text-2xl font-bold">Welcome to FootPass</h2>
      <Freddy>
        Hello — I’m Freddy. I’ll help you take a few clear photos of your feet and keep a private
        record over time. Everything stays on this device. Let’s start with your name.
      </Freddy>

      <Card className="space-y-4">
        <label className="block">
          <span className="mb-2 block text-sm font-semibold text-muted">Display name</span>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="What should I call you?"
            className="w-full rounded-xl2 border border-black/10 px-4 py-4 text-lg outline-none focus:border-brand"
            autoFocus
          />
        </label>
        <p className="text-sm text-muted">No email or account needed. You can change this later in Settings.</p>
        <BigButton onClick={finish} disabled={saving}>
          {saving ? "Saving…" : "Finish setup →"}
        </BigButton>
      </Card>
    </div>
  );
}
