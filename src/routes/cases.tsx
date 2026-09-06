import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { FilePlus2 } from "lucide-react";
import { PageHeader, Panel, SeverityBadge } from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
const seedCases: any[] = [];
const investigator = { name: "Investigator" };
import type { Case } from "@/lib/types";
import { toast } from "sonner";

export const Route = createFileRoute("/cases")({
  head: () => ({
    meta: [
      { title: "Cases — SENTINEL Investigation Intelligence" },
      {
        name: "description",
        content: "Manage digital investigation cases, priorities, assigned investigators and open alerts.",
      },
      { property: "og:title", content: "Investigation Cases" },
      { property: "og:description", content: "Case workspace for cross-domain digital investigations." },
    ],
  }),
  component: CasesPage,
});

const caseTypes = [
  "Financial Fraud",
  "Cybercrime",
  "Organized Digital Fraud",
  "Suspicious Financial Network",
  "Other",
];

function CasesPage() {
  const [caseList, setCaseList] = useState<Case[]>(seedCases);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    id: `CASE-2026-${Math.floor(1030 + Math.random() * 60)}`,
    name: "",
    type: caseTypes[0]!,
    description: "",
    priority: "HIGH",
    investigator: investigator.name,
    incidentDate: "2026-08-16",
    status: "Active",
  });
  const [error, setError] = useState<string | null>(null);

  const submit = () => {
    if (!form.name.trim()) {
      setError("Case name is required before the case can be created.");
      return;
    }
    setError(null);
    setCaseList((prev) => [
      {
        id: form.id,
        name: form.name,
        type: form.type,
        status: form.status as Case["status"],
        priority: form.priority as Case["priority"],
        entities: 0,
        alerts: 0,
        lastActivity: "just now",
        investigator: form.investigator,
        incidentDate: form.incidentDate,
        description: form.description || "No description provided.",
      },
      ...prev,
    ]);
    setOpen(false);
    toast.success(`${form.id} created`, { description: "Import datasets to begin analysis." });
  };

  return (
    <div className="space-y-5">
      <PageHeader
        title="Cases"
        subtitle="Every case is an isolated investigation workspace with its own datasets, entities and findings."
        action={
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button>
                <FilePlus2 className="size-4" />
                New Case
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>Create new case</DialogTitle>
                <DialogDescription>
                  Case metadata is recorded in the audit trail on creation.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <Label htmlFor="cid">Case ID</Label>
                  <Input
                    id="cid"
                    value={form.id}
                    onChange={(e) => setForm({ ...form, id: e.target.value })}
                    className="font-mono"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="cdate">Incident date</Label>
                  <Input
                    id="cdate"
                    type="date"
                    value={form.incidentDate}
                    onChange={(e) => setForm({ ...form, incidentDate: e.target.value })}
                  />
                </div>
                <div className="space-y-1.5 sm:col-span-2">
                  <Label htmlFor="cname">Case name</Label>
                  <Input
                    id="cname"
                    placeholder="e.g. Online Financial Fraud Investigation"
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="ctype">Case type</Label>
                  <select
                    id="ctype"
                    value={form.type}
                    onChange={(e) => setForm({ ...form, type: e.target.value })}
                    className="h-9 w-full rounded-md border border-input bg-background px-2 text-sm"
                  >
                    {caseTypes.map((t) => (
                      <option key={t}>{t}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="cprio">Priority</Label>
                  <select
                    id="cprio"
                    value={form.priority}
                    onChange={(e) => setForm({ ...form, priority: e.target.value })}
                    className="h-9 w-full rounded-md border border-input bg-background px-2 text-sm"
                  >
                    {["HIGH", "MEDIUM", "LOW"].map((t) => (
                      <option key={t}>{t}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="cinv">Investigator</Label>
                  <Input
                    id="cinv"
                    value={form.investigator}
                    onChange={(e) => setForm({ ...form, investigator: e.target.value })}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="cstatus">Status</Label>
                  <select
                    id="cstatus"
                    value={form.status}
                    onChange={(e) => setForm({ ...form, status: e.target.value })}
                    className="h-9 w-full rounded-md border border-input bg-background px-2 text-sm"
                  >
                    {["Active", "Under Review", "Closed"].map((t) => (
                      <option key={t}>{t}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5 sm:col-span-2">
                  <Label htmlFor="cdesc">Description</Label>
                  <Textarea
                    id="cdesc"
                    rows={3}
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                    placeholder="Summarize the complaint and the authorized datasets requested."
                  />
                </div>
              </div>
              {error && (
                <p className="rounded-sm border border-sev-high/40 bg-sev-high/10 px-3 py-2 text-xs text-sev-high">
                  {error}
                </p>
              )}
              <DialogFooter>
                <Button variant="ghost" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={submit}>Create case</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      <div className="grid gap-3 lg:grid-cols-2">
        {caseList.map((c) => (
          <Panel key={c.id} className="transition-colors hover:border-primary/40">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-primary">{c.id}</span>
                  <SeverityBadge severity={c.priority} />
                  <span className="rounded-sm border border-border px-1.5 py-0.5 text-[10px] tracking-wider text-muted-foreground uppercase">
                    {c.status}
                  </span>
                </div>
                <h3 className="mt-1.5 text-sm font-semibold text-foreground">{c.name}</h3>
                <p className="mt-1 text-xs text-muted-foreground">{c.description}</p>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 border-t border-border pt-3 font-mono text-xs sm:grid-cols-4">
              <div>
                <div className="label-xs">Entities</div>
                {c.entities.toLocaleString("en-IN")}
              </div>
              <div>
                <div className="label-xs">Alerts</div>
                <span className="text-sev-high">{c.alerts}</span>
              </div>
              <div>
                <div className="label-xs">Incident</div>
                {c.incidentDate}
              </div>
              <div>
                <div className="label-xs">Last activity</div>
                {c.lastActivity}
              </div>
            </div>
            <div className="mt-3 flex items-center justify-between">
              <span className="text-[11px] text-muted-foreground">{c.investigator}</span>
              <Button asChild size="sm" variant="outline">
                <Link to="/graph">Open Investigation</Link>
              </Button>
            </div>
          </Panel>
        ))}
      </div>
    </div>
  );
}
