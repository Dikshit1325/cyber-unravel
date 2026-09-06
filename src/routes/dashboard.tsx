import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowUpRight, FilePlus2, Network, ShieldAlert, Sparkles } from "lucide-react";
import {
  DomainTag,
  KpiCard,
  Panel,
  SeverityBadge,
  domainColor,
} from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import {
  actionableLead,
  alerts,
  cases,
  hiddenRelationships,
  kpis,
  timelineEvents,
} from "@/lib/mock-data";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Command Center — SENTINEL Investigation Intelligence" },
      {
        name: "description",
        content:
          "Cross-domain intelligence across telecom, financial and digital footprints: live alerts, active cases and actionable investigative leads.",
      },
      { property: "og:title", content: "Digital Investigation Command Center" },
      {
        property: "og:description",
        content: "From scattered data to actionable intelligence — unified investigation analytics.",
      },
    ],
  }),
  component: CommandCenter,
});

function CommandCenter() {
  return (
    <div className="space-y-5">
      <section className="panel grid-bg relative overflow-hidden p-6">
        <div className="relative">
          <p className="label-xs">Digital Investigation Intelligence Platform</p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-foreground lg:text-3xl">
            Digital Investigation Command Center
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
            Cross-domain intelligence across telecom, financial and digital footprints.{" "}
            <span className="text-primary">Uncovering the truth hidden in the data.</span>
          </p>
          <div className="mt-5 flex flex-wrap gap-2">
            <Button asChild>
              <Link to="/graph">
                Open Investigation
                <Network className="size-4" />
              </Link>
            </Button>
            <Button asChild variant="outline">
              <Link to="/cases">
                Create New Case
                <FilePlus2 className="size-4" />
              </Link>
            </Button>
          </div>
          <p className="mt-4 max-w-2xl text-[11px] text-muted-foreground">
            Analytical and investigative support system operating on authorized, imported and synthetic
            demonstration datasets. Outputs are investigative leads that require review — they do not
            establish guilt.
          </p>
        </div>
      </section>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        {kpis.map((k) => (
          <KpiCard key={k.label} {...k} />
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <Panel
          title="Active investigations"
          subtitle="Cases with open analytical findings"
          className="xl:col-span-2"
          bodyClassName="p-0"
          action={
            <Button asChild variant="ghost" size="sm">
              <Link to="/cases">All cases</Link>
            </Button>
          }
        >
          <div className="divide-y divide-border">
            {cases.slice(0, 4).map((c) => (
              <div key={c.id} className="flex flex-wrap items-center gap-4 px-4 py-3.5">
                <div className="min-w-56 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-primary">{c.id}</span>
                    <SeverityBadge severity={c.priority} />
                  </div>
                  <div className="mt-1 text-sm font-medium text-foreground">{c.name}</div>
                  <div className="mt-0.5 text-xs text-muted-foreground">
                    {c.type} · {c.status} · last activity {c.lastActivity}
                  </div>
                </div>
                <div className="flex gap-6 font-mono text-xs">
                  <div>
                    <div className="label-xs">Entities</div>
                    <div className="text-foreground">{c.entities.toLocaleString("en-IN")}</div>
                  </div>
                  <div>
                    <div className="label-xs">Alerts</div>
                    <div className="text-sev-high">{c.alerts}</div>
                  </div>
                </div>
                <Button asChild size="sm" variant="outline">
                  <Link to="/graph">Open Investigation</Link>
                </Button>
              </div>
            ))}
          </div>
        </Panel>

        <Panel
          title="Live alert feed"
          subtitle="Anomalies awaiting investigator review"
          bodyClassName="space-y-2.5 p-3"
        >
          {alerts.map((a) => (
            <div
              key={a.id}
              className="rounded-sm border border-border bg-secondary/40 p-3 transition-colors hover:border-primary/40"
            >
              <div className="flex items-center gap-2">
                <SeverityBadge severity={a.severity} />
                <span className="text-sm font-medium text-foreground">{a.title}</span>
              </div>
              <div className="mt-1 font-mono text-[11px] text-muted-foreground">{a.entity}</div>
              <p className="mt-1.5 text-xs text-muted-foreground">{a.detail}</p>
              <div className="mt-2.5 flex items-center justify-between">
                <span className="font-mono text-[10px] text-muted-foreground">{a.detectedAt}</span>
                <Button asChild size="sm" variant="ghost" className="h-7 text-xs">
                  <Link to="/anomalies">
                    View Investigation
                    <ArrowUpRight className="size-3" />
                  </Link>
                </Button>
              </div>
            </div>
          ))}
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <Panel
          title="Actionable investigative lead"
          subtitle="Generated from cross-domain correlation"
          className="xl:col-span-2 border-primary/30"
        >
          <div className="flex items-start gap-3">
            <span className="mt-0.5 grid size-8 shrink-0 place-items-center rounded-sm border border-primary/40 bg-primary/12 text-primary">
              <Sparkles className="size-4" aria-hidden />
            </span>
            <div>
              <p className="text-sm leading-relaxed text-foreground">{actionableLead.headline}</p>
              <ul className="mt-3 space-y-1.5">
                {actionableLead.supporting.map((s) => (
                  <li key={s} className="flex gap-2 text-xs text-muted-foreground">
                    <span className="text-primary">▸</span>
                    {s}
                  </li>
                ))}
              </ul>
              <div className="mt-4 flex flex-wrap gap-2">
                <Button asChild size="sm">
                  <Link to="/entities/$entityId" params={{ entityId: actionableLead.entityId }}>
                    Open {actionableLead.entityId}
                  </Link>
                </Button>
                <Button asChild size="sm" variant="outline">
                  <Link to="/timeline">Reconstruct timeline</Link>
                </Button>
                <Button asChild size="sm" variant="ghost">
                  <Link to="/reports">Generate report</Link>
                </Button>
              </div>
            </div>
          </div>
        </Panel>

        <Panel title="Hidden relationships" subtitle="Discovered across datasets" bodyClassName="space-y-2 p-3">
          {hiddenRelationships.map((h) => (
            <div key={h.id} className="rounded-sm border border-border bg-secondary/40 p-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-foreground">{h.title}</span>
                <SeverityBadge severity={h.strength} />
              </div>
              <p className="mt-1 font-mono text-[11px] text-primary">
                {h.entityId}: {h.clusterA} ↔ {h.clusterB}
              </p>
              <Button asChild size="sm" variant="ghost" className="mt-2 h-7 px-0 text-xs">
                <Link to="/clusters">Explore Relationship</Link>
              </Button>
            </div>
          ))}
        </Panel>
      </div>

      <Panel
        title="Incident window snapshot"
        subtitle="16 Aug 2026 · 18:00 – 20:00"
        action={
          <Button asChild variant="ghost" size="sm">
            <Link to="/timeline">Full timeline</Link>
          </Button>
        }
      >
        <ol className="grid gap-2 md:grid-cols-2 xl:grid-cols-4">
          {timelineEvents.slice(0, 8).map((e) => (
            <li key={e.id} className="rounded-sm border border-border bg-secondary/30 p-3">
              <div className="flex items-center justify-between">
                <span className={`font-mono text-xs ${domainColor[e.domain]}`}>{e.time}</span>
                <DomainTag domain={e.domain} />
              </div>
              <div className="mt-1.5 text-xs font-medium text-foreground">{e.title}</div>
              <p className="mt-0.5 text-[11px] text-muted-foreground">{e.detail}</p>
            </li>
          ))}
        </ol>
      </Panel>

      <p className="flex items-center gap-2 text-[11px] text-muted-foreground">
        <ShieldAlert className="size-3.5 text-sev-medium" aria-hidden />
        Prototype workspace populated with synthetic investigation data for demonstration.
      </p>
    </div>
  );
}
