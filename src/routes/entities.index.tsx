import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { PageHeader, Panel, SeverityBadge, DomainTag, entityIcon } from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { entities } from "@/lib/mock-data";
import type { EntityType, Severity } from "@/lib/types";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/entities/")({
  head: () => ({
    meta: [
      { title: "Entities — SENTINEL Investigation Intelligence" },
      {
        name: "description",
        content:
          "Resolved investigation entities across persons, phones, accounts, social profiles, devices and IP records with priority scores.",
      },
      { property: "og:title", content: "Investigation Entities" },
      { property: "og:description", content: "Resolved cross-domain entities and their priority scores." },
    ],
  }),
  component: EntitiesPage,
});

const types: (EntityType | "All")[] = [
  "All",
  "Person",
  "Phone",
  "Bank Account",
  "Social Account",
  "IP Address",
  "Device",
];
const priorities: (Severity | "All")[] = ["All", "HIGH", "MEDIUM", "LOW"];

function EntitiesPage() {
  const [type, setType] = useState<EntityType | "All">("All");
  const [priority, setPriority] = useState<Severity | "All">("All");
  const [q, setQ] = useState("");

  const rows = useMemo(
    () =>
      entities
        .filter((e) => (type === "All" ? true : e.type === type))
        .filter((e) => (priority === "All" ? true : e.priority === priority))
        .filter((e) =>
          q.trim() ? `${e.id} ${e.label}`.toLowerCase().includes(q.trim().toLowerCase()) : true,
        )
        .sort((a, b) => b.score - a.score),
    [type, priority, q],
  );

  return (
    <div className="space-y-5">
      <PageHeader
        title="Entities"
        subtitle="Every identifier observed in the imported datasets, resolved into a single entity view with an explainable priority score."
      />

      <Panel bodyClassName="flex flex-wrap items-center gap-2 p-3">
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Filter by identifier…"
          className="h-8 w-56 font-mono text-xs"
          aria-label="Filter entities"
        />
        <div className="flex flex-wrap gap-1.5">
          {types.map((t) => (
            <Chip key={t} active={type === t} onClick={() => setType(t)} label={t} />
          ))}
        </div>
        <div className="ml-auto flex gap-1.5">
          {priorities.map((p) => (
            <Chip key={p} active={priority === p} onClick={() => setPriority(p)} label={p} />
          ))}
        </div>
      </Panel>

      {rows.length === 0 ? (
        <Panel bodyClassName="p-0">
          <div className="px-6 py-14 text-center">
            <p className="text-sm font-medium text-foreground">No entities match these filters</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Clear the filters or import an additional dataset to widen the entity population.
            </p>
            <Button
              size="sm"
              variant="outline"
              className="mt-4"
              onClick={() => {
                setType("All");
                setPriority("All");
                setQ("");
              }}
            >
              Clear filters
            </Button>
          </div>
        </Panel>
      ) : (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {rows.map((e) => {
            const Icon = entityIcon[e.type];
            return (
              <Link
                key={e.id}
                to="/entities/$entityId"
                params={{ entityId: e.id }}
                className="panel block p-4 transition-colors hover:border-primary/40"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="grid size-7 place-items-center rounded-sm border border-border bg-secondary text-primary">
                      <Icon className="size-3.5" aria-hidden />
                    </span>
                    <div>
                      <div className="font-mono text-xs text-primary">{e.id}</div>
                      <div className="text-xs text-muted-foreground">{e.type}</div>
                    </div>
                  </div>
                  <SeverityBadge severity={e.priority} />
                </div>
                <div className="mt-2.5 text-sm font-medium text-foreground">{e.label}</div>
                <div className="mt-2 flex items-center gap-2">
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-secondary">
                    <div
                      className={cn(
                        "h-full",
                        e.priority === "HIGH"
                          ? "bg-sev-high"
                          : e.priority === "MEDIUM"
                            ? "bg-sev-medium"
                            : "bg-sev-low",
                      )}
                      style={{ width: `${e.score}%` }}
                    />
                  </div>
                  <span className="font-mono text-xs text-foreground">{e.score}</span>
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <DomainTag domain={e.domain} />
                  <span className="font-mono text-[10px] text-muted-foreground">{e.cluster}</span>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

function Chip({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
  return (
    <button
      type="button"
      aria-pressed={active}
      onClick={onClick}
      className={cn(
        "rounded-sm border px-2 py-1 font-mono text-[10px] transition-colors",
        active
          ? "border-primary/50 bg-primary/12 text-primary"
          : "border-border text-muted-foreground hover:text-foreground",
      )}
    >
      {label}
    </button>
  );
}
