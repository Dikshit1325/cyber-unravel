import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import {
  DomainTag,
  PageHeader,
  Panel,
  PriorityScore,
  SeverityBadge,
  StatRow,
  entityIcon,
} from "@/components/investigation/primitives";
import { GraphView, EDGE_TYPES, NODE_TYPES } from "@/components/investigation/GraphView";
import { EntityDrawer } from "@/components/investigation/EntityDrawer";
import { Button } from "@/components/ui/button";
import {
  anomaliesFor,
  communicationsFor,
  getEntity,
  inr,
  neighborsOf,
  relationshipsFor,
  timelineFor,
  transactionsFor,
} from "@/lib/mock-data";

export const Route = createFileRoute("/entities/$entityId")({
  head: ({ params }) => ({
    meta: [
      { title: `Entity ${params.entityId} — SENTINEL` },
      {
        name: "description",
        content: `Cross-domain profile for entity ${params.entityId}: identifiers, relationships, anomalies, timeline and analytical findings.`,
      },
      { property: "og:title", content: `Entity ${params.entityId} profile` },
      {
        property: "og:description",
        content: "Connected identifiers, activity summary and explainable analytical findings.",
      },
    ],
  }),
  component: EntityProfile,
});

function EntityProfile() {
  const { entityId } = Route.useParams();
  const entity = getEntity(entityId);
  const [drawerId, setDrawerId] = useState<string | null>(null);

  if (!entity) {
    return (
      <div className="space-y-4">
        <PageHeader title="Entity not found" subtitle={`No record matches identifier ${entityId}.`} />
        <Panel bodyClassName="p-6">
          <p className="text-sm text-muted-foreground">
            The identifier may be misspelled, or the dataset containing it has not been imported into this
            case workspace.
          </p>
          <div className="mt-4 flex gap-2">
            <Button asChild variant="outline">
              <Link to="/entities">Browse entities</Link>
            </Button>
            <Button asChild>
              <Link to="/data-sources">Import Dataset</Link>
            </Button>
          </div>
        </Panel>
      </div>
    );
  }

  const Icon = entityIcon[entity.type];
  const rels = relationshipsFor(entity.id);
  const txns = transactionsFor(entity.id);
  const comms = communicationsFor(entity.id);
  const anos = anomaliesFor(entity.id);
  const events = timelineFor(entity.id);

  return (
    <div className="space-y-5">
      <Button asChild variant="ghost" size="sm" className="-ml-2">
        <Link to="/entities">
          <ArrowLeft className="size-3.5" />
          All entities
        </Link>
      </Button>

      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border pb-5">
        <div className="flex items-start gap-3">
          <span className="grid size-11 place-items-center rounded-md border border-primary/40 bg-primary/12 text-primary">
            <Icon className="size-5" aria-hidden />
          </span>
          <div>
            <h1 className="font-mono text-xl font-semibold text-foreground">Entity {entity.id}</h1>
            <p className="mt-0.5 text-sm text-muted-foreground">{entity.label}</p>
            <div className="mt-2 flex flex-wrap gap-2">
              <DomainTag domain={entity.domain} />
              <SeverityBadge severity={entity.priority} label={`${entity.priority} PRIORITY`} />
              <span className="rounded-sm border border-border px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
                {entity.cluster}
              </span>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button asChild variant="outline">
            <Link to="/graph">Open in graph</Link>
          </Button>
          <Button asChild>
            <Link to="/reports">Generate report</Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <Panel title="Overview">
          <StatRow label="Entity Type" value={entity.type} />
          <StatRow label="Investigation Priority" value={entity.priority} />
          <StatRow label="First Observed" value={entity.firstObserved} />
          <StatRow label="Last Observed" value={entity.lastObserved} />
          <StatRow label="Cluster" value={entity.cluster} />
        </Panel>

        <Panel title="Connected identifiers">
          {entity.identifiers.length === 0 ? (
            <p className="text-xs text-muted-foreground">
              No secondary identifiers correlated to this entity yet.
            </p>
          ) : (
            entity.identifiers.map((i) => <StatRow key={i.label} label={i.label} value={i.value} />)
          )}
        </Panel>

        <Panel title="Activity summary">
          <StatRow label="Calls" value={comms.length || entity.activity.calls} />
          <StatRow label="Transactions" value={txns.length || entity.activity.transactions} />
          <StatRow label="Social Events" value={entity.activity.socialEvents} />
          <StatRow label="Anomalies" value={anos.length} />
          <StatRow label="Connected Entities" value={neighborsOf(entity.id).length} />
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-[300px_1fr]">
        <Panel title="Investigation priority score">
          <PriorityScore score={entity.score} breakdown={entity.scoreBreakdown} />
        </Panel>

        <Panel title="Relationship network" subtitle="Click a node to inspect its relationship metadata" bodyClassName="p-3">
          <GraphView
            className="h-[380px]"
            filters={{ nodeTypes: [...NODE_TYPES], edgeTypes: [...EDGE_TYPES], query: "" }}
            selectedId={entity.id}
            focusId={entity.id}
            onSelect={(id) => setDrawerId(id)}
          />
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Panel title="Activity timeline" bodyClassName="p-4">
          {events.length === 0 ? (
            <p className="text-xs text-muted-foreground">
              No incident-window events recorded for this entity.
            </p>
          ) : (
            <ol className="space-y-2">
              {events.map((e) => (
                <li key={e.id} className="rounded-sm border border-border bg-secondary/30 p-2.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-foreground">{e.time}</span>
                    <DomainTag domain={e.domain} />
                  </div>
                  <div className="mt-1 text-xs text-foreground">{e.title}</div>
                  <p className="text-[11px] text-muted-foreground">{e.detail}</p>
                </li>
              ))}
            </ol>
          )}
          <Button asChild size="sm" variant="ghost" className="mt-3 px-0">
            <Link to="/timeline">Open full timeline</Link>
          </Button>
        </Panel>

        <Panel title="Analytical findings" bodyClassName="p-4">
          {entity.findings.length === 0 && anos.length === 0 ? (
            <p className="text-xs text-muted-foreground">
              No analytical findings recorded. This entity is retained for network completeness.
            </p>
          ) : (
            <>
              <ul className="space-y-1.5">
                {entity.findings.map((f) => (
                  <li key={f} className="flex gap-2 text-xs text-foreground">
                    <span className="text-primary">▸</span>
                    {f}
                  </li>
                ))}
              </ul>
              {anos.length > 0 && (
                <div className="mt-3 space-y-2">
                  <div className="label-xs">Linked anomalies</div>
                  {anos.map((a) => (
                    <div key={a.id} className="rounded-sm border border-border bg-secondary/30 p-2.5">
                      <div className="flex items-center gap-2">
                        <SeverityBadge severity={a.severity} />
                        <span className="text-xs font-medium text-foreground">{a.title}</span>
                      </div>
                      <p className="mt-1 text-[11px] text-muted-foreground">{a.pattern}</p>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
          <p className="mt-3 text-[11px] text-muted-foreground">
            Findings are analytical observations that require review; they do not establish wrongdoing.
          </p>
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Panel title="Financial relationships" bodyClassName="p-0">
          {txns.length === 0 ? (
            <p className="p-4 text-xs text-muted-foreground">No transactions linked to this entity.</p>
          ) : (
            <table className="w-full text-xs">
              <thead className="border-b border-border text-left text-muted-foreground">
                <tr>
                  <th className="px-4 py-2 font-medium">Timestamp</th>
                  <th className="px-4 py-2 font-medium">Counterparty</th>
                  <th className="px-4 py-2 font-medium">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border font-mono">
                {txns.map((t) => (
                  <tr key={t.id}>
                    <td className="px-4 py-2">{t.timestamp}</td>
                    <td className="px-4 py-2">{t.sender === entity.id ? t.receiver : t.sender}</td>
                    <td className="px-4 py-2 text-financial">{inr(t.amount)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Panel>

        <Panel title="Relationship set" bodyClassName="space-y-1.5 p-3">
          {rels.map((r) => (
            <div key={r.id} className="rounded-sm border border-border bg-secondary/30 p-2.5">
              <div className="flex items-center justify-between font-mono text-[11px]">
                <span className="text-foreground">{r.source === entity.id ? r.target : r.source}</span>
                <span className="text-primary">{r.type}</span>
              </div>
              <p className="mt-0.5 text-[11px] text-muted-foreground">{r.note}</p>
            </div>
          ))}
        </Panel>
      </div>

      <EntityDrawer entityId={drawerId} onOpenChange={(o) => !o && setDrawerId(null)} />
    </div>
  );
}
