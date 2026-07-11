import { useEffect, useState } from "react";
import { api, type Check, type FootImage } from "../lib/api";
import { Card, Freddy } from "../components/ui";

export default function Passport() {
  const [checks, setChecks] = useState<Check[]>([]);
  const [images, setImages] = useState<Record<number, FootImage[]>>({});

  useEffect(() => {
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

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Passport history</h2>

      {checks.length === 0 ? (
        <Freddy>
          No checks yet. Tap “Start Today’s Check” on the Today screen to take your first photos —
          they’ll appear here with thumbnails.
        </Freddy>
      ) : (
        checks.map((c) => {
          const imgs = images[c.id] ?? [];
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
            </Card>
          );
        })
      )}
    </div>
  );
}
