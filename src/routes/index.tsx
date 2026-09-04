import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  Database,
  Fingerprint,
  GitBranch,
  Globe2,
  Lock,
  Network,
  Radar,
  ShieldAlert,
  Wallet,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { CyberGlobe } from "@/components/landing/CyberGlobe";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "SENTINEL — Digital Investigation Intelligence Platform" },
      {
        name: "description",
        content:
          "One analytics platform correlating telecom CDR/IPDR, bank statements and social activity to detect anomalies, uncover hidden patterns and generate actionable investigative leads.",
      },
      { property: "og:title", content: "SENTINEL — Digital Investigation Intelligence" },
      {
        property: "og:description",
        content:
          "From scattered digital footprints to actionable intelligence: cross-domain anomaly detection for investigators.",
      },
    ],
  }),
  component: Landing,
});

const MOTTOS = [
  "From scattered data to actionable intelligence.",
  "Every footprint tells a story. We read all of them.",
  "Correlate telecom, finance and social — in one pane of glass.",
  "Anomalies surface. Patterns connect. Leads emerge.",
];

const FEED = [
  { sev: "HIGH", text: "Layered fund dispersal detected · 7 accounts · ₹41.2L", domain: "Financial" },
  { sev: "HIGH", text: "SIM-box burst pattern · 214 short calls in 9 min", domain: "Telecom" },
  { sev: "MEDIUM", text: "IPDR session overlap across 3 identities · same NAT pool", domain: "Network" },
  { sev: "MEDIUM", text: "Coordinated posting cluster · 12 accounts, 1 device fingerprint", domain: "Social" },
  { sev: "LOW", text: "New cross-domain bridge entity surfaced in cluster C-04", domain: "Cross-Domain" },
  { sev: "HIGH", text: "Mule-account cash-out spike within 6 min of inbound transfer", domain: "Financial" },
];

const CAPABILITIES = [
  {
    icon: Radar,
    title: "Anomaly detection",
    body: "Behavioural baselines per identity flag bursts, dormancy breaks, structuring and impossible-travel signals with an explainable score.",
  },
  {
    icon: Network,
    title: "Link analysis graph",
    body: "Entity-resolved graph across phones, accounts, devices and handles with cluster detection and bridge-node discovery.",
  },
  {
    icon: Wallet,
    title: "Money-flow tracing",
    body: "Follow layered transfers hop by hop across IMPS, UPI, NEFT and cash deposits with timing correlation.",
  },
  {
    icon: GitBranch,
    title: "Cross-domain correlation",
    body: "A call at 18:41, a transfer at 18:47, a post at 18:52 — stitched into one defensible sequence.",
  },
  {
    icon: Database,
    title: "Multi-source ingestion",
    body: "CDR, IPDR, bank statements and social exports normalised, validated and deduplicated on import.",
  },
  {
    icon: Fingerprint,
    title: "Audit-ready output",
    body: "Every query, view and export logged; reports are generated as investigative leads, never verdicts.",
  },
];

function Landing() {
  const [mottoIndex, setMottoIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setMottoIndex((i) => (i + 1) % MOTTOS.length), 3600);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-40 border-b border-border bg-background/85 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center gap-3 px-5 py-3">
          <span className="grid size-8 place-items-center rounded-sm border border-primary/40 bg-primary/12 text-primary">
            <ShieldAlert className="size-4" aria-hidden />
          </span>
          <div className="leading-tight">
            <div className="text-sm font-semibold tracking-widest text-foreground uppercase">
              Sentinel
            </div>
            <div className="text-[10px] tracking-widest text-muted-foreground uppercase">
              Digital Investigation Intelligence
            </div>
          </div>
          <nav className="ml-auto flex items-center gap-2">
            <Button asChild variant="ghost" size="sm">
              <Link to="/auth">Sign in</Link>
            </Button>
            <Button asChild size="sm">
              <Link to="/auth">
                Get access
                <ArrowRight className="size-3.5" />
              </Link>
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero with revolving earth */}
      <section className="relative overflow-hidden">
        <div className="grid-bg absolute inset-0 opacity-60" />
        <CyberGlobe className="pointer-events-none absolute inset-0 size-full opacity-90" />
        <div className="relative mx-auto max-w-7xl px-5 py-24 lg:py-32">
          <div className="max-w-2xl">
            <p className="label-xs flex items-center gap-2">
              <Globe2 className="size-3.5 text-primary" aria-hidden />
              Live cross-domain threat surface
            </p>
            <h1 className="mt-4 text-4xl leading-tight font-semibold tracking-tight text-foreground lg:text-6xl">
              A single analytics platform for the
              <span className="text-primary"> entire digital footprint</span>
            </h1>
            <p
              key={mottoIndex}
              className="mt-5 animate-fade-in font-mono text-base text-primary lg:text-lg"
            >
              “{MOTTOS[mottoIndex]}”
            </p>
            <p className="mt-4 max-w-xl text-sm leading-relaxed text-muted-foreground">
              SENTINEL analyzes telecom CDR/IPDR records, bank statements and social media activity
              together — detecting anomalies, uncovering hidden relationships and producing
              investigative leads that hold up under review.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button asChild size="lg">
                <Link to="/auth">
                  Sign in to command center
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline">
                <Link to="/auth">Create investigator account</Link>
              </Button>
            </div>
            <div className="mt-6 flex flex-wrap gap-x-6 gap-y-2 font-mono text-[11px] text-muted-foreground">
              <span>4 data domains</span>
              <span>· 18.4M records indexed</span>
              <span>· 63 anomaly detectors</span>
              <span>· full audit trail</span>
            </div>
          </div>
        </div>
      </section>

      {/* Live attack / anomaly feed */}
      <section className="border-y border-border bg-panel/60">
        <div className="mx-auto max-w-7xl px-5 py-10">
          <div className="flex items-center gap-2">
            <Activity className="size-4 text-sev-high" aria-hidden />
            <h2 className="text-sm font-semibold tracking-wide text-foreground uppercase">
              Live anomaly & cyber-attack stream
            </h2>
            <span className="ml-2 flex items-center gap-1.5 font-mono text-[10px] text-muted-foreground">
              <span className="size-1.5 animate-pulse rounded-full bg-sev-high" />
              streaming
            </span>
          </div>
          <div className="mt-4 grid gap-2 md:grid-cols-2 xl:grid-cols-3">
            {FEED.map((f) => (
              <div
                key={f.text}
                className="flex items-start gap-3 rounded-sm border border-border bg-secondary/40 p-3 transition-colors hover:border-primary/40"
              >
                <span
                  className={`mt-0.5 rounded-sm border px-1.5 py-0.5 font-mono text-[10px] ${
                    f.sev === "HIGH"
                      ? "border-sev-high/40 bg-sev-high/12 text-sev-high"
                      : f.sev === "MEDIUM"
                        ? "border-sev-medium/40 bg-sev-medium/12 text-sev-medium"
                        : "border-sev-low/40 bg-sev-low/12 text-sev-low"
                  }`}
                >
                  {f.sev}
                </span>
                <div>
                  <p className="text-xs text-foreground">{f.text}</p>
                  <p className="mt-1 font-mono text-[10px] text-muted-foreground">{f.domain}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Capabilities */}
      <section className="mx-auto max-w-7xl px-5 py-16">
        <p className="label-xs">Platform capabilities</p>
        <h2 className="mt-2 text-2xl font-semibold tracking-tight text-foreground lg:text-3xl">
          Built for investigators, not dashboards
        </h2>
        <div className="mt-8 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {CAPABILITIES.map((c) => (
            <article key={c.title} className="panel p-5 transition-colors hover:border-primary/40">
              <span className="grid size-9 place-items-center rounded-sm border border-primary/30 bg-primary/10 text-primary">
                <c.icon className="size-4" aria-hidden />
              </span>
              <h3 className="mt-4 text-sm font-semibold text-foreground">{c.title}</h3>
              <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">{c.body}</p>
            </article>
          ))}
        </div>
      </section>

      {/* Flow */}
      <section className="border-t border-border bg-panel/40">
        <div className="mx-auto max-w-7xl px-5 py-16">
          <p className="label-xs">How it works</p>
          <ol className="mt-6 grid gap-3 md:grid-cols-4">
            {[
              ["01", "Ingest", "Import CDR/IPDR, statements and social exports under lawful authorization."],
              ["02", "Resolve", "Entity resolution links numbers, accounts, devices and handles to identities."],
              ["03", "Detect", "Behavioural models and graph analytics surface anomalies and hidden bridges."],
              ["04", "Act", "Explainable leads, reconstructed timelines and audit-ready case reports."],
            ].map(([n, title, body]) => (
              <li key={n} className="panel p-5">
                <span className="font-mono text-xs text-primary">{n}</span>
                <h3 className="mt-2 text-sm font-semibold text-foreground">{title}</h3>
                <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">{body}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-20 text-center">
        <h2 className="text-2xl font-semibold tracking-tight text-foreground lg:text-4xl">
          Open the command center
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-sm text-muted-foreground">
          Sign in with your authorized credentials, or register to explore the workspace on synthetic
          demonstration data.
        </p>
        <div className="mt-7 flex flex-wrap justify-center gap-3">
          <Button asChild size="lg">
            <Link to="/auth">
              Sign in
              <Lock className="size-4" />
            </Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link to="/auth">Sign up</Link>
          </Button>
        </div>
      </section>

      <footer className="border-t border-border px-5 py-6">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-3 text-[11px] text-muted-foreground">
          <ShieldAlert className="size-3.5 text-sev-medium" aria-hidden />
          Analytical support system operating on authorized and synthetic demonstration datasets.
          Outputs are investigative leads requiring review — they do not establish guilt.
          <span className="ml-auto font-mono">SENTINEL · 2026</span>
        </div>
      </footer>
    </div>
  );
}
