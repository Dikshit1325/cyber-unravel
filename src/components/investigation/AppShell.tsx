import { Link, useRouterState } from "@tanstack/react-router";
import { useState, type ReactNode } from "react";
import {
  Activity,
  Bell,
  Database,
  FileText,
  Gauge,
  GitBranch,
  History,
  LayoutGrid,
  LogOut,
  Menu,
  MessageSquare,
  Network,
  Settings,
  ShieldAlert,
  Users,
  Wallet,
  Clock,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { alerts, investigator, platform, primaryCase } from "@/lib/mock-data";
import { GlobalSearch } from "./GlobalSearch";
import { SeverityBadge } from "./primitives";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { toast } from "sonner";

const nav = [
  { to: "/", label: "Command Center", icon: Gauge },
  { to: "/cases", label: "Cases", icon: LayoutGrid },
  { to: "/graph", label: "Investigation Graph", icon: Network },
  { to: "/timeline", label: "Timeline", icon: Clock },
  { to: "/entities", label: "Entities", icon: Users },
  { to: "/transactions", label: "Transactions", icon: Wallet },
  { to: "/communications", label: "Communications", icon: MessageSquare },
  { to: "/anomalies", label: "Anomalies & Alerts", icon: ShieldAlert },
  { to: "/cross-domain", label: "Cross-Domain Intelligence", icon: GitBranch },
  { to: "/clusters", label: "Clusters & Hidden Links", icon: Activity },
  { to: "/data-sources", label: "Data Sources", icon: Database },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/audit", label: "Audit Trail", icon: History },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const [open, setOpen] = useState(false);
  const [role, setRole] = useState<string>(investigator.roles[0]);

  return (
    <div className="flex min-h-screen bg-background">
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-sidebar-border bg-sidebar transition-transform lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex items-center gap-2.5 border-b border-sidebar-border px-4 py-4">
          <div className="grid size-8 place-items-center rounded-sm border border-primary/40 bg-primary/12 text-primary">
            <ShieldAlert className="size-4" aria-hidden />
          </div>
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold tracking-wide text-sidebar-foreground">
              {platform.name}
            </div>
            <div className="truncate text-[10px] tracking-widest text-muted-foreground uppercase">
              Investigation Intelligence
            </div>
          </div>
        </div>

        <nav className="flex-1 space-y-0.5 overflow-y-auto px-2 py-3">
          {nav.map((item) => {
            const active = item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={() => setOpen(false)}
                className={cn(
                  "flex items-center gap-2.5 rounded-sm px-2.5 py-2 text-[13px] transition-colors",
                  active
                    ? "border-l-2 border-primary bg-sidebar-accent pl-2 font-medium text-sidebar-accent-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground",
                )}
              >
                <item.icon className={cn("size-4 shrink-0", active && "text-primary")} aria-hidden />
                <span className="truncate">{item.label}</span>
                {item.to === "/anomalies" && (
                  <span className="ml-auto rounded-sm border border-sev-high/40 bg-sev-high/12 px-1 font-mono text-[10px] text-sev-high">
                    {alerts.length}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-sidebar-border px-3 py-3">
          <div className="text-[13px] font-medium text-sidebar-foreground">{investigator.name}</div>
          <div className="mt-0.5 font-mono text-[11px] text-muted-foreground">
            {role} · {investigator.badge}
          </div>
          <div className="mt-2 flex items-center justify-between gap-2">
            <span className="truncate font-mono text-[10px] text-muted-foreground">
              {primaryCase.id}
            </span>
            <SeverityBadge severity="HIGH" label="ACTIVE" />
          </div>
          <div className="mt-2 flex gap-1.5">
            <select
              value={role}
              onChange={(e) => {
                setRole(e.target.value);
                toast.success(`Role switched to ${e.target.value}`, {
                  description: "Prototype role simulation — permissions shown in Settings.",
                });
              }}
              aria-label="Switch role"
              className="h-7 flex-1 rounded-sm border border-input bg-background px-1.5 text-[11px] text-foreground"
            >
              {investigator.roles.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={() => toast("Session ended (prototype)")}
              aria-label="Logout"
              className="grid size-7 place-items-center rounded-sm border border-input text-muted-foreground hover:text-foreground"
            >
              <LogOut className="size-3.5" aria-hidden />
            </button>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col lg:pl-64">
        <header className="sticky top-0 z-30 flex items-center gap-3 border-b border-border bg-background/95 px-4 py-2.5 backdrop-blur">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle navigation"
          >
            <Menu className="size-4" />
          </Button>
          <GlobalSearch />
          <div className="ml-auto flex items-center gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="Notifications" className="relative">
                  <Bell className="size-4" />
                  <span className="absolute top-1.5 right-1.5 size-1.5 rounded-full bg-sev-high" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80">
                <DropdownMenuLabel>Active alerts</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {alerts.map((a) => (
                  <DropdownMenuItem key={a.id} asChild>
                    <Link to="/anomalies" className="flex flex-col items-start gap-1">
                      <span className="flex items-center gap-2 text-xs font-medium">
                        <SeverityBadge severity={a.severity} />
                        {a.title}
                      </span>
                      <span className="text-[11px] text-muted-foreground">{a.entity}</span>
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            <div className="hidden items-center gap-2 rounded-md border border-border px-2 py-1 sm:flex">
              <div className="grid size-6 place-items-center rounded-sm bg-primary/15 font-mono text-[10px] text-primary">
                AR
              </div>
              <div className="leading-tight">
                <div className="text-[11px] font-medium">{investigator.name}</div>
                <div className="font-mono text-[10px] text-muted-foreground">{role}</div>
              </div>
            </div>
          </div>
        </header>

        <main className="min-w-0 flex-1 px-4 py-5 lg:px-6">{children}</main>
      </div>

      {open && (
        <button
          type="button"
          aria-label="Close navigation"
          className="fixed inset-0 z-30 bg-background/70 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}
    </div>
  );
}
