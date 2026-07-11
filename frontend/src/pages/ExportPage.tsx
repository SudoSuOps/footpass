import { Card, Freddy } from "../components/ui";

export default function ExportPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Export passport</h2>
      <Freddy>
        When you’re ready to share with your clinician, FootPass will build a tidy package — a ZIP
        with your originals and notes, or a clean PDF summary — that you own and control.
      </Freddy>
      <Card>
        <p className="text-sm text-muted">ZIP and PDF export arrive in a later update.</p>
      </Card>
    </div>
  );
}
