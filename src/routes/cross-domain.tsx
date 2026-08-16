import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowDown } from "lucide-react";
import { DomainTag, PageHeader, Panel } from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import { crossDomainChain } from "@/lib/mock-data";

export const Route = createFileRoute("/cross-domain")({
  head: () => ({
    meta: [
      { title: "Cross-Domain Intelligence — SENTINEL" },
      {
        name: "description",
        content:
          "How telecom, financial, social and network records connect through shared or correlated identifiers.",
      },
      { property: "og:title", content: "Cross-Domain Intelligence" },
      { property: "og:description", content: "One connected chain across four data domains." },
    ],
  }),
  component: CrossDomainPage,
});

function CrossDomainPage() {
  return (
    <div className="space-y-5">
      <PageHeader
        title="Cross-Domain Intelligence"
        subtitle="These records are connected through shared or correlated identifiers and activity patterns observed in the imported datasets."
      />

      <div className="grid gap-4 xl:grid-cols-[1fr_320px]">
        <Panel title="Correlation chain" subtitle="Telecom → Person → Financial → Social → Network">
          <ol className="space-y-2">
            {crossDomainChain.map((step, i) => (
              <li key={step.id}>
                <div className="flex items-center justify-between gap-3 rounded-sm border border-border bg-secondary/30 p-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <DomainTag domain={step.domain} />
                      <span className="font-mono text-xs text-primary">{step.id}</span>
                    </div>
                    <div className="mt-1 text-sm text-foreground">{step.label}</div>
                    <p className="text-[11px] text-muted-foreground">{step.note}</p>
                  </div>
                  <Button asChild size="sm" variant="ghost" className="h-7 text-[11px]">
                    <Link to="/entities/$entityId" params={{ entityId: step.id }}>
                      Inspect
                    </Link>
                  </Button>
                </div>
                {i < crossDomainChain.length - 1 && (
                  <div className="flex justify-center py-1 text-muted-foreground">
                    <ArrowDown className="size-4" aria-hidden />
                  </div>
                )}
              </li>
            ))}
          </ol>
        </Panel>

        <div className="space-y-3">
          <Panel title="What links these domains" bodyClassName="space-y-2 p-4">
            {[
              "Subscriber identifier shared between CDR and bank KYC records",
              "IPDR session origin observed for both telecom and social activity",
              "Transfer timing aligned with call and session timestamps",
              "Public profile identifier correlated with the resolved person entity",
            ].map((s) => (
              <p key={s} className="flex gap-2 text-xs text-muted-foreground">
                <span className="text-primary">▸</span>
                {s}
              </p>
            ))}
          </Panel>
          <Panel title="Next step" bodyClassName="p-4">
            <p className="text-xs text-muted-foreground">
              Correlations are analytical links across authorized datasets and require corroboration before any
              investigative action.
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <Button asChild size="sm">
                <Link to="/graph">Open in graph</Link>
              </Button>
              <Button asChild size="sm" variant="outline">
                <Link to="/timeline">Check timing</Link>
              </Button>
            </div>
          </Panel>
        </div>
      </div>
    </div>
  );
}
