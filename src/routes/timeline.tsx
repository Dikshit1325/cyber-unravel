import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Clock } from "lucide-react";
import {
  DomainTag,
  PageHeader,
  Panel,
  SeverityBadge,
  StatRow,
} from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cases, entities, timelineEvents } from "@/lib/mock-data";
import type { TimelineEvent } from "@/lib/types";

export const Route = createFileRoute("/timeline")({
  head: () => ({
    meta: [
      { title: "Incident Timeline Reconstruction — SENTINEL" },
      {
        name: "description",
        content:
          "Reconstruct a chronological cross-domain sequence of calls, transfers, sessions and public activity within an incident window.",
      },
      { property: "og:title", content: "Incident Timeline Reconstruction" },
      {
        property: "og:description",
        content: "Chronological cross-domain event reconstruction for a selected incident window.",
      },
    ],
  }),
  component: TimelinePage,
});

function TimelinePage() {
  const [caseId, setCaseId] = useState(cases[0]!.id);
  const [entityId, setEntityId] = useState("All entities");
  const [from, setFrom] = useState("18:00");
  const [to, setTo] = useState("20:00");
  const [active, setActive] = useState<TimelineEvent | null>(null);

  const filtered = useMemo(
    () =>
      timelineEvents.filter((e) => {
        const inWindow = e.time >= from && e.time <= to;
        const matchEntity = entityId === "All entities" || e.entityIds.includes(entityId);
        return inWindow && matchEntity;
      }),
    [from, to, entityId],
  );

  return (
    <div className="space-y-5">
      <PageHeader
        title="Incident Timeline Reconstruction"
        subtitle="Sequence authorized telecom, financial, social and network records into one chronological narrative."
      />

      <Panel title="Reconstruction parameters" bodyClassName="grid gap-3 p-4 md:grid-cols-4">
        <div className="space-y-1.5">
          <Label htmlFor="case">Case</Label>
          <select
            id="case"
            value={caseId}
            onChange={(e) => setCaseId(e.target.value)}
            className="h-9 w-full rounded-md border border-input bg-background px-2 font-mono text-xs"
          >
            {cases.map((c) => (
              <option key={c.id} value={c.id}>
                {c.id}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="ent">Entity</Label>
          <select
            id="ent"
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            className="h-9 w-full rounded-md border border-input bg-background px-2 font-mono text-xs"
          >
            <option>All entities</option>
            {entities.map((e) => (
              <option key={e.id} value={e.id}>
                {e.id}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="start">Window start</Label>
          <Input id="start" type="time" value={from} onChange={(e) => setFrom(e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="end">Window end</Label>
          <Input id="end" type="time" value={to} onChange={(e) => setTo(e.target.value)} />
        </div>
      </Panel>

      <div className="grid gap-4 xl:grid-cols-[1fr_280px]">
        <Panel
          title="Incident window"
          subtitle={`16 Aug 2026 · ${from} – ${to} · ${filtered.length} events`}
        >
          {filtered.length === 0 ? (
            <div className="rounded-md border border-dashed border-border px-6 py-12 text-center">
              <p className="text-sm font-medium text-foreground">No events in this window</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Widen the window or clear the entity filter to reconstruct more activity.
              </p>
              <Button
                variant="outline"
                size="sm"
                className="mt-4"
                onClick={() => {
                  setFrom("00:00");
                  setTo("23:59");
                  setEntityId("All entities");
                }}
              >
                Reset filters
              </Button>
            </div>
          ) : (
            <ol className="relative space-y-0 border-l border-border pl-6">
              {filtered.map((e) => (
                <li key={e.id} className="relative pb-5">
                  <span className="absolute top-1.5 -left-[27px] size-2.5 rounded-full border border-primary bg-background" />
                  <button
                    type="button"
                    onClick={() => setActive(e)}
                    className="w-full rounded-sm border border-border bg-secondary/30 p-3 text-left transition-colors hover:border-primary/40"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-sm text-foreground">{e.time}</span>
                      <DomainTag domain={e.domain} />
                      {e.severity && <SeverityBadge severity={e.severity} />}
                    </div>
                    <div className="mt-1 text-sm font-medium text-foreground">{e.title}</div>
                    <p className="mt-0.5 text-xs text-muted-foreground">{e.detail}</p>
                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                      {e.entityIds.map((id) => (
                        <span
                          key={id}
                          className="rounded-sm border border-border px-1.5 font-mono text-[10px] text-muted-foreground"
                        >
                          {id}
                        </span>
                      ))}
                    </div>
                  </button>
                </li>
              ))}
            </ol>
          )}
        </Panel>

        <div className="space-y-3">
          <Panel title="Window summary" bodyClassName="p-4">
            <StatRow label="Case" value={caseId} />
            <StatRow label="Events" value={filtered.length} />
            <StatRow
              label="Financial events"
              value={filtered.filter((e) => e.domain === "Financial").length}
            />
            <StatRow
              label="Telecom events"
              value={filtered.filter((e) => e.domain === "Telecom").length}
            />
            <StatRow
              label="High severity"
              value={filtered.filter((e) => e.severity === "HIGH").length}
            />
          </Panel>
          <Panel title="Reconstruction reading" bodyClassName="p-4">
            <p className="text-xs leading-relaxed text-muted-foreground">
              Communication activity precedes each flagged transfer by 8–13 minutes, and a session record
              appears between the two transfer legs. This ordering is an analytical observation for review,
              not a conclusion.
            </p>
            <Button asChild size="sm" className="mt-3">
              <Link to="/reports">Add to investigation report</Link>
            </Button>
          </Panel>
        </div>
      </div>

      <Dialog open={Boolean(active)} onOpenChange={(o) => !o && setActive(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 font-mono text-base">
              <Clock className="size-4 text-primary" aria-hidden />
              {active?.date} {active?.time}
            </DialogTitle>
          </DialogHeader>
          {active && (
            <div className="space-y-3">
              <div className="flex gap-2">
                <DomainTag domain={active.domain} />
                {active.severity && <SeverityBadge severity={active.severity} />}
              </div>
              <div>
                <div className="label-xs">Event</div>
                <p className="text-sm text-foreground">{active.title}</p>
              </div>
              <div>
                <div className="label-xs">Record detail</div>
                <p className="text-sm text-muted-foreground">{active.detail}</p>
              </div>
              <div>
                <div className="label-xs mb-1">Entities involved</div>
                <div className="flex flex-wrap gap-2">
                  {active.entityIds.map((id) => (
                    <Button key={id} asChild size="sm" variant="outline" className="h-7 font-mono text-xs">
                      <Link to="/entities/$entityId" params={{ entityId: id }}>
                        {id}
                      </Link>
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
