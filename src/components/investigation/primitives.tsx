import { cn } from "@/lib/utils";
import type { Domain, EntityType, Severity } from "@/lib/types";
import {
  AlertTriangle,
  Banknote,
  Cpu,
  Globe,
  MapPin,
  Phone,
  Receipt,
  Share2,
  TrendingDown,
  TrendingUp,
  User,
  type LucideIcon,
} from "lucide-react";
import type { ReactNode } from "react";

export const severityStyles: Record<Severity | "NORMAL", string> = {
  HIGH: "border-sev-high/40 bg-sev-high/12 text-sev-high",
  MEDIUM: "border-sev-medium/40 bg-sev-medium/12 text-sev-medium",
  LOW: "border-sev-low/35 bg-sev-low/10 text-sev-low",
  NORMAL: "border-border bg-secondary text-muted-foreground",
};

const severityGlyph: Record<Severity | "NORMAL", string> = {
  HIGH: "▲",
  MEDIUM: "◆",
  LOW: "▾",
  NORMAL: "•",
};

export function SeverityBadge({
  severity,
  label,
  className,
}: {
  severity: Severity | "NORMAL";
  label?: string;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-sm border px-1.5 py-0.5 font-mono text-[10px] font-semibold tracking-widest uppercase",
        severityStyles[severity],
        className,
      )}
      aria-label={`Severity ${severity}`}
    >
      <span aria-hidden>{severityGlyph[severity]}</span>
      {label ?? severity}
    </span>
  );
}

export const domainColor: Record<Domain, string> = {
  Telecom: "text-telecom",
  Financial: "text-financial",
  Social: "text-social",
  Network: "text-network",
  "Cross-Domain": "text-primary",
};

export const domainBorder: Record<Domain, string> = {
  Telecom: "border-telecom/40 bg-telecom/10 text-telecom",
  Financial: "border-financial/40 bg-financial/10 text-financial",
  Social: "border-social/40 bg-social/10 text-social",
  Network: "border-network/40 bg-network/10 text-network",
  "Cross-Domain": "border-primary/40 bg-primary/10 text-primary",
};

export function DomainTag({ domain }: { domain: Domain }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-sm border px-1.5 py-0.5 font-mono text-[10px] font-semibold tracking-widest uppercase",
        domainBorder[domain],
      )}
    >
      {domain}
    </span>
  );
}

export const entityIcon: Record<EntityType, LucideIcon> = {
  Person: User,
  Phone: Phone,
  "Bank Account": Banknote,
  "Social Account": Share2,
  "IP Address": Globe,
  Device: Cpu,
  Transaction: Receipt,
  Location: MapPin,
};

export function Panel({
  title,
  subtitle,
  action,
  children,
  className,
  bodyClassName,
}: {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
}) {
  return (
    <section className={cn("panel flex flex-col overflow-hidden", className)}>
      {(title || action) && (
        <header className="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
          <div className="min-w-0">
            {title && <h2 className="truncate text-sm font-semibold text-foreground">{title}</h2>}
            {subtitle && <p className="truncate text-xs text-muted-foreground">{subtitle}</p>}
          </div>
          {action}
        </header>
      )}
      <div className={cn("flex-1", bodyClassName ?? "p-4")}>{children}</div>
    </section>
  );
}

export function PageHeader({
  title,
  subtitle,
  action,
}: {
  title: string;
  subtitle: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4 border-b border-border pb-5">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-foreground">{title}</h1>
        <p className="mt-1 max-w-3xl text-sm text-muted-foreground">{subtitle}</p>
      </div>
      {action}
    </div>
  );
}

export function KpiCard({
  label,
  value,
  trend,
  direction,
  hint,
}: {
  label: string;
  value: string;
  trend: string;
  direction: "up" | "down";
  hint: string;
}) {
  const Icon = direction === "up" ? TrendingUp : TrendingDown;
  return (
    <div className="panel group relative overflow-hidden p-4 transition-colors hover:border-primary/40">
      <div className="label-xs">{label}</div>
      <div className="mt-2 font-mono text-2xl font-semibold tracking-tight text-foreground">{value}</div>
      <div className="mt-2 flex items-center gap-2 text-xs">
        <span className="inline-flex items-center gap-1 font-mono text-primary">
          <Icon className="size-3.5" aria-hidden />
          {trend}
        </span>
        <span className="text-muted-foreground">{hint}</span>
      </div>
      <div className="absolute inset-x-0 bottom-0 h-px bg-linear-to-r from-transparent via-primary/50 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
    </div>
  );
}

export function StatRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-border/60 py-2 text-sm last:border-0">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-mono text-foreground">{value}</span>
    </div>
  );
}

export function PriorityScore({
  score,
  breakdown,
  compact,
}: {
  score: number;
  breakdown: { label: string; points: number }[];
  compact?: boolean;
}) {
  const severity: Severity = score >= 70 ? "HIGH" : score >= 45 ? "MEDIUM" : "LOW";
  return (
    <div className="space-y-3">
      <div className="flex items-end gap-3">
        <div className="font-mono text-3xl font-semibold text-foreground">
          {score}
          <span className="text-base text-muted-foreground">/100</span>
        </div>
        <SeverityBadge severity={severity} label={`${severity} PRIORITY`} className="mb-1.5" />
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-secondary">
        <div
          className={cn(
            "h-full rounded-full",
            severity === "HIGH" ? "bg-sev-high" : severity === "MEDIUM" ? "bg-sev-medium" : "bg-sev-low",
          )}
          style={{ width: `${score}%` }}
        />
      </div>
      {!compact && (
        <ul className="space-y-1.5">
          {breakdown.map((f) => (
            <li key={f.label} className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">{f.label}</span>
              <span className="font-mono text-primary">+{f.points}</span>
            </li>
          ))}
        </ul>
      )}
      <p className="flex gap-2 rounded-sm border border-border bg-secondary/50 p-2 text-[11px] leading-relaxed text-muted-foreground">
        <AlertTriangle className="mt-0.5 size-3.5 shrink-0 text-sev-medium" aria-hidden />
        Priority score is an analytical aid for investigation and does not establish guilt.
      </p>
    </div>
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-md border border-dashed border-border px-6 py-14 text-center">
      <div className="grid size-10 place-items-center rounded-md border border-border bg-secondary text-muted-foreground">
        <Share2 className="size-5" aria-hidden />
      </div>
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      <p className="max-w-sm text-xs text-muted-foreground">{description}</p>
      {action}
    </div>
  );
}

export function LoadingState({ label = "Analyzing data" }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 rounded-md border border-border bg-secondary/40 px-4 py-3 text-sm text-muted-foreground">
      <span className="size-3 animate-ping rounded-full bg-primary" aria-hidden />
      {label}…
    </div>
  );
}
