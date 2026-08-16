import { Link } from "@tanstack/react-router";
import { ArrowUpRight, ChevronRight, Minimize2, Maximize2 } from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import {
  anomaliesFor,
  communicationsFor,
  getEntity,
  neighborsOf,
  relationshipsFor,
  transactionsFor,
} from "@/lib/mock-data";
import { DomainTag, PriorityScore, SeverityBadge, StatRow, entityIcon } from "./primitives";

export function EntityDrawer({
  entityId,
  onOpenChange,
  onExpand,
  onCollapse,
  expanded,
}: {
  entityId: string | null;
  onOpenChange: (open: boolean) => void;
  onExpand?: (id: string) => void;
  onCollapse?: (id: string) => void;
  expanded?: boolean;
}) {
  const entity = entityId ? getEntity(entityId) : undefined;
  if (!entity) return null;
  const Icon = entityIcon[entity.type];
  const rels = relationshipsFor(entity.id);
  const neighbors = neighborsOf(entity.id);

  return (
    <Sheet open={Boolean(entityId)} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full overflow-y-auto sm:max-w-md">
        <SheetHeader className="border-b border-border pb-4">
          <div className="flex items-center gap-2">
            <span className="grid size-8 place-items-center rounded-sm border border-primary/40 bg-primary/12 text-primary">
              <Icon className="size-4" aria-hidden />
            </span>
            <div>
              <SheetTitle className="font-mono text-base">ENTITY {entity.id}</SheetTitle>
              <p className="text-xs text-muted-foreground">{entity.label}</p>
            </div>
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            <DomainTag domain={entity.domain} />
            <SeverityBadge severity={entity.priority} label={`${entity.priority} PRIORITY`} />
            <span className="rounded-sm border border-border px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
              {entity.cluster}
            </span>
          </div>
        </SheetHeader>

        <div className="space-y-5 px-4 pb-8">
          <div>
            <div className="label-xs mb-2">Investigation Priority Score</div>
            <PriorityScore score={entity.score} breakdown={entity.scoreBreakdown} />
          </div>

          <div>
            <div className="label-xs mb-1">Footprint</div>
            <StatRow label="Type" value={entity.type} />
            <StatRow label="Connected Entities" value={neighbors.length} />
            <StatRow label="Transactions" value={transactionsFor(entity.id).length || entity.activity.transactions} />
            <StatRow label="Communications" value={communicationsFor(entity.id).length || entity.activity.calls} />
            <StatRow label="Anomalies" value={anomaliesFor(entity.id).length} />
            <StatRow label="Relationships" value={rels.length} />
          </div>

          {entity.findings.length > 0 && (
            <div>
              <div className="label-xs mb-2">Why this entity is high priority</div>
              <ul className="space-y-1.5">
                {entity.findings.map((f) => (
                  <li key={f} className="flex gap-2 text-xs leading-relaxed text-foreground">
                    <ChevronRight className="mt-0.5 size-3.5 shrink-0 text-primary" aria-hidden />
                    {f}
                  </li>
                ))}
              </ul>
              <p className="mt-2 text-[11px] text-muted-foreground">
                Analytical findings only — these do not establish wrongdoing and require review.
              </p>
            </div>
          )}

          <div>
            <div className="label-xs mb-2">Relationship metadata</div>
            <div className="space-y-1.5">
              {rels.map((r) => (
                <div key={r.id} className="rounded-sm border border-border bg-secondary/40 p-2">
                  <div className="flex items-center justify-between font-mono text-[11px]">
                    <span className="text-foreground">
                      {r.source === entity.id ? r.target : r.source}
                    </span>
                    <span className="text-primary">{r.type}</span>
                  </div>
                  <p className="mt-1 text-[11px] text-muted-foreground">
                    {r.note} · {r.observations} observations · first seen {r.firstSeen}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button asChild size="sm">
              <Link to="/entities/$entityId" params={{ entityId: entity.id }}>
                Open entity profile
                <ArrowUpRight className="size-3.5" />
              </Link>
            </Button>
            {onExpand && (
              <Button size="sm" variant="outline" onClick={() => onExpand(entity.id)}>
                <Maximize2 className="size-3.5" />
                Expand relationships
              </Button>
            )}
            {onCollapse && expanded && (
              <Button size="sm" variant="ghost" onClick={() => onCollapse(entity.id)}>
                <Minimize2 className="size-3.5" />
                Collapse
              </Button>
            )}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
