import { createFileRoute } from "@tanstack/react-router";
import { FileText, Printer } from "lucide-react";
import { PageHeader, Panel, SeverityBadge } from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import { anomalies, entities, primaryCase, timelineEvents } from "@/lib/mock-data";
import { toast } from "sonner";

export const Route = createFileRoute("/reports")({
  head: () => ({
    meta: [
      { title: "Case Report — SENTINEL" },
      {
        name: "description",
        content:
          "Generate a structured investigation report with findings, correlations, timeline and evidence references.",
      },
      { property: "og:title", content: "Investigation Report Builder" },
      { property: "og:description", content: "Court-ready structured summaries of analytical findings." },
    ],
  }),
  component: ReportsPage,
});

function ReportsPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        title="Investigation Report"
        subtitle={`${primaryCase.id} · ${primaryCase.title}`}
        action={
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => toast.success("Report exported as PDF (simulated)")}>
              <FileText className="size-4" />
              Export PDF
            </Button>
            <Button onClick={() => toast("Print preview opened (simulated)")}>
              <Printer className="size-4" />
              Print
            </Button>
          </div>
        }
      />

      <Panel bodyClassName="space-y-6 p-6 md:p-8">
        <header className="border-b border-border pb-4">
          <p className="label-xs">Confidential · Restricted distribution</p>
          <h2 className="mt-1 text-lg font-semibold text-foreground">
            Digital Footprint Analysis Report
          </h2>
          <p className="mt-1 text-xs text-muted-foreground">
            Case {primaryCase.id} · Officer {primaryCase.officer} · Generated for internal investigative use
          </p>
        </header>

        <section>
          <h3 className="label-xs">1. Executive summary</h3>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            Analysis of authorized telecom, financial and public social datasets identified{" "}
            {anomalies.length} anomalies and a recurring bridge entity connecting two otherwise separate
            activity clusters. Findings are analytical indicators derived from imported records and require
            corroboration through standard investigative procedure.
          </p>
        </section>

        <section>
          <h3 className="label-xs">2. Key findings</h3>
          <ul className="mt-2 space-y-2">
            {anomalies.slice(0, 4).map((a) => (
              <li key={a.id} className="flex items-start gap-2 text-sm">
                <SeverityBadge severity={a.severity} />
                <span className="text-muted-foreground">
                  <span className="text-foreground">{a.title}</span> — {a.description}
                </span>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h3 className="label-xs">3. Entities of interest</h3>
          <div className="mt-2 overflow-x-auto">
            <table className="w-full min-w-[520px] text-xs">
              <thead className="border-b border-border text-left text-muted-foreground">
                <tr>
                  {["Identifier", "Type", "Priority", "Domains"].map((h) => (
                    <th key={h} className="py-2 font-medium">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {entities
                  .slice()
                  .sort((a, b) => b.priority - a.priority)
                  .slice(0, 6)
                  .map((e) => (
                    <tr key={e.id}>
                      <td className="py-2 font-mono text-primary">{e.id}</td>
                      <td className="py-2 text-muted-foreground">{e.type}</td>
                      <td className="py-2 font-mono text-foreground">{e.priority}</td>
                      <td className="py-2 text-muted-foreground">{e.domains.join(", ")}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </section>

        <section>
          <h3 className="label-xs">4. Reconstructed sequence</h3>
          <ol className="mt-2 space-y-1.5">
            {timelineEvents.slice(0, 6).map((t) => (
              <li key={t.id} className="flex gap-3 text-xs">
                <span className="w-36 shrink-0 font-mono text-muted-foreground">{t.timestamp}</span>
                <span className="text-foreground">{t.title}</span>
              </li>
            ))}
          </ol>
        </section>

        <section>
          <h3 className="label-xs">5. Method &amp; limitations</h3>
          <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
            Detections use rule-based thresholds and graph analysis over imported datasets. Scores are
            explainable and reproducible, but they are decision-support indicators only. No live platform
            access, interception, or personal data beyond the authorized case datasets was used.
          </p>
        </section>
      </Panel>
    </div>
  );
}
