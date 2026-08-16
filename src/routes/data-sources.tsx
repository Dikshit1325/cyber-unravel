import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Database, Upload } from "lucide-react";
import { PageHeader, Panel, SeverityBadge, StatRow } from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { datasets } from "@/lib/mock-data";
import { toast } from "sonner";

export const Route = createFileRoute("/data-sources")({
  head: () => ({
    meta: [
      { title: "Data Sources — SENTINEL" },
      {
        name: "description",
        content: "Manage authorized CDR, IPDR, bank statement and public social datasets imported into the case.",
      },
      { property: "og:title", content: "Investigation Data Sources" },
      { property: "og:description", content: "Import, validate and track authorized investigation datasets." },
    ],
  }),
  component: DataSourcesPage,
});

const steps = ["Upload Dataset", "Detect Dataset Type", "Map Fields", "Validate", "Import"];

function DataSourcesPage() {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);
  const [progress, setProgress] = useState(0);

  const next = () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
      return;
    }
    setProgress(0);
    const timer = setInterval(() => {
      setProgress((p) => {
        if (p >= 100) {
          clearInterval(timer);
          setOpen(false);
          setStep(0);
          toast.success("Dataset successfully imported", {
            description: "12,401 valid records added · 81 warnings logged",
          });
          return 100;
        }
        return p + 20;
      });
    }, 250);
  };

  return (
    <div className="space-y-5">
      <PageHeader
        title="Data Sources"
        subtitle="Only authorized, imported or synthetic demonstration datasets are analyzed. No live access to external platforms is used."
        action={
          <Button onClick={() => setOpen(true)}>
            <Upload className="size-4" />
            Import Dataset
          </Button>
        }
      />

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {datasets.map((d) => (
          <Panel key={d.id} bodyClassName="p-4">
            <div className="flex items-start justify-between">
              <span className="grid size-8 place-items-center rounded-sm border border-border bg-secondary text-primary">
                <Database className="size-4" aria-hidden />
              </span>
              <SeverityBadge
                severity={d.status === "Imported" ? "LOW" : "MEDIUM"}
                label={d.status}
              />
            </div>
            <h3 className="mt-3 text-sm font-semibold text-foreground">{d.kind}</h3>
            <p className="text-xs text-muted-foreground">{d.name}</p>
            <div className="mt-3">
              <StatRow label="Records" value={d.records.toLocaleString("en-IN")} />
              <StatRow label="Last updated" value={d.lastUpdated} />
            </div>
            <p className="mt-2 text-[11px] text-muted-foreground">{d.source}</p>
          </Panel>
        ))}
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              Step {step + 1} of {steps.length}: {steps[step]}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex gap-1">
              {steps.map((s, i) => (
                <div
                  key={s}
                  className={`h-1 flex-1 rounded-full ${i <= step ? "bg-primary" : "bg-secondary"}`}
                />
              ))}
            </div>

            {step === 0 && (
              <label className="flex cursor-pointer flex-col items-center gap-2 rounded-md border border-dashed border-border p-8 text-center">
                <Upload className="size-5 text-primary" aria-hidden />
                <span className="text-sm text-foreground">Drop a CSV/XLSX export or browse</span>
                <span className="text-[11px] text-muted-foreground">
                  Supported: CDR, IPDR, bank statement, public social activity exports
                </span>
                <input type="file" className="hidden" aria-label="Upload dataset" />
              </label>
            )}
            {step === 1 && (
              <div className="rounded-sm border border-primary/40 bg-primary/8 p-3 text-sm text-foreground">
                Detected: <span className="font-mono">CDR Dataset</span>
                <p className="mt-1 text-[11px] text-muted-foreground">
                  Detection based on column signature and value patterns.
                </p>
              </div>
            )}
            {step === 2 && (
              <div className="space-y-1.5 font-mono text-xs">
                {[
                  ["Caller", "phone_a"],
                  ["Receiver", "phone_b"],
                  ["Timestamp", "timestamp"],
                  ["Duration", "duration"],
                ].map(([a, b]) => (
                  <div
                    key={a}
                    className="flex items-center justify-between rounded-sm border border-border bg-secondary/40 px-3 py-2"
                  >
                    <span className="text-muted-foreground">{a}</span>
                    <span className="text-primary">→ {b}</span>
                  </div>
                ))}
              </div>
            )}
            {step === 3 && (
              <div>
                <StatRow label="Records" value="12,482" />
                <StatRow label="Valid" value="12,401" />
                <StatRow label="Warnings" value="81" />
                <p className="mt-2 rounded-sm border border-sev-medium/40 bg-sev-medium/10 p-2 text-[11px] text-sev-medium">
                  81 rows have missing duration values and will be imported without call-length analytics.
                </p>
              </div>
            )}
            {step === 4 && (
              <div className="space-y-2">
                <Progress value={progress} />
                <p className="text-xs text-muted-foreground">
                  {progress > 0 ? `Importing… ${progress}%` : "Ready to import 12,401 validated records."}
                </p>
              </div>
            )}

            <div className="flex justify-between">
              <Button
                variant="ghost"
                onClick={() => (step === 0 ? setOpen(false) : setStep(step - 1))}
              >
                {step === 0 ? "Cancel" : "Back"}
              </Button>
              <Button onClick={next}>{step === steps.length - 1 ? "Start import" : "Continue"}</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
