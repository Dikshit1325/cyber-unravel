import { createFileRoute, Link } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { PageHeader, Panel, SeverityBadge, StatRow } from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { inr, moneyFlowChain, transactions, transactionVolumeSeries } from "@/lib/mock-data";

export const Route = createFileRoute("/transactions")({
  head: () => ({
    meta: [
      { title: "Transaction Intelligence — SENTINEL" },
      {
        name: "description",
        content:
          "Financial analytics over imported bank statements: volume trends, money-flow chains and transactions requiring review.",
      },
      { property: "og:title", content: "Transaction Intelligence" },
      {
        property: "og:description",
        content: "Money-flow tracing and financial anomaly review across authorized bank data.",
      },
    ],
  }),
  component: TransactionsPage,
});

function TransactionsPage() {
  const [min, setMin] = useState(0);
  const [priority, setPriority] = useState("All");
  const [type, setType] = useState("All");
  const [account, setAccount] = useState("");

  const rows = useMemo(
    () =>
      transactions
        .filter((t) => t.amount >= min)
        .filter((t) => (priority === "All" ? true : t.priority === priority))
        .filter((t) => (type === "All" ? true : t.type === type))
        .filter((t) =>
          account.trim()
            ? `${t.sender} ${t.receiver}`.toLowerCase().includes(account.trim().toLowerCase())
            : true,
        ),
    [min, priority, type, account],
  );

  const incoming = transactions.reduce((s, t) => s + t.amount, 0);
  const flagged = transactions.filter((t) => t.priority === "HIGH").length;
  const accounts = new Set(transactions.flatMap((t) => [t.sender, t.receiver])).size;

  return (
    <div className="space-y-5">
      <PageHeader
        title="Transaction Intelligence"
        subtitle="Financial movement reconstructed from authorized bank statement imports, scored against each account's observed baseline."
      />

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <Panel bodyClassName="p-4">
          <div className="label-xs">Total volume</div>
          <div className="mt-1 font-mono text-xl text-foreground">{inr(incoming)}</div>
        </Panel>
        <Panel bodyClassName="p-4">
          <div className="label-xs">Accounts involved</div>
          <div className="mt-1 font-mono text-xl text-foreground">{accounts}</div>
        </Panel>
        <Panel bodyClassName="p-4">
          <div className="label-xs">Requires review</div>
          <div className="mt-1 font-mono text-xl text-sev-high">{flagged}</div>
        </Panel>
        <Panel bodyClassName="p-4">
          <div className="label-xs">Average amount</div>
          <div className="mt-1 font-mono text-xl text-foreground">
            {inr(Math.round(incoming / transactions.length))}
          </div>
        </Panel>
        <Panel bodyClassName="p-4">
          <div className="label-xs">Incident-window volume</div>
          <div className="mt-1 font-mono text-xl text-financial">{inr(480000)}</div>
        </Panel>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_320px]">
        <Panel title="Transaction volume over time" subtitle="Total vs. flagged value" bodyClassName="p-3">
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={transactionVolumeSeries}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="time" stroke="var(--muted-foreground)" fontSize={11} />
                <YAxis
                  stroke="var(--muted-foreground)"
                  fontSize={11}
                  tickFormatter={(v: number) => `${v / 1000}k`}
                />
                <Tooltip
                  contentStyle={{
                    background: "var(--popover)",
                    border: "1px solid var(--border)",
                    fontSize: 12,
                  }}
                  formatter={(v) => inr(Number(v))}
                />
                <Line type="monotone" dataKey="volume" stroke="var(--chart-1)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="flagged" stroke="var(--chart-5)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Money flow chain" subtitle="Layered onward transfers" bodyClassName="p-4">
          <ol className="space-y-1.5">
            {moneyFlowChain.map((f, i) => (
              <li key={`${f.from}-${f.to}`} className="rounded-sm border border-border bg-secondary/30 p-2.5">
                <div className="flex items-center justify-between font-mono text-[11px]">
                  <span className="text-foreground">{f.from}</span>
                  <span className="text-financial">{inr(f.amount)}</span>
                </div>
                <div className="mt-0.5 font-mono text-[11px] text-muted-foreground">↓ {f.to}</div>
                <div className="mt-1 text-[10px] text-muted-foreground">Leg {i + 1} of the observed chain</div>
              </li>
            ))}
          </ol>
        </Panel>
      </div>

      <Panel
        title="Transaction records"
        subtitle={`${rows.length} of ${transactions.length} records`}
        bodyClassName="p-0"
      >
        <div className="grid gap-3 border-b border-border p-3 md:grid-cols-4">
          <div className="space-y-1">
            <Label htmlFor="min">Minimum amount</Label>
            <Input
              id="min"
              type="number"
              value={min}
              onChange={(e) => setMin(Number(e.target.value))}
              className="h-8 font-mono text-xs"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="acc">Account</Label>
            <Input
              id="acc"
              value={account}
              onChange={(e) => setAccount(e.target.value)}
              placeholder="AC-48291"
              className="h-8 font-mono text-xs"
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="prio">Priority</Label>
            <select
              id="prio"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="h-8 w-full rounded-md border border-input bg-background px-2 text-xs"
            >
              {["All", "HIGH", "MEDIUM", "NORMAL"].map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <Label htmlFor="ttype">Type</Label>
            <select
              id="ttype"
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="h-8 w-full rounded-md border border-input bg-background px-2 text-xs"
            >
              {["All", "IMPS", "NEFT", "UPI", "RTGS", "Cash Deposit"].map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
          </div>
        </div>

        {rows.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <p className="text-sm font-medium text-foreground">No transactions match these filters</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Lower the minimum amount or clear the account filter.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px] text-xs">
              <thead className="border-b border-border text-left text-muted-foreground">
                <tr>
                  {["Timestamp", "Sender", "Receiver", "Amount", "Type", "Priority", "Case", "Status", ""].map(
                    (h) => (
                      <th key={h} className="px-3 py-2 font-medium">
                        {h}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-border font-mono">
                {rows.map((t) => (
                  <tr key={t.id} className="hover:bg-secondary/40">
                    <td className="px-3 py-2">{t.timestamp}</td>
                    <td className="px-3 py-2">
                      <Link
                        to="/entities/$entityId"
                        params={{ entityId: t.sender }}
                        className="text-primary hover:underline"
                      >
                        {t.sender}
                      </Link>
                    </td>
                    <td className="px-3 py-2">
                      <Link
                        to="/entities/$entityId"
                        params={{ entityId: t.receiver }}
                        className="text-primary hover:underline"
                      >
                        {t.receiver}
                      </Link>
                    </td>
                    <td className="px-3 py-2 text-financial">{inr(t.amount)}</td>
                    <td className="px-3 py-2">{t.type}</td>
                    <td className="px-3 py-2">
                      <SeverityBadge severity={t.priority} />
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">{t.caseId}</td>
                    <td className="px-3 py-2 text-muted-foreground">{t.status}</td>
                    <td className="px-3 py-2">
                      <Button asChild size="sm" variant="ghost" className="h-7 text-[11px]">
                        <Link to="/graph">Trace</Link>
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      <Panel title="Financial reading" bodyClassName="grid gap-4 p-4 md:grid-cols-2">
        <div>
          <StatRow label="Longest observed chain" value="4 legs (AC-99102 → AC-8821)" />
          <StatRow label="Fastest onward transfer" value="4 minutes" />
          <StatRow label="Highest pass-through ratio" value="92% (AC-8821)" />
        </div>
        <p className="text-xs leading-relaxed text-muted-foreground">
          Value entering AC-48291 during the incident window is redistributed to three counterparties within
          nine minutes. Pass-through behaviour of this kind is an analytical indicator for review and should be
          corroborated with statement documentation.
        </p>
      </Panel>
    </div>
  );
}
