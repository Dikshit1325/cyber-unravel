import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Search, Sparkles } from "lucide-react";
import {
  EDGE_TYPES,
  GraphView,
  NODE_TYPES,
} from "@/components/investigation/GraphView";
import { EntityDrawer } from "@/components/investigation/EntityDrawer";
import { PageHeader, Panel, SeverityBadge } from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { clusters, entities, hiddenRelationships, primaryCase } from "@/lib/mock-data";
import type { EntityType, RelationshipType } from "@/lib/types";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

export const Route = createFileRoute("/graph")({
  head: () => ({
    meta: [
      { title: "Investigation Graph — SENTINEL" },
      {
        name: "description",
        content:
          "Interactive relationship graph linking persons, phones, accounts, social profiles, devices and IP records.",
      },
      { property: "og:title", content: "Investigation Relationship Graph" },
      {
        property: "og:description",
        content: "Explore connected entities, clusters and bridge relationships across data domains.",
      },
    ],
  }),
  component: GraphPage,
});

function GraphPage() {
  const [nodeTypes, setNodeTypes] = useState<EntityType[]>([...NODE_TYPES]);
  const [edgeTypes, setEdgeTypes] = useState<RelationshipType[]>([...EDGE_TYPES]);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<string | null>("ENT-1092");
  const [drawerId, setDrawerId] = useState<string | null>(null);
  const [focusId, setFocusId] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string[]>([]);

  const toggle = <T,>(list: T[], value: T, set: (v: T[]) => void) =>
    set(list.includes(value) ? list.filter((v) => v !== value) : [...list, value]);

  return (
    <div className="space-y-4">
      <PageHeader
        title="Investigation Graph"
        subtitle={`${primaryCase.id} · relationships derived from authorized CDR, IPDR, bank statement and public social datasets.`}
        action={
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setFocusId(null);
                setExpanded([]);
                setQuery("");
                toast("Graph reset to full network view");
              }}
            >
              Reset view
            </Button>
            <Button
              onClick={() => {
                setSelected("ENT-1092");
                setFocusId("ENT-1092");
                toast.success("Focused on bridge entity ENT-1092");
              }}
            >
              <Sparkles className="size-4" />
              Focus bridge entity
            </Button>
          </div>
        }
      />

      <div className="grid gap-4 xl:grid-cols-[240px_1fr_260px]">
        <div className="space-y-3">
          <Panel title="Search entity" bodyClassName="p-3">
            <div className="relative">
              <Search
                className="absolute top-2.5 left-2.5 size-3.5 text-muted-foreground"
                aria-hidden
              />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="ENT-1092, AC-48291…"
                className="h-9 pl-8 font-mono text-xs"
                aria-label="Search graph entity"
              />
            </div>
            {query && !entities.some((e) => e.id.toLowerCase().includes(query.toLowerCase())) && (
              <p className="mt-2 text-[11px] text-sev-medium">
                No entity matches “{query}”. Check the identifier or import the related dataset.
              </p>
            )}
          </Panel>

          <Panel title="Node types" bodyClassName="flex flex-wrap gap-1.5 p-3">
            {NODE_TYPES.map((t) => (
              <FilterChip
                key={t}
                active={nodeTypes.includes(t)}
                onClick={() => toggle(nodeTypes, t, setNodeTypes)}
                label={t}
              />
            ))}
          </Panel>

          <Panel title="Relationship types" bodyClassName="flex flex-wrap gap-1.5 p-3">
            {EDGE_TYPES.map((t) => (
              <FilterChip
                key={t}
                active={edgeTypes.includes(t)}
                onClick={() => toggle(edgeTypes, t, setEdgeTypes)}
                label={t}
              />
            ))}
          </Panel>
        </div>

        <GraphView
          className="h-[560px] xl:h-[680px]"
          filters={{ nodeTypes, edgeTypes, query }}
          selectedId={selected}
          focusId={focusId}
          expandedIds={expanded}
          onSelect={(id) => {
            setSelected(id);
            setDrawerId(id);
          }}
        />

        <div className="space-y-3">
          <Panel title="Clusters" bodyClassName="space-y-2 p-3">
            {clusters.map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => {
                  setSelected(c.centralEntity);
                  setDrawerId(null);
                  toast(`${c.name} highlighted`, { description: `Central entity ${c.centralEntity}` });
                }}
                className="w-full rounded-sm border border-border bg-secondary/40 p-2.5 text-left transition-colors hover:border-primary/40"
              >
                <div className="flex items-center justify-between font-mono text-[11px]">
                  <span className="text-foreground">{c.name}</span>
                  <span className="text-muted-foreground">{c.entityCount} entities</span>
                </div>
                <p className="mt-1 text-[11px] text-muted-foreground">Central: {c.centralEntity}</p>
              </button>
            ))}
          </Panel>

          <Panel title="Hidden relationships" bodyClassName="space-y-2 p-3">
            {hiddenRelationships.map((h) => (
              <div key={h.id} className="rounded-sm border border-border bg-secondary/40 p-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-foreground">{h.title}</span>
                  <SeverityBadge severity={h.strength} />
                </div>
                <p className="mt-1 font-mono text-[11px] text-primary">{h.entityId}</p>
                <ul className="mt-1 space-y-0.5">
                  {h.evidence.map((e) => (
                    <li key={e} className="text-[11px] text-muted-foreground">
                      · {e}
                    </li>
                  ))}
                </ul>
                <Button
                  size="sm"
                  variant="ghost"
                  className="mt-1.5 h-7 px-0 text-xs"
                  onClick={() => {
                    setSelected(h.entityId);
                    setFocusId(h.entityId);
                    setDrawerId(h.entityId);
                  }}
                >
                  Explore Relationship
                </Button>
              </div>
            ))}
          </Panel>
        </div>
      </div>

      <EntityDrawer
        entityId={drawerId}
        onOpenChange={(open) => !open && setDrawerId(null)}
        expanded={drawerId ? expanded.includes(drawerId) : false}
        onExpand={(id) => {
          setFocusId(id);
          setExpanded((prev) => (prev.includes(id) ? prev : [...prev, id]));
          toast.success(`Expanded relationships for ${id}`);
        }}
        onCollapse={(id) => {
          setExpanded((prev) => prev.filter((v) => v !== id));
          toast(`Collapsed relationships for ${id}`);
        }}
      />
    </div>
  );
}

function FilterChip({
  active,
  onClick,
  label,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      aria-pressed={active}
      onClick={onClick}
      className={cn(
        "rounded-sm border px-1.5 py-1 font-mono text-[10px] transition-colors",
        active
          ? "border-primary/50 bg-primary/12 text-primary"
          : "border-border text-muted-foreground hover:text-foreground",
      )}
    >
      {label}
    </button>
  );
}
