import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api, type CaptureResult } from "../lib/api";
import { BigButton, Card } from "../components/ui";

const SIDES = [
  { key: "right", label: "Right" },
  { key: "left", label: "Left" },
];
const VIEWS = [
  { key: "plantar", label: "Sole" },
  { key: "medial", label: "Inside" },
  { key: "lateral", label: "Outside" },
];

function viewLabel(side: string, view: string): string {
  const s = side === "right" ? "Right foot" : "Left foot";
  const v = view === "plantar" ? "sole (bottom)" : view === "medial" ? "inside" : "outside";
  return `${s} — ${v}`;
}

export default function Capture() {
  const [params] = useSearchParams();
  const nav = useNavigate();
  const [checkId, setCheckId] = useState<number | null>(
    params.get("check") ? Number(params.get("check")) : null,
  );
  const [cameraOk, setCameraOk] = useState<boolean | null>(null);
  const [side, setSide] = useState("right");
  const [view, setView] = useState("plantar");
  const [flipH, setFlipH] = useState(false);
  const [captured, setCaptured] = useState<CaptureResult | null>(null);
  const [countdown, setCountdown] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [savedCount, setSavedCount] = useState(0);
  const [busy, setBusy] = useState(false);
  const voiceRef = useRef(false);

  useEffect(() => {
    api.cameraStatus().then((s) => setCameraOk(s.available)).catch(() => setCameraOk(false));
    api.settings().then((rows) => {
      voiceRef.current = rows.find((r) => r.setting_key === "voice_guidance")?.setting_value === "true";
    }).catch(() => {});
    if (checkId === null) {
      api.createCheck().then((c) => setCheckId(c.id)).catch(() => {});
    }
  }, [checkId]);

  const say = (text: string) => {
    if (voiceRef.current && "speechSynthesis" in window) {
      const u = new SpeechSynthesisUtterance(text);
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(u);
    }
  };

  const doCapture = useCallback(async () => {
    if (busy || captured) return;
    setBusy(true);
    try {
      const shot = await api.capture(flipH);
      setCaptured(shot);
      say(shot.quality.status === "pass" ? "Photo captured." : "That photo may be blurry. Let’s try again.");
    } catch {
      /* camera hiccup — ignore, user can retry */
    } finally {
      setBusy(false);
    }
  }, [busy, captured, flipH]);

  const startCountdown = () => {
    if (busy || captured || countdown !== null) return;
    let n = 3;
    setCountdown(n);
    say("Hold still.");
    const t = setInterval(() => {
      n -= 1;
      if (n <= 0) {
        clearInterval(t);
        setCountdown(null);
        doCapture();
      } else {
        setCountdown(n);
      }
    }, 1000);
  };

  // Hands-free: spacebar / Enter captures (Bluetooth remotes present as keyboards)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.code === "Space" || e.code === "Enter") {
        e.preventDefault();
        if (!captured) doCapture();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [captured, doCapture]);

  async function save() {
    if (!captured || checkId === null) return;
    setSaving(true);
    try {
      await api.saveImage(checkId, side, view, captured.image_b64, {
        ...captured.quality,
        device: captured.device_index,
      });
      setSavedCount((c) => c + 1);
      setCaptured(null);
      say("Saved.");
    } catch {
      /* keep the review open so nothing is lost */
    } finally {
      setSaving(false);
    }
  }

  async function finish() {
    if (checkId !== null) {
      try {
        await api.completeCheck(checkId);
      } catch {
        /* ignore */
      }
    }
    say("Your check is saved.");
    nav("/passport");
  }

  const q = captured?.quality;
  const pass = q?.status === "pass";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Today’s photos</h2>
        {savedCount > 0 && (
          <span className="rounded-full bg-brand/10 px-3 py-1 text-sm font-semibold text-brand">
            {savedCount} saved
          </span>
        )}
      </div>

      {/* which photo */}
      <Card className="space-y-3">
        <p className="text-sm font-semibold text-muted">{viewLabel(side, view)}</p>
        <div className="flex gap-2">
          {SIDES.map((s) => (
            <button
              key={s.key}
              onClick={() => setSide(s.key)}
              className={`flex-1 rounded-xl2 py-3 text-base font-semibold ${
                side === s.key ? "bg-brand text-white" : "bg-white ring-2 ring-brand/20 text-ink"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          {VIEWS.map((v) => (
            <button
              key={v.key}
              onClick={() => setView(v.key)}
              className={`flex-1 rounded-xl2 py-3 text-base font-semibold ${
                view === v.key ? "bg-ink text-white" : "bg-white ring-2 ring-ink/10 text-ink"
              }`}
            >
              {v.label}
            </button>
          ))}
        </div>
      </Card>

      {/* preview / review */}
      <div className="relative overflow-hidden rounded-xl2 bg-black ring-1 ring-black/10">
        {captured ? (
          <img
            src={`data:image/jpeg;base64,${captured.image_b64}`}
            alt="captured"
            className="w-full"
          />
        ) : cameraOk === false ? (
          <div className="grid aspect-[4/3] place-items-center p-6 text-center text-white/80">
            No camera detected on the appliance. Check the USB connection, then reload.
          </div>
        ) : (
          <>
            <img
              key={String(flipH)}
              src={api.streamUrl(flipH)}
              alt="live preview"
              className="w-full"
            />
            {/* plantar positioning guide */}
            {view === "plantar" && (
              <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
                <div className="h-[78%] w-[46%] rounded-[45%] border-4 border-dashed border-white/70" />
                <span className="absolute bottom-3 rounded-full bg-black/50 px-3 py-1 text-sm text-white">
                  Center your sole in the outline
                </span>
              </div>
            )}
            {countdown !== null && (
              <div className="absolute inset-0 grid place-items-center bg-black/40">
                <span className="text-8xl font-bold text-white">{countdown}</span>
              </div>
            )}
          </>
        )}
      </div>

      {/* quality verdict on review */}
      {captured && (
        <Card
          className={pass ? "ring-2 ring-brand/40" : "ring-2 ring-accent/40"}
        >
          <p className="font-semibold">
            {pass ? "✓ Looks good" : "⚠ Might want a retake"}
          </p>
          {!pass && q && (
            <p className="text-sm text-muted">{q.reasons.join(" · ") || "low quality"}</p>
          )}
          <p className="mt-1 text-xs text-muted">
            {captured.width}×{captured.height} · sharpness {q?.sharpness} · brightness {q?.brightness}
          </p>
        </Card>
      )}

      {/* controls */}
      {captured ? (
        <div className="grid grid-cols-2 gap-3">
          <BigButton variant="secondary" onClick={() => setCaptured(null)}>
            ↺ Retake
          </BigButton>
          <BigButton onClick={save} disabled={saving}>
            {saving ? "Saving…" : "✓ Save"}
          </BigButton>
        </div>
      ) : (
        <div className="space-y-3">
          <BigButton onClick={doCapture} disabled={busy || cameraOk === false}>
            📸 Capture <span className="text-base font-normal opacity-80">(or press space)</span>
          </BigButton>
          <div className="grid grid-cols-2 gap-3">
            <BigButton variant="secondary" onClick={startCountdown} disabled={cameraOk === false}>
              ⏱ 3-2-1 timer
            </BigButton>
            <BigButton variant="secondary" onClick={() => setFlipH((f) => !f)}>
              {flipH ? "⇄ Flipped" : "⇄ Flip"}
            </BigButton>
          </div>
        </div>
      )}

      <button onClick={finish} className="w-full py-3 text-sm font-semibold text-brand">
        Finish check →
      </button>

      <p className="px-1 text-xs leading-relaxed text-muted">
        FootPass helps you organize and compare images. It does not diagnose medical conditions.
      </p>
    </div>
  );
}
