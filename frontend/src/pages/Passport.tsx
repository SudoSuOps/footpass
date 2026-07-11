import { useEffect, useState } from "react";
import { api, type Check, type FootImage, type ReviewResult, type VisionStatus } from "../lib/api";
import { Card, Freddy } from "../components/ui";

export default function Passport() {
  const [checks, setChecks] = useState<Check[]>([]);
  const [images, setImages] = useState<Record<number, FootImage[]>>({});
  const [vision, setVision] = useState<VisionStatus | null>(null);
  const [reviews, setReviews] = useState<Record<number, ReviewResult>>({});
  const [busy, setBusy] = useState<number | null>(null);
  const [errs, setErrs] = useState<Record<number, string>>({});

  useEffect(() => {
    api.visionStatus().then(setVision).catch(() => {});
    api.checks().then(async (cs) => {
      setChecks(cs);
      const byCheck: Record<number, FootImage[]> = {};
      await Promise.all(
        cs.map(async (c) => {
          try {
            byCheck[c.id] = await api.checkImages(c.id);
          } catch {
            byCheck[c.id] = [];
          }
        }),
      );
      setImages(byCheck);
    }).catch(() => {});
  }, []);

  async function askFreddy(checkId: number) {
    setBusy(checkId);
    setErrs((e) => ({ ...e, [checkId]: "" }));
    try {
      const r = await api.reviewCheck(checkId);
      setReviews((rv) => ({ ...rv, [checkId]: r }));
    } catch {
      setErrs((e) => ({ ...e, [checkId]: "Freddy couldn’t reach the review helper just now." }));
    } finally {
      setBusy(null);
    }
  }

  const aiReady = vision?.enabled && vision?.reachable;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Passport history</h2>

      {vision?.enabled && (
        <div className="flex items-center gap-2 text-sm">
          <span className={`h-2.5 w-2.5 rounded-full ${aiReady ? "bg-brand" : "bg-muted"}`} />
          <span className="text-muted">
            Freddy’s review helper: {aiReady ? "ready" : "offline"}
          </span>
        </div>
      )}

      {checks.length === 0 ? (
        <Freddy>
          No checks yet. Tap “Start Today’s Check” on the Today screen to take your first photos —
          they’ll appear here with thumbnails.
        </Freddy>
      ) : (
        checks.map((c) => {
          const imgs = images[c.id] ?? [];
          const review = reviews[c.id];
          return (
            <Card key={c.id} className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-semibold">{c.check_date}</span>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    c.status === "completed" ? "bg-brand/10 text-brand" : "bg-muted/10 text-muted"
                  }`}
                >
                  {c.status.replace("_", " ")}
                </span>
              </div>

              {imgs.length === 0 ? (
                <p className="text-sm text-muted">No photos in this check.</p>
              ) : (
                <div className="grid grid-cols-3 gap-2">
                  {imgs.map((im) => (
                    <a key={im.id} href={api.imageUrl(im.id)} target="_blank" rel="noreferrer">
                      <img
                        src={api.thumbUrl(im.id)}
                        alt={`${im.side} ${im.view}`}
                        className="aspect-square w-full rounded-lg object-cover ring-1 ring-black/10"
                      />
                      <span className="mt-1 block text-center text-[11px] text-muted">
                        {im.side} · {im.view}
                      </span>
                    </a>
                  ))}
                </div>
              )}

              {aiReady && imgs.length > 0 && (
                <button
                  onClick={() => askFreddy(c.id)}
                  disabled={busy === c.id}
                  className="w-full rounded-xl2 bg-brand/10 py-3 text-sm font-semibold text-brand disabled:opacity-60"
                >
                  {busy === c.id ? "🐝 Freddy is looking…" : "🐝 Ask Freddy to look"}
                </button>
              )}

              {errs[c.id] && <p className="text-sm text-accent">{errs[c.id]}</p>}

              {review && (
                <div className="rounded-xl2 bg-white/70 p-4 ring-1 ring-black/5">
                  <p className="mb-1 text-sm font-semibold">🐝 Freddy’s observation</p>
                  <p className="text-sm leading-relaxed text-ink/90">{review.review}</p>
                  <p className="mt-2 text-[11px] leading-relaxed text-muted">{review.disclaimer}</p>
                </div>
              )}
            </Card>
          );
        })
      )}
    </div>
  );
}
