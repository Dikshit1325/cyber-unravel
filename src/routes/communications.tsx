import { createFileRoute, Link } from "@tanstack/react-router";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { PageHeader, Panel, SeverityBadge } from "@/components/investigation/primitives";
import { communicationVolumeSeries, communications, topContacts } from "@/lib/mock-data";

export const Route = createFileRoute("/communications")({
  head: () => ({
    meta: [
      { title: "Communication Intelligence — SENTINEL" },
      {
        name: "description",
        content:
          "Call and session analytics from authorized CDR/IPDR data: volume spikes, top contacts and new relationship formation.",
      },
      { property: "og:title", content: "Communication Intelligence" },
      { property: "og:description", content: "Telecom pattern analytics for investigation support." },
    ],
  }),
  component: CommunicationsPage,
});

function CommunicationsPage() {
  const spikes = communications.filter((c) => c.newRelationship).length;
  return (
    <div className="space-y-5">
      <PageHeader
        title="Communication Intelligence"
        subtitle="Call, SMS and session records from authorized telecom datasets, analyzed for spikes and new relationship formation."
      />

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-6">
        {[
          { label: "Total calls", value: String(communications.length) },
          { label: "Unique contacts", value: String(topContacts.length) },
          { label: "Communication spikes", value: "2" },
          { label: "Average duration", value: "3m 12s" },
          { label: "New relationships", value: String(spikes) },
          { label: "High-priority links", value: "2" },
        ].map((k) => (
          <Panel key={k.label} bodyClassName="p-4">
            <div className="label-xs">{k.label}</div>
            <div className="mt-1 font-mono text-xl text-foreground">{k.value}</div>
          </Panel>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Panel title="Communication volume" subtitle="Calls vs. new relationships" bodyClassName="p-3">
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={communicationVolumeSeries}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="time" stroke="var(--muted-foreground)" fontSize={11} />
                <YAxis stroke="var(--muted-foreground)" fontSize={11} />
                <Tooltip
                  contentStyle={{ background: "var(--popover)", border: "1px solid var(--border)", fontSize: 12 }}
                />
                <Line type="monotone" dataKey="calls" stroke="var(--chart-1)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="newLinks" stroke="var(--chart-3)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Top connected numbers" bodyClassName="p-3">
          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topContacts}>
                <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="number" stroke="var(--muted-foreground)" fontSize={9} />
                <YAxis stroke="var(--muted-foreground)" fontSize={11} />
                <Tooltip
                  contentStyle={{ background: "var(--popover)", border: "1px solid var(--border)", fontSize: 12 }}
                />
                <Bar dataKey="calls" fill="var(--chart-1)" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <Panel title="Communication records" bodyClassName="p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-xs">
            <thead className="border-b border-border text-left text-muted-foreground">
              <tr>
                {["Timestamp", "From", "To", "Duration", "Type", "New link", "Priority"].map((h) => (
                  <th key={h} className="px-3 py-2 font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border font-mono">
              {communications.map((c) => (
                <tr key={c.id} className="hover:bg-secondary/40">
                  <td className="px-3 py-2">{c.timestamp}</td>
                  <td className="px-3 py-2">
                    <Link to="/entities/$entityId" params={{ entityId: c.from }} className="text-primary hover:underline">
                      {c.from}
                    </Link>
                  </td>
                  <td className="px-3 py-2">
                    <Link to="/entities/$entityId" params={{ entityId: c.to }} className="text-primary hover:underline">
                      {c.to}
                    </Link>
                  </td>
                  <td className="px-3 py-2">{c.duration}</td>
                  <td className="px-3 py-2">{c.kind}</td>
                  <td className="px-3 py-2 text-muted-foreground">{c.newRelationship ? "Yes" : "—"}</td>
                  <td className="px-3 py-2">
                    <SeverityBadge severity={c.priority} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
