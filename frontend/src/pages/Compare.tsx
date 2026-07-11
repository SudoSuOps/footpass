import { Card, Freddy } from "../components/ui";

export default function Compare() {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Compare photos</h2>
      <Freddy>
        Once you have photos from two different days, you’ll be able to line them up side by side —
        with an opacity slider, a before/after wipe, and zoom — to see what has changed.
      </Freddy>
      <Card>
        <p className="text-sm text-muted">
          Image comparison arrives in a later update.
        </p>
      </Card>
      <p className="px-1 text-xs leading-relaxed text-muted">
        FootPass helps you organize and compare images. It does not diagnose medical conditions.
        Contact your clinician if you notice a new or concerning change.
      </p>
    </div>
  );
}
