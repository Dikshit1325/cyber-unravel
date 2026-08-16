import { useMemo, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { entities, relationships as allRelationships } from "@/lib/mock-data";
import type { Entity, EntityType, Relationship, RelationshipType } from "@/lib/types";
import { entityIcon } from "./primitives";

const RADIUS_BY_CLUSTER: Record<string, { cx: number; cy: number; r: number }> = {
  "CL-01": { cx: 300, cy: 250, r: 165 },
  "CL-02": { cx: 700, cy: 210, r: 145 },
  "CL-03": { cx: 520, cy: 470, r: 120 },
};

export const NODE_TYPES: EntityType[] = [
  "Person",
  "Phone",
  "Bank Account",
  "Social Account",
  "IP Address",
  "Device",
];

export const EDGE_TYPES: RelationshipType[] = [
  "CALLED",
  "TRANSFERRED_TO",
  "USES",
  "OWNS",
  "CONNECTED_TO",
  "ASSOCIATED_WITH",
  "LOGGED_FROM",
  "COMMUNICATED_WITH",
];

const typeColor: Record<EntityType, string> = {
  Person: "var(--primary)",
  Phone: "var(--telecom)",
  "Bank Account": "var(--financial)",
  "Social Account": "var(--social)",
  "IP Address": "var(--network)",
  Device: "var(--muted-foreground)",
  Transaction: "var(--financial)",
  Location: "var(--muted-foreground)",
};

function layout(list: Entity[]) {
  const grouped = new Map<string, Entity[]>();
  for (const e of list) {
    const arr = grouped.get(e.cluster) ?? [];
    arr.push(e);
    grouped.set(e.cluster, arr);
  }
  const positions = new Map<string, { x: number; y: number }>();
  for (const [cluster, members] of grouped) {
    const geo = RADIUS_BY_CLUSTER[cluster] ?? { cx: 500, cy: 350, r: 150 };
    members.forEach((m, i) => {
      const angle = (i / members.length) * Math.PI * 2 - Math.PI / 2;
      const isHub = m.type === "Person" && i === 0;
      const r = isHub ? geo.r * 0.18 : geo.r * (m.type === "Person" ? 0.6 : 1);
      positions.set(m.id, { x: geo.cx + Math.cos(angle) * r, y: geo.cy + Math.sin(angle) * r });
    });
  }
  return positions;
}

export interface GraphFilters {
  nodeTypes: EntityType[];
  edgeTypes: RelationshipType[];
  query: string;
}

export function GraphView({
  filters,
  selectedId,
  onSelect,
  focusId,
  expandedIds,
  className,
}: {
  filters: GraphFilters;
  selectedId: string | null;
  onSelect: (id: string) => void;
  focusId?: string | null;
  expandedIds?: string[];
  className?: string;
}) {
  const [view, setView] = useState({ x: 0, y: 0, k: 1 });
  const drag = useRef<{ x: number; y: number } | null>(null);

  const { nodes, edges, positions } = useMemo(() => {
    let visible = entities.filter((e) => filters.nodeTypes.includes(e.type));
    if (filters.query.trim()) {
      const q = filters.query.trim().toLowerCase();
      const matched = visible.filter(
        (e) => e.id.toLowerCase().includes(q) || e.label.toLowerCase().includes(q),
      );
      const keep = new Set<string>();
      matched.forEach((m) => {
        keep.add(m.id);
        allRelationships.forEach((r) => {
          if (r.source === m.id) keep.add(r.target);
          if (r.target === m.id) keep.add(r.source);
        });
      });
      visible = visible.filter((e) => keep.has(e.id));
    }
    if (focusId) {
      const keep = new Set<string>([focusId]);
      allRelationships.forEach((r) => {
        if (r.source === focusId) keep.add(r.target);
        if (r.target === focusId) keep.add(r.source);
      });
      (expandedIds ?? []).forEach((id) => {
        keep.add(id);
        allRelationships.forEach((r) => {
          if (r.source === id) keep.add(r.target);
          if (r.target === id) keep.add(r.source);
        });
      });
      visible = visible.filter((e) => keep.has(e.id));
    }
    const ids = new Set(visible.map((e) => e.id));
    const visibleEdges = allRelationships.filter(
      (r) => ids.has(r.source) && ids.has(r.target) && filters.edgeTypes.includes(r.type),
    );
    return { nodes: visible, edges: visibleEdges, positions: layout(visible) };
  }, [filters, focusId, expandedIds]);

  const highlighted = useMemo(() => {
    if (!selectedId) return new Set<string>();
    const set = new Set<string>([selectedId]);
    edges.forEach((e) => {
      if (e.source === selectedId) set.add(e.target);
      if (e.target === selectedId) set.add(e.source);
    });
    return set;
  }, [selectedId, edges]);

  return (
    <div className={cn("relative overflow-hidden rounded-md border border-border bg-panel", className)}>
      <div className="grid-bg absolute inset-0 opacity-70" aria-hidden />
      <svg
        role="img"
        aria-label="Investigation relationship graph"
        viewBox="0 0 1000 700"
        className="relative size-full cursor-grab active:cursor-grabbing"
        onWheel={(e) => {
          e.preventDefault();
          setView((v) => ({ ...v, k: Math.min(2.6, Math.max(0.5, v.k * (e.deltaY < 0 ? 1.12 : 0.9))) }));
        }}
        onPointerDown={(e) => {
          drag.current = { x: e.clientX, y: e.clientY };
        }}
        onPointerMove={(e) => {
          if (!drag.current) return;
          const dx = e.clientX - drag.current.x;
          const dy = e.clientY - drag.current.y;
          drag.current = { x: e.clientX, y: e.clientY };
          setView((v) => ({ ...v, x: v.x + dx, y: v.y + dy }));
        }}
        onPointerUp={() => {
          drag.current = null;
        }}
        onPointerLeave={() => {
          drag.current = null;
        }}
      >
        <g transform={`translate(${view.x} ${view.y}) scale(${view.k})`}>
          {Object.entries(RADIUS_BY_CLUSTER).map(([id, geo]) => (
            <g key={id}>
              <circle
                cx={geo.cx}
                cy={geo.cy}
                r={geo.r + 34}
                fill="oklch(1 0 0 / 2%)"
                stroke="var(--border)"
                strokeDasharray="4 6"
              />
              <text
                x={geo.cx}
                y={geo.cy - geo.r - 44}
                textAnchor="middle"
                className="fill-muted-foreground font-mono text-[11px] tracking-widest"
              >
                {id}
              </text>
            </g>
          ))}

          {edges.map((edge) => {
            const a = positions.get(edge.source);
            const b = positions.get(edge.target);
            if (!a || !b) return null;
            const dim = selectedId && !(highlighted.has(edge.source) && highlighted.has(edge.target));
            const mx = (a.x + b.x) / 2;
            const my = (a.y + b.y) / 2;
            return (
              <g key={edge.id} opacity={dim ? 0.15 : 1}>
                <line
                  x1={a.x}
                  y1={a.y}
                  x2={b.x}
                  y2={b.y}
                  stroke={edge.type === "TRANSFERRED_TO" ? "var(--financial)" : "var(--border)"}
                  strokeWidth={edge.weight >= 5 ? 1.8 : 1.1}
                />
                {(!selectedId || !dim) && (
                  <text
                    x={mx}
                    y={my - 4}
                    textAnchor="middle"
                    className="fill-muted-foreground font-mono"
                    fontSize={7.5}
                  >
                    {edge.type}
                  </text>
                )}
              </g>
            );
          })}

          {nodes.map((node) => {
            const p = positions.get(node.id);
            if (!p) return null;
            const Icon = entityIcon[node.type];
            const isSelected = selectedId === node.id;
            const dim = selectedId ? !highlighted.has(node.id) : false;
            const size = node.type === "Person" ? 19 : 15;
            return (
              <g
                key={node.id}
                transform={`translate(${p.x} ${p.y})`}
                opacity={dim ? 0.25 : 1}
                className="cursor-pointer"
                tabIndex={0}
                role="button"
                aria-label={`${node.id} ${node.type}`}
                onClick={() => onSelect(node.id)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") onSelect(node.id);
                }}
              >
                {node.priority === "HIGH" && (
                  <circle r={size + 8} fill="var(--sev-high)" opacity={0.12} />
                )}
                <circle
                  r={size}
                  fill="var(--card)"
                  stroke={isSelected ? "var(--primary)" : typeColor[node.type]}
                  strokeWidth={isSelected ? 2.6 : 1.4}
                />
                <foreignObject x={-8} y={-8} width={16} height={16}>
                  <div className="flex size-4 items-center justify-center">
                    <Icon className="size-3.5" style={{ color: typeColor[node.type] }} aria-hidden />
                  </div>
                </foreignObject>
                <text
                  y={size + 12}
                  textAnchor="middle"
                  className="fill-foreground font-mono"
                  fontSize={9}
                >
                  {node.id}
                </text>
              </g>
            );
          })}
        </g>
      </svg>

      <div className="absolute right-3 bottom-3 flex flex-col gap-1">
        {[
          { label: "+", fn: () => setView((v) => ({ ...v, k: Math.min(2.6, v.k * 1.2) })) },
          { label: "−", fn: () => setView((v) => ({ ...v, k: Math.max(0.5, v.k / 1.2) })) },
          { label: "⟲", fn: () => setView({ x: 0, y: 0, k: 1 }) },
        ].map((b) => (
          <button
            key={b.label}
            type="button"
            onClick={b.fn}
            aria-label={`Zoom ${b.label}`}
            className="grid size-7 place-items-center rounded-sm border border-border bg-card text-sm text-muted-foreground hover:text-foreground"
          >
            {b.label}
          </button>
        ))}
      </div>

      <div className="absolute bottom-3 left-3 flex flex-wrap gap-2 rounded-sm border border-border bg-card/90 p-2">
        {NODE_TYPES.map((t) => (
          <span key={t} className="flex items-center gap-1.5 font-mono text-[10px] text-muted-foreground">
            <span className="size-2 rounded-full" style={{ background: typeColor[t] }} />
            {t}
          </span>
        ))}
      </div>

      <div className="absolute top-3 left-3 rounded-sm border border-border bg-card/90 px-2 py-1 font-mono text-[10px] text-muted-foreground">
        {nodes.length} nodes · {edges.length} relationships
      </div>
    </div>
  );
}

export function edgeLabel(r: Relationship) {
  return `${r.source} —${r.type}→ ${r.target}`;
}
