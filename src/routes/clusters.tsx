import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { DomainTag, PageHeader, Panel, SeverityBadge, StatRow } from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import { clusters, hiddenRelationships } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

export const Route = createFileRoute("/clusters")({
  head: () => ({
    meta: [
      { title: "Clusters & Hidden Links — SENTINEL" },
      {
        name: "description",
        content: "Network clusters, central entities and potential bridge relationships discovered across datasets.",
      },
      { property: "og:title", content: "Cluster Analysis & Hidden Relationships" },
      { property: "og:description", content: "Isolate clusters and review potential bridge entities." },
    ],
  }),
  component: ClustersPage,
});

function ClustersPage() {
  const [isolated, setIsolated] = useState<string | null>(null);

  return (
    <div className="space-y-5">
      <PageHeader
        title="Clusters & Hidden Relationships"
        subtitle="Community detection over the relationship graph, with bridge entities that connect otherwise separate clusters."
        action={
          <Button
            onClick={() =>
              toast.success("3 hidden relationships discovered", {
                description: "Bridge and shared-origin links listed below.",
              })
            }
          >
            Discover Hidden Relationships
          </Button>
        }
      />

      <div className="grid gap-3 lg:grid-cols-3">
        {clusters.map((c) => (
          <Panel
            key={c.id}
            className={cn(isolated === c.id && "border-primary/50")}
            title={c.name}
            subtitle={`${c.entityCount} entities`}
          >
            <div className="flex flex-wrap gap-1.5">
              {c.domains.map((d) => (
                <DomainTag key={d} domain={d} />
              ))}
            </div>
            <div className="mt-3">
              <StatRow label="Most connected entity" value={c.centralEntity} />
              <StatRow label="Most active entity" value={c.mostActiveEntity} />
              <StatRow label="Potential bridges" value={c.bridges.join(", ")} />
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <Button
                size="sm"
                variant={isolated === c.id ? "default" : "outline"}
                onClick={() => {
                  setIsolated(isolated === c.id ? null : c.id);
                  toast(isolated === c.id ? `${c.name} restored` : `${c.name} isolated`);
                }}
              >
                {isolated === c.id ? "Restore" : "Isolate cluster"}
              </Button>
              <Button asChild size="sm" variant="ghost">
                <Link to="/graph">Highlight in graph</Link>
              </Button>
            </div>
          </Panel>
        ))}
      </div>

      <Panel title="Hidden relationship findings" bodyClassName="grid gap-3 p-4 lg:grid-cols-3">
        {hiddenRelationships.map((h) => (
          <div key={h.id} className="rounded-sm border border-border bg-secondary/30 p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-foreground">{h.title}</span>
              <SeverityBadge severity={h.strength} />
            </div>
            <p className="mt-1 font-mono text-[11px] text-primary">
              {h.entityId}: {h.clusterA} ↔ {h.clusterB}
            </p>
            <ul className="mt-2 space-y-0.5">
              {h.evidence.map((e) => (
                <li key={e} className="text-[11px] text-muted-foreground">
                  · {e}
                </li>
              ))}
            </ul>
            <Button asChild size="sm" variant="outline" className="mt-3">
              <Link to="/entities/$entityId" params={{ entityId: h.entityId }}>
                Explore Relationship
              </Link>
            </Button>
          </div>
        ))}
      </Panel>
    </div>
  );
}
