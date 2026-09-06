import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { PageHeader, Panel, SeverityBadge, DomainTag } from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/anomalies")({
  head: () => ({
    meta: [
      { title: "Anomalies & Alerts — SENTINEL" },
      {
        name: "description",
        content:
          "Explainable anomaly analytics across telecom, financial, social, network and cross-domain signals.",
      },
      { property: "og:title", content: "Anomaly & Alert Center" },
      { property: "og:description", content: "Every detection is explained by the signals that produced it." },
    ],
  }),
  component: AnomaliesPage,
});

const tabs = ["All", "Telecom", "Financial", "Social", "Network", "Cross-Domain"] as const;

function AnomaliesPage() {
  const [tab, setTab] = useState<(typeof tabs)[number]>("All");
  const [explain, setExplain] = useState<any | null>(null);
  const rows = [].filter((a: any) => (tab === "All" ? true : a.domain === tab));

  return (
    <div className="space-y-5">
      <PageHeader
        title="Anomalies & Alerts"
        subtitle="Detections are analytical findings that require review. Every anomaly exposes the signals behind it — nothing is a black box."
      />

      <div className="flex flex-wrap gap-1.5 border-b border-border pb-3">
        {tabs.map((t) => (
          <button
            key={t}
            type="button"
            aria-pressed={tab === t}
            onClick={() => setTab(t)}
            className={cn(
              "rounded-sm border px-2.5 py-1 font-mono text-[11px] transition-colors",
              tab === t
                ? "border-primary/50 bg-primary/12 text-primary"
                : "border-border text-muted-foreground hover:text-foreground",
            )}
          >
            {t}
          </button>
        ))}
      </div>

      {rows.length === 0 ? (
        <Panel bodyClassName="p-10 text-center">
          <p className="text-sm font-medium text-foreground">No anomalies in this domain</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Import the corresponding dataset to run detection for this domain.
          </p>
          <Button asChild size="sm" variant="outline" className="mt-4">
            <Link to="/data-sources">Import Dataset</Link>
          </Button>
        </Panel>
      ) : (
        <div className="grid gap-3 xl:grid-cols-2">
          {rows.map((a) => (
            <Panel key={a.id} className="transition-colors hover:border-primary/40">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <SeverityBadge severity={a.severity} />
                    <DomainTag domain={a.domain} />
                    <span className="font-mono text-[11px] text-muted-foreground">{a.id}</span>
                  </div>
                  <h3 className="mt-2 text-sm font-semibold text-foreground">{a.title}</h3>
                  <p className="mt-0.5 font-mono text-[11px] text-primary">{a.entityLabel}</p>
                </div>
                <div className="text-right font-mono text-[11px] text-muted-foreground">
                  <div>{a.detectedAt}</div>
                  <div className="mt-1 text-foreground">
                    confidence {Math.round(a.confidence * 100)}%
                  </div>
                </div>
              </div>
              <p className="mt-3 text-xs text-muted-foreground">{a.pattern}</p>
              <p className="mt-2 text-xs leading-relaxed text-foreground">{a.explanation}</p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {a.relatedEntities.map((e) => (
                  <Link
                    key={e}
                    to="/entities/$entityId"
                    params={{ entityId: e }}
                    className="rounded-sm border border-border px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground hover:text-primary"
                  >
                    {e}
                  </Link>
                ))}
              </div>
              <div className="mt-4 flex gap-2">
                <Button asChild size="sm">
                  <Link to="/entities/$entityId" params={{ entityId: a.entityId }}>
                    View Investigation
                  </Link>
                </Button>
                <Button size="sm" variant="outline" onClick={() => setExplain(a)}>
                  Explain Anomaly
                </Button>
              </div>
            </Panel>
          ))}
        </div>
      )}

      <Dialog open={Boolean(explain)} onOpenChange={(o) => !o && setExplain(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Why was this flagged?</DialogTitle>
          </DialogHeader>
          {explain && (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-2">
                <SeverityBadge severity={explain.severity} />
                <DomainTag domain={explain.domain} />
                <span className="font-mono text-xs text-muted-foreground">{explain.entityLabel}</span>
              </div>
              <ol className="space-y-2">
                {explain.signals.map((s, i) => (
                  <li key={s} className="rounded-sm border border-border bg-secondary/40 p-2.5">
                    <div className="label-xs">Signal {i + 1}</div>
                    <p className="mt-0.5 text-xs text-foreground">{s}</p>
                  </li>
                ))}
              </ol>
              <div className="rounded-sm border border-primary/30 bg-primary/8 p-3">
                <div className="label-xs">Investigative relevance</div>
                <p className="mt-1 text-xs text-foreground">{explain.relevance}</p>
              </div>
              <p className="text-[11px] text-muted-foreground">
                Detection confidence {Math.round(explain.confidence * 100)}%. This finding requires review and
                does not establish wrongdoing.
              </p>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
