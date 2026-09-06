// Audit Trail Page
import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState, useMemo } from "react";
import {
  PageHeader,
  Panel,
  KpiCard,
} from "@/components/investigation/primitives";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { getAudit, type AuditRecord, type AuditResponse } from "@/lib/api";

export const Route = createFileRoute("/audit")({
  head: () => ({
    meta: [
      { title: "Audit Trail — SENTINEL" },
      {
        name: "description",
        content: "A complete trail of investigator activity, showing actions, resources and outcomes.",
      },
      { property: "og:title", content: "Audit Trail" },
      { property: "og:description", content: "Investigator audit log for security compliance." },
    ],
  }),
  component: AuditPage,
});

function AuditPage() {
  // filter state
  const [userId, setUserId] = useState<string>("");
  const [action, setAction] = useState<string>("");
  const [resourceType, setResourceType] = useState<string>("");
  const [status, setStatus] = useState<string>("");
  const [startTime, setStartTime] = useState<string>("");
  const [endTime, setEndTime] = useState<string>("");

  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // fetch audit logs whenever filters change
  useEffect(() => {
    const fetchAudit = async () => {
      setLoading(true);
      setError(null);
      try {
        const params: any = {};
        if (userId) params.user_id = userId;
        if (action) params.action = action;
        if (resourceType) params.resource_type = resourceType;
        if (status) params.status = status;
        if (startTime) params.start_time = startTime;
        if (endTime) params.end_time = endTime;
        const data: AuditResponse = await getAudit(params);
        setRecords(data.audit_records);
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Failed to load audit logs";
        setError(msg);
        console.error("Audit fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAudit();
  }, [userId, action, resourceType, status, startTime, endTime]);

  // summary calculations
  const totalEvents = records.length;
  const successful = useMemo(() => records.filter(r => r.status === "SUCCESS").length, [records]);
  const denied = useMemo(() => records.filter(r => r.status === "DENIED").length, [records]);
  const uniqueUsers = useMemo(() => {
    const setU = new Set<string>();
    records.forEach(r => setU.add(r.user_id));
    return setU.size;
  }, [records]);

  // status badge helper
  const renderStatusBadge = (s: string) => {
    const variant = s === "SUCCESS" ? "default" : s === "DENIED" ? "destructive" : "outline";
    return <Badge variant={variant as any}>{s}</Badge>;
  };

  return (
    <div className="space-y-5">
      <PageHeader
        title="Audit Trail"
        subtitle="A complete trail of investigator activity."
      />

      {/* Summary cards */}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Total Events" value={totalEvents.toLocaleString()} />
        <KpiCard label="Successful Actions" value={successful.toLocaleString()} />
        <KpiCard label="Denied Actions" value={denied.toLocaleString()} />
        <KpiCard label="Unique Users" value={uniqueUsers.toLocaleString()} />
      </div>

      {/* Filters */}
      <Panel title="Filters" bodyClassName="grid gap-3 md:grid-cols-2 lg:grid-cols-3 p-4">
        <div className="space-y-1.5">
          <label htmlFor="filter-user" className="text-sm font-medium">User ID</label>
          <Input id="filter-user" placeholder="admin_01" value={userId} onChange={e => setUserId(e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <label htmlFor="filter-action" className="text-sm font-medium">Action</label>
          <Input id="filter-action" placeholder="search" value={action} onChange={e => setAction(e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <label htmlFor="filter-resource" className="text-sm font-medium">Resource Type</label>
          <Input id="filter-resource" placeholder="ENTITY" value={resourceType} onChange={e => setResourceType(e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <label htmlFor="filter-status" className="text-sm font-medium">Status</label>
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger id="filter-status" className="w-full">
              <SelectValue placeholder="Any" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">Any</SelectItem>
              <SelectItem value="SUCCESS">SUCCESS</SelectItem>
              <SelectItem value="DENIED">DENIED</SelectItem>
              <SelectItem value="FAILURE">FAILURE</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-1.5">
          <label htmlFor="filter-start" className="text-sm font-medium">Start Time (ISO)</label>
          <Input id="filter-start" type="datetime-local" value={startTime} onChange={e => setStartTime(e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <label htmlFor="filter-end" className="text-sm font-medium">End Time (ISO)</label>
          <Input id="filter-end" type="datetime-local" value={endTime} onChange={e => setEndTime(e.target.value)} />
        </div>
      </Panel>

      {/* Content */}
      {loading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full border-b-2 border-primary h-8 w-8" />
        </div>
      )}
      {error && (
        <div className="border border-destructive/30 bg-destructive/10 p-4 rounded">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}
      {!loading && !error && (
        <Panel title="Audit Records" subtitle={`${totalEvents} records`}>
          {records.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No audit records match the selected filters.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Resource Type</TableHead>
                  <TableHead>Resource ID</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {records.map((r) => (
                  <TableRow key={r.audit_id} className="hover:bg-muted/50 cursor-pointer" onClick={() => {}}
                  >
                    <TableCell>{new Date(r.timestamp).toLocaleString()}</TableCell>
                    <TableCell>{r.user_id}</TableCell>
                    <TableCell>{r.role}</TableCell>
                    <TableCell>{r.action}</TableCell>
                    <TableCell>{r.resource_type}</TableCell>
                    <TableCell>{r.resource_id ?? "-"}</TableCell>
                    <TableCell>{renderStatusBadge(r.status)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Panel>
      )}
    </div>
  );
}
