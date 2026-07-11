import { useEffect, useState } from "react";
import { api, type Check } from "../lib/api";
import { Card, Freddy } from "../components/ui";

export default function Passport() {
  const [checks, setChecks] = useState<Check[]>([]);

  useEffect(() => {
    api.checks().then(setChecks).catch(() => {});
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Passport history</h2>

      {checks.length === 0 ? (
        <Freddy>
          No checks yet. When you complete your first daily check, it will appear here — with
          thumbnails, a calendar view, and notes.
        </Freddy>
      ) : (
        <Card className="divide-y divide-black/5">
          {checks.map((c) => (
            <div key={c.id} className="flex items-center justify-between py-3">
              <span className="font-semibold">{c.check_date}</span>
              <span
                className={`rounded-full px-3 py-1 text-xs font-medium ${
                  c.status === "completed" ? "bg-brand/10 text-brand" : "bg-muted/10 text-muted"
                }`}
              >
                {c.status.replace("_", " ")}
              </span>
            </div>
          ))}
        </Card>
      )}

      <p className="text-xs text-muted">
        Calendar view, thumbnails, filters, and clinician-review flags arrive with the guided
        capture update.
      </p>
    </div>
  );
}
