import type {
  Severity,
  Anomaly,
  AuditEvent,
  Case,
  Cluster,
  Communication,
  Dataset,
  Entity,
  HiddenRelationship,
  Relationship,
  TimelineEvent,
  Transaction,
} from "./types";

export const investigator = {
  name: "Insp. A. Rathore",
  badge: "CYB-4471",
  unit: "Cyber Crime Cell — Zone 2",
  roles: ["Investigator", "Senior Officer", "Administrator"] as const,
};

export const platform = {
  name: "SENTINEL",
  full: "Digital Investigation Intelligence Platform",
  motto: "From Scattered Data to Actionable Intelligence.",
};

export const kpis = [
  { label: "Active Cases", value: "24", trend: "+3", direction: "up" as const, hint: "vs last week" },
  { label: "Entities Analyzed", value: "12,481", trend: "+1,204", direction: "up" as const, hint: "after last import" },
  { label: "Relationships Discovered", value: "38,291", trend: "+2,870", direction: "up" as const, hint: "graph expansion" },
  { label: "Active Alerts", value: "137", trend: "+12", direction: "up" as const, hint: "last 24h" },
  { label: "High-Priority Leads", value: "23", trend: "+4", direction: "up" as const, hint: "requires review" },
];

export const cases: Case[] = [
  {
    id: "CASE-2026-1024",
    name: "Online Financial Fraud Investigation",
    type: "Financial Fraud",
    status: "Active",
    priority: "HIGH",
    entities: 4281,
    alerts: 31,
    lastActivity: "12 minutes ago",
    investigator: "Insp. A. Rathore",
    incidentDate: "2026-08-16",
    description:
      "Reported online financial fraud involving layered transfers across multiple accounts, coordinated call activity and correlated social/IP footprints within a two-hour incident window.",
  },
  {
    id: "CASE-2026-0987",
    name: "Coordinated Digital Fraud",
    type: "Organized Digital Fraud",
    status: "Active",
    priority: "HIGH",
    entities: 2914,
    alerts: 22,
    lastActivity: "1 hour ago",
    investigator: "SI M. Kulkarni",
    incidentDate: "2026-08-09",
    description: "Multiple complainants reporting a repeated fraud script across authorized datasets.",
  },
  {
    id: "CASE-2026-0955",
    name: "Suspicious Transaction Network",
    type: "Suspicious Financial Network",
    status: "Under Review",
    priority: "MEDIUM",
    entities: 1873,
    alerts: 14,
    lastActivity: "5 hours ago",
    investigator: "Insp. R. Devi",
    incidentDate: "2026-07-28",
    description: "Layered account network flagged for rapid pass-through fund movement.",
  },
  {
    id: "CASE-2026-0921",
    name: "SIM / Communication Abuse",
    type: "Cybercrime",
    status: "Active",
    priority: "MEDIUM",
    entities: 1102,
    alerts: 9,
    lastActivity: "yesterday",
    investigator: "SI P. Bhatt",
    incidentDate: "2026-07-14",
    description: "Bulk SIM usage pattern observed across authorized telecom records.",
  },
  {
    id: "CASE-2026-0899",
    name: "Cyber-enabled Financial Crime",
    type: "Cybercrime",
    status: "Under Review",
    priority: "LOW",
    entities: 764,
    alerts: 4,
    lastActivity: "3 days ago",
    investigator: "Insp. A. Rathore",
    incidentDate: "2026-06-30",
    description: "Historical case retained for cross-case correlation analysis.",
  },
];

export const primaryCase = cases[0]!;

const CASE_ID = primaryCase.id;

export const entities: Entity[] = [
  {
    id: "ENT-1092",
    label: "Person — Subject 1092",
    type: "Person",
    domain: "Cross-Domain",
    priority: "HIGH",
    score: 87,
    scoreBreakdown: [
      { label: "Communication anomalies", points: 18 },
      { label: "Financial anomalies", points: 27 },
      { label: "Cross-domain connections", points: 21 },
      { label: "Incident-window activity", points: 14 },
      { label: "Network centrality", points: 7 },
    ],
    firstObserved: "2026-08-12",
    lastObserved: "2026-08-16",
    cluster: "CL-01",
    identifiers: [
      { label: "Phone", value: "+91 XXXXX 3210" },
      { label: "Bank Accounts", value: "AC-48291, AC-77218" },
      { label: "Social Accounts", value: "SOC-1001" },
      { label: "IP Addresses", value: "IP-1001, IP-1002, IP-1003" },
      { label: "Devices", value: "DEV-1001, DEV-1002" },
    ],
    activity: { calls: 38, transactions: 12, socialEvents: 16, anomalies: 5 },
    findings: [
      "Connected to 4 accounts carrying financial anomalies",
      "Communication spike observed during the incident window",
      "Acts as a potential bridge between Cluster 01 and Cluster 02",
      "Appears in 3 transaction paths flagged for review",
    ],
    caseId: CASE_ID,
  },
  {
    id: "ENT-1001",
    label: "Person — Subject 1001",
    type: "Person",
    domain: "Cross-Domain",
    priority: "HIGH",
    score: 74,
    scoreBreakdown: [
      { label: "Financial anomalies", points: 26 },
      { label: "Cross-domain connections", points: 18 },
      { label: "Incident-window activity", points: 16 },
      { label: "Communication anomalies", points: 9 },
      { label: "Network centrality", points: 5 },
    ],
    firstObserved: "2026-08-11",
    lastObserved: "2026-08-16",
    cluster: "CL-01",
    identifiers: [
      { label: "Phone", value: "+91 XXXXX 1145" },
      { label: "Bank Accounts", value: "AC-99102" },
      { label: "Social Accounts", value: "SOC-1002" },
      { label: "IP Addresses", value: "IP-1001" },
    ],
    activity: { calls: 24, transactions: 9, socialEvents: 6, anomalies: 3 },
    findings: [
      "Originating party of the first flagged transfer in the incident window",
      "Shares an IP session with ENT-1092",
    ],
    caseId: CASE_ID,
  },
  {
    id: "ENT-1002",
    label: "Person — Subject 1002",
    type: "Person",
    domain: "Cross-Domain",
    priority: "MEDIUM",
    score: 61,
    scoreBreakdown: [
      { label: "Financial anomalies", points: 20 },
      { label: "Communication anomalies", points: 15 },
      { label: "Cross-domain connections", points: 14 },
      { label: "Incident-window activity", points: 8 },
      { label: "Network centrality", points: 4 },
    ],
    firstObserved: "2026-08-12",
    lastObserved: "2026-08-16",
    cluster: "CL-02",
    identifiers: [
      { label: "Phone", value: "+91 XXXXX 7788" },
      { label: "Bank Accounts", value: "AC-12038" },
      { label: "Social Accounts", value: "SOC-1003" },
    ],
    activity: { calls: 19, transactions: 7, socialEvents: 11, anomalies: 2 },
    findings: ["Receives onward transfers within minutes of incoming credits"],
    caseId: CASE_ID,
  },
  {
    id: "ENT-1003",
    label: "Person — Subject 1003",
    type: "Person",
    domain: "Cross-Domain",
    priority: "MEDIUM",
    score: 55,
    scoreBreakdown: [
      { label: "Communication anomalies", points: 21 },
      { label: "Cross-domain connections", points: 12 },
      { label: "Incident-window activity", points: 12 },
      { label: "Financial anomalies", points: 6 },
      { label: "Network centrality", points: 4 },
    ],
    firstObserved: "2026-08-13",
    lastObserved: "2026-08-16",
    cluster: "CL-02",
    identifiers: [{ label: "Phone", value: "+91 XXXXX 4402" }],
    activity: { calls: 31, transactions: 2, socialEvents: 4, anomalies: 2 },
    findings: ["23 new communication relationships detected within 30 minutes"],
    caseId: CASE_ID,
  },
  {
    id: "ENT-1004",
    label: "Person — Subject 1004",
    type: "Person",
    domain: "Cross-Domain",
    priority: "LOW",
    score: 34,
    scoreBreakdown: [
      { label: "Cross-domain connections", points: 14 },
      { label: "Incident-window activity", points: 10 },
      { label: "Communication anomalies", points: 6 },
      { label: "Network centrality", points: 4 },
    ],
    firstObserved: "2026-08-14",
    lastObserved: "2026-08-15",
    cluster: "CL-03",
    identifiers: [{ label: "Phone", value: "+91 XXXXX 9931" }],
    activity: { calls: 8, transactions: 1, socialEvents: 3, anomalies: 0 },
    findings: ["Peripheral entity; retained for completeness of the network view"],
    caseId: CASE_ID,
  },
  ...phoneEntities(),
  ...accountEntities(),
  ...socialEntities(),
  ...ipEntities(),
  ...deviceEntities(),
];

function base(
  id: string,
  label: string,
  type: Entity["type"],
  domain: Entity["domain"],
  priority: Entity["priority"],
  score: number,
  cluster: string,
  extras: Partial<Entity> = {},
): Entity {
  return {
    id,
    label,
    type,
    domain,
    priority,
    score,
    scoreBreakdown: [
      { label: "Incident-window activity", points: Math.round(score * 0.32) },
      { label: "Cross-domain connections", points: Math.round(score * 0.28) },
      { label: "Anomaly involvement", points: Math.round(score * 0.24) },
      { label: "Network centrality", points: score - Math.round(score * 0.84) },
    ],
    firstObserved: "2026-08-12",
    lastObserved: "2026-08-16",
    cluster,
    identifiers: [],
    activity: { calls: 0, transactions: 0, socialEvents: 0, anomalies: 0 },
    findings: [],
    caseId: CASE_ID,
    ...extras,
  };
}

function phoneEntities(): Entity[] {
  return [
    base("PH-1001", "+91 XXXXX 3210", "Phone", "Telecom", "HIGH", 81, "CL-01", {
      identifiers: [{ label: "Registered To", value: "ENT-1092 (authorized record)" }],
      activity: { calls: 38, transactions: 0, socialEvents: 0, anomalies: 2 },
      findings: ["Call volume during incident window is 4.1x the observed baseline"],
    }),
    base("PH-1002", "+91 XXXXX 7788", "Phone", "Telecom", "MEDIUM", 58, "CL-02", {
      identifiers: [{ label: "Registered To", value: "ENT-1002 (authorized record)" }],
      activity: { calls: 19, transactions: 0, socialEvents: 0, anomalies: 1 },
    }),
    base("PH-1003", "+91 XXXXX 4402", "Phone", "Telecom", "MEDIUM", 52, "CL-02", {
      identifiers: [{ label: "Registered To", value: "ENT-1003 (authorized record)" }],
      activity: { calls: 31, transactions: 0, socialEvents: 0, anomalies: 1 },
      findings: ["23 new communication relationships within 30 minutes"],
    }),
  ];
}

function accountEntities(): Entity[] {
  return [
    base("AC-48291", "Bank Account AC-48291", "Bank Account", "Financial", "HIGH", 88, "CL-01", {
      identifiers: [{ label: "Held By", value: "ENT-1092" }, { label: "Channel", value: "IMPS / UPI" }],
      activity: { calls: 0, transactions: 12, socialEvents: 0, anomalies: 3 },
      findings: ["₹4,80,000 moved across 4 transactions within 9 minutes"],
    }),
    base("AC-77218", "Bank Account AC-77218", "Bank Account", "Financial", "HIGH", 72, "CL-01", {
      identifiers: [{ label: "Held By", value: "ENT-1092" }],
      activity: { calls: 0, transactions: 8, socialEvents: 0, anomalies: 2 },
    }),
    base("AC-99102", "Bank Account AC-99102", "Bank Account", "Financial", "MEDIUM", 63, "CL-01", {
      identifiers: [{ label: "Held By", value: "ENT-1001" }],
      activity: { calls: 0, transactions: 9, socialEvents: 0, anomalies: 1 },
    }),
    base("AC-12038", "Bank Account AC-12038", "Bank Account", "Financial", "MEDIUM", 59, "CL-02", {
      identifiers: [{ label: "Held By", value: "ENT-1002" }],
      activity: { calls: 0, transactions: 7, socialEvents: 0, anomalies: 1 },
    }),
    base("AC-8821", "Bank Account AC-8821", "Bank Account", "Financial", "MEDIUM", 66, "CL-03", {
      identifiers: [{ label: "Held By", value: "Unlinked (pending verification)" }],
      activity: { calls: 0, transactions: 5, socialEvents: 0, anomalies: 2 },
      findings: ["92% of incoming funds transferred onward within the investigation window"],
    }),
  ];
}

function socialEntities(): Entity[] {
  return [
    base("SOC-1001", "Public Profile SOC-1001", "Social Account", "Social", "MEDIUM", 57, "CL-01", {
      identifiers: [{ label: "Data Basis", value: "Public / authorized imported dataset" }],
      activity: { calls: 0, transactions: 0, socialEvents: 16, anomalies: 1 },
    }),
    base("SOC-1002", "Public Profile SOC-1002", "Social Account", "Social", "LOW", 41, "CL-01", {
      identifiers: [{ label: "Data Basis", value: "Public / authorized imported dataset" }],
      activity: { calls: 0, transactions: 0, socialEvents: 6, anomalies: 0 },
    }),
    base("SOC-1003", "Public Profile SOC-1003", "Social Account", "Social", "MEDIUM", 49, "CL-02", {
      identifiers: [{ label: "Data Basis", value: "Public / authorized imported dataset" }],
      activity: { calls: 0, transactions: 0, socialEvents: 11, anomalies: 1 },
    }),
  ];
}

function ipEntities(): Entity[] {
  return [
    base("IP-1001", "IP 103.x.x.41", "IP Address", "Network", "HIGH", 69, "CL-01", {
      identifiers: [{ label: "Observed Sessions", value: "42 (IPDR)" }],
      activity: { calls: 0, transactions: 0, socialEvents: 0, anomalies: 2 },
      findings: ["Shared session origin across two otherwise separate clusters"],
    }),
    base("IP-1002", "IP 45.x.x.118", "IP Address", "Network", "LOW", 32, "CL-02", {
      identifiers: [{ label: "Observed Sessions", value: "11 (IPDR)" }],
    }),
    base("IP-1003", "IP 192.168.x.x", "IP Address", "Network", "LOW", 28, "CL-03", {
      identifiers: [{ label: "Observed Sessions", value: "7 (IPDR, NAT-private)" }],
    }),
  ];
}

function deviceEntities(): Entity[] {
  return [
    base("DEV-1001", "Device DEV-1001", "Device", "Network", "MEDIUM", 47, "CL-01", {
      identifiers: [{ label: "Handset Class", value: "Android (IMEI redacted)" }],
    }),
    base("DEV-1002", "Device DEV-1002", "Device", "Network", "LOW", 30, "CL-02", {
      identifiers: [{ label: "Handset Class", value: "Android (IMEI redacted)" }],
    }),
  ];
}

export const relationships: Relationship[] = [
  rel("ENT-1092", "PH-1001", "USES", 5, 61, "Authorized subscriber record"),
  rel("ENT-1092", "AC-48291", "OWNS", 5, 12, "Account mapping from bank statement import"),
  rel("ENT-1092", "AC-77218", "OWNS", 4, 8, "Secondary account"),
  rel("ENT-1092", "SOC-1001", "ASSOCIATED_WITH", 3, 16, "Correlated public profile identifier"),
  rel("ENT-1092", "IP-1001", "LOGGED_FROM", 4, 22, "IPDR session overlap"),
  rel("ENT-1092", "DEV-1001", "USES", 3, 14, "Device fingerprint recurrence"),
  rel("ENT-1001", "AC-99102", "OWNS", 4, 9, "Account mapping"),
  rel("ENT-1001", "IP-1001", "LOGGED_FROM", 3, 12, "Shared session origin"),
  rel("ENT-1001", "SOC-1002", "ASSOCIATED_WITH", 2, 6, "Correlated public profile"),
  rel("PH-1001", "PH-1002", "CALLED", 5, 18, "18 calls, 4 within incident window"),
  rel("PH-1002", "PH-1003", "CALLED", 4, 11, "Onward call chain"),
  rel("PH-1001", "PH-1003", "COMMUNICATED_WITH", 3, 6, "SMS + short calls"),
  rel("ENT-1002", "PH-1002", "USES", 5, 19, "Authorized subscriber record"),
  rel("ENT-1003", "PH-1003", "USES", 5, 31, "Authorized subscriber record"),
  rel("ENT-1002", "AC-12038", "OWNS", 4, 7, "Account mapping"),
  rel("ENT-1002", "SOC-1003", "ASSOCIATED_WITH", 3, 11, "Correlated public profile"),
  rel("AC-99102", "AC-48291", "TRANSFERRED_TO", 5, 3, "₹1,00,000 during incident window"),
  rel("AC-48291", "AC-77218", "TRANSFERRED_TO", 5, 4, "₹95,000 pass-through"),
  rel("AC-77218", "AC-12038", "TRANSFERRED_TO", 4, 3, "₹1,45,000 layered onward"),
  rel("AC-12038", "AC-8821", "TRANSFERRED_TO", 4, 2, "₹1,40,000 onward"),
  rel("AC-8821", "AC-48291", "CONNECTED_TO", 2, 1, "Return leg observed"),
  rel("ENT-1003", "ENT-1004", "ASSOCIATED_WITH", 2, 4, "Repeated co-location in call records"),
  rel("ENT-1004", "IP-1003", "LOGGED_FROM", 2, 7, "IPDR session"),
  rel("ENT-1002", "IP-1002", "LOGGED_FROM", 3, 11, "IPDR session"),
  rel("ENT-1002", "DEV-1002", "USES", 3, 5, "Device fingerprint"),
  rel("SOC-1001", "SOC-1003", "CONNECTED_TO", 3, 9, "Public interaction dataset"),
];

function rel(
  source: string,
  target: string,
  type: Relationship["type"],
  weight: number,
  observations: number,
  note: string,
): Relationship {
  return {
    id: `${source}__${type}__${target}`,
    source,
    target,
    type,
    weight,
    observations,
    firstSeen: "2026-08-12",
    note,
  };
}

export const transactions: Transaction[] = [
  tx("TXN-88010", "2026-08-16 18:15", "AC-99102", "AC-48291", 100000, "IMPS", "HIGH"),
  tx("TXN-88011", "2026-08-16 18:19", "AC-48291", "AC-77218", 95000, "IMPS", "HIGH"),
  tx("TXN-88012", "2026-08-16 18:22", "AC-48291", "AC-12038", 145000, "UPI", "HIGH"),
  tx("TXN-88013", "2026-08-16 18:24", "AC-48291", "AC-8821", 140000, "IMPS", "HIGH"),
  tx("TXN-88014", "2026-08-16 18:34", "AC-77218", "AC-12038", 95000, "NEFT", "MEDIUM"),
  tx("TXN-88015", "2026-08-16 18:52", "AC-12038", "AC-8821", 140000, "IMPS", "MEDIUM"),
  tx("TXN-88016", "2026-08-16 19:10", "AC-8821", "AC-99102", 42000, "UPI", "MEDIUM"),
  tx("TXN-87990", "2026-08-15 11:02", "AC-99102", "AC-12038", 18000, "UPI", "NORMAL"),
  tx("TXN-87991", "2026-08-15 14:41", "AC-12038", "AC-77218", 7500, "UPI", "NORMAL"),
  tx("TXN-87992", "2026-08-14 09:18", "AC-48291", "AC-99102", 22000, "NEFT", "NORMAL"),
  tx("TXN-87993", "2026-08-14 19:55", "AC-8821", "AC-12038", 61000, "IMPS", "MEDIUM"),
  tx("TXN-87994", "2026-08-13 16:30", "AC-77218", "AC-8821", 34000, "UPI", "NORMAL"),
  tx("TXN-87995", "2026-08-13 10:12", "AC-99102", "AC-48291", 15000, "UPI", "NORMAL"),
  tx("TXN-87996", "2026-08-12 20:04", "AC-48291", "AC-12038", 88000, "RTGS", "MEDIUM"),
];

function tx(
  id: string,
  timestamp: string,
  sender: string,
  receiver: string,
  amount: number,
  type: Transaction["type"],
  priority: Transaction["priority"],
): Transaction {
  return {
    id,
    timestamp,
    sender,
    receiver,
    amount,
    type,
    priority,
    caseId: CASE_ID,
    status: priority === "HIGH" ? "Requires Review" : priority === "MEDIUM" ? "Reviewed" : "Cleared",
  };
}

export const communications: Communication[] = [
  comm("COM-5501", "2026-08-16 18:02", "PH-1001", "PH-1002", "4m 21s", "Voice Call", true, "HIGH"),
  comm("COM-5502", "2026-08-16 18:21", "PH-1002", "PH-1003", "2m 13s", "Voice Call", true, "HIGH"),
  comm("COM-5503", "2026-08-16 18:31", "PH-1001", "PH-1003", "0m 48s", "Voice Call", false, "MEDIUM"),
  comm("COM-5504", "2026-08-16 18:33", "PH-1001", "IP-1001", "12m 04s", "IPDR Session", false, "MEDIUM"),
  comm("COM-5505", "2026-08-16 18:47", "PH-1002", "PH-1001", "1m 55s", "Voice Call", false, "MEDIUM"),
  comm("COM-5506", "2026-08-16 19:12", "PH-1003", "PH-1002", "3m 02s", "Voice Call", true, "MEDIUM"),
  comm("COM-5507", "2026-08-15 12:41", "PH-1001", "PH-1002", "5m 10s", "Voice Call", false, "NORMAL"),
  comm("COM-5508", "2026-08-15 17:22", "PH-1002", "PH-1003", "0m 32s", "SMS", false, "NORMAL"),
  comm("COM-5509", "2026-08-14 09:03", "PH-1001", "PH-1003", "2m 48s", "Voice Call", false, "NORMAL"),
  comm("COM-5510", "2026-08-13 21:15", "PH-1003", "PH-1001", "6m 27s", "Voice Call", false, "NORMAL"),
];

function comm(
  id: string,
  timestamp: string,
  from: string,
  to: string,
  duration: string,
  kind: Communication["kind"],
  newRelationship: boolean,
  priority: Communication["priority"],
): Communication {
  return { id, timestamp, from, to, duration, kind, newRelationship, priority };
}

export const anomalies: Anomaly[] = [
  {
    id: "ANO-3301",
    title: "Transaction Burst",
    domain: "Financial",
    severity: "HIGH",
    entityId: "AC-48291",
    entityLabel: "Account AC-48291",
    detectedAt: "16 Aug 2026, 18:15",
    confidence: 0.94,
    pattern: "4 transactions · ₹4,80,000 total · 9 minute span",
    explanation:
      "Transaction volume and frequency significantly deviate from the entity's observed baseline during the selected investigation window.",
    signals: [
      "Transaction frequency is significantly above the historical baseline.",
      "Multiple counterparties were involved within a short time interval.",
      "The activity overlaps with the investigation incident window.",
      "The receiving account is connected to another flagged entity.",
    ],
    relevance: "Review the connected transaction chain and associated entities.",
    relatedEntities: ["ENT-1092", "AC-77218", "AC-12038", "AC-8821"],
  },
  {
    id: "ANO-3302",
    title: "Bridge Entity Detected",
    domain: "Cross-Domain",
    severity: "HIGH",
    entityId: "ENT-1092",
    entityLabel: "Entity ENT-1092",
    detectedAt: "16 Aug 2026, 18:38",
    confidence: 0.91,
    pattern: "Connects Cluster 01 ↔ Cluster 02 across telecom + financial domains",
    explanation:
      "The entity provides the only observed path between two otherwise separate investigation clusters within the analyzed dataset.",
    signals: [
      "Removal of the entity disconnects two clusters in the relationship graph.",
      "Relationships span more than one data domain.",
      "Bridging relationships were first observed inside the incident window.",
      "Adjacent entities on both sides carry open anomalies.",
    ],
    relevance: "Explore both clusters through this entity's relationship set.",
    relatedEntities: ["PH-1001", "AC-48291", "IP-1001", "ENT-1002"],
  },
  {
    id: "ANO-3303",
    title: "Communication Spike",
    domain: "Telecom",
    severity: "MEDIUM",
    entityId: "PH-1003",
    entityLabel: "Phone +91 XXXXX 3210",
    detectedAt: "16 Aug 2026, 18:44",
    confidence: 0.82,
    pattern: "23 new communication relationships in 30 minutes",
    explanation:
      "New-contact formation rate is far above the entity's normal daily pattern in the authorized CDR dataset.",
    signals: [
      "New-contact rate exceeds the 30-day baseline by 6.4x.",
      "Short-duration calls dominate the burst.",
      "Burst overlaps the incident window.",
      "Two contacted numbers already carry open anomalies.",
    ],
    relevance: "Review the contact list formed during the burst window.",
    relatedEntities: ["PH-1001", "PH-1002", "ENT-1003"],
  },
  {
    id: "ANO-3304",
    title: "Unusual Account Flow",
    domain: "Financial",
    severity: "MEDIUM",
    entityId: "AC-8821",
    entityLabel: "Account AC-8821",
    detectedAt: "16 Aug 2026, 19:02",
    confidence: 0.79,
    pattern: "92% of incoming funds transferred onward within the window",
    explanation:
      "Pass-through ratio is characteristic of a layering step rather than the account's observed historical behaviour.",
    signals: [
      "Incoming-to-outgoing turnaround averages under 11 minutes.",
      "Balance retention is below 8% of credited value.",
      "Counterparties overlap with a flagged transaction chain.",
      "Activity is concentrated in the incident window.",
    ],
    relevance: "Trace the onward beneficiaries and request statement corroboration.",
    relatedEntities: ["AC-12038", "AC-48291"],
  },
  {
    id: "ANO-3305",
    title: "Shared Session Origin",
    domain: "Network",
    severity: "MEDIUM",
    entityId: "IP-1001",
    entityLabel: "IP 103.x.x.41",
    detectedAt: "16 Aug 2026, 18:33",
    confidence: 0.76,
    pattern: "3 distinct entities logged from a single session origin",
    explanation:
      "Multiple otherwise unrelated entities share one session origin during a narrow interval in the IPDR dataset.",
    signals: [
      "Three entity identifiers share one session origin.",
      "Sessions occur within a 21-minute interval.",
      "One of the entities is a flagged bridge entity.",
      "Session origin is not observed in the entities' prior history.",
    ],
    relevance: "Correlate session records with device and telecom activity.",
    relatedEntities: ["ENT-1092", "ENT-1001", "DEV-1001"],
  },
  {
    id: "ANO-3306",
    title: "Correlated Public Activity",
    domain: "Social",
    severity: "LOW",
    entityId: "SOC-1001",
    entityLabel: "Public Profile SOC-1001",
    detectedAt: "16 Aug 2026, 18:41",
    confidence: 0.68,
    pattern: "Public posting activity aligned with financial event timing",
    explanation:
      "Publicly available activity timestamps align closely with flagged financial events in the incident window.",
    signals: [
      "Activity timestamps fall within 7 minutes of flagged transfers.",
      "Profile is correlated with a high-priority entity identifier.",
      "Posting cadence deviates from the imported baseline.",
      "Correlated profile appears in a second cluster.",
    ],
    relevance: "Treat as supporting context only; corroborate with authorized records.",
    relatedEntities: ["ENT-1092", "SOC-1003"],
  },
];

export const alerts = anomalies.slice(0, 4).map((a) => ({
  id: a.id,
  severity: a.severity,
  title: a.title,
  entity: a.entityLabel,
  detail: a.pattern,
  detectedAt: a.detectedAt,
}));

export const timelineEvents: TimelineEvent[] = [
  ev("TL-01", "18:02", "Telecom", "Phone A → Phone B", "Voice call · duration 4m 21s", ["PH-1001", "PH-1002"], "MEDIUM"),
  ev("TL-02", "18:15", "Financial", "AC-99102 → AC-48291", "₹1,00,000 transferred via IMPS", ["AC-99102", "AC-48291"], "HIGH"),
  ev("TL-03", "18:21", "Telecom", "Phone B → Phone C", "Voice call · duration 2m 13s", ["PH-1002", "PH-1003"], "MEDIUM"),
  ev("TL-04", "18:31", "Network", "IP 103.x.x.41", "IPDR session detected for ENT-1092", ["IP-1001", "ENT-1092"], "MEDIUM"),
  ev("TL-05", "18:34", "Financial", "AC-48291 → AC-77218", "₹95,000 onward transfer", ["AC-48291", "AC-77218"], "HIGH"),
  ev("TL-06", "18:41", "Social", "Public Profile SOC-1001", "Public activity detected in imported dataset", ["SOC-1001"], "LOW"),
  ev("TL-07", "18:52", "Financial", "AC-12038 → AC-8821", "₹1,40,000 layered onward", ["AC-12038", "AC-8821"], "HIGH"),
  ev("TL-08", "19:12", "Telecom", "Phone C → Phone B", "Voice call · duration 3m 02s", ["PH-1003", "PH-1002"], "MEDIUM"),
];

function ev(
  id: string,
  time: string,
  domain: TimelineEvent["domain"],
  title: string,
  detail: string,
  entityIds: string[],
  severity: Severity,
): TimelineEvent {
  return { id, time, date: "2026-08-16", domain, title, detail, entityIds, severity };
}

export const datasets: Dataset[] = [
  { id: "DS-01", name: "Telecom CDR Extract", kind: "CDR", status: "Imported", records: 24812, lastUpdated: "16 Aug 2026", source: "Authorized telecom request TR-2291" },
  { id: "DS-02", name: "IPDR Session Logs", kind: "IPDR", status: "Imported", records: 18421, lastUpdated: "16 Aug 2026", source: "Authorized telecom request TR-2292" },
  { id: "DS-03", name: "Bank Statement Bundle", kind: "Bank Statements", status: "Imported", records: 8942, lastUpdated: "16 Aug 2026", source: "Authorized bank response BR-1180" },
  { id: "DS-04", name: "Public Social Activity Export", kind: "Social Activity", status: "Validation Warnings", records: 14821, lastUpdated: "15 Aug 2026", source: "Public / authorized imported dataset" },
];

export const auditEvents: AuditEvent[] = [
  { id: "AUD-01", timestamp: "16 Aug 2026, 17:41", user: "Insp. A. Rathore", role: "Investigator", action: "Uploaded CDR dataset", caseId: CASE_ID, object: "DS-01" },
  { id: "AUD-02", timestamp: "16 Aug 2026, 17:49", user: "System", role: "Service", action: "Entity resolution completed", caseId: CASE_ID, object: "12,481 entities" },
  { id: "AUD-03", timestamp: "16 Aug 2026, 17:58", user: "System", role: "Service", action: "Anomaly detection executed", caseId: CASE_ID, object: "137 anomalies" },
  { id: "AUD-04", timestamp: "16 Aug 2026, 18:46", user: "Insp. A. Rathore", role: "Investigator", action: "Entity reviewed", caseId: CASE_ID, object: "ENT-1092" },
  { id: "AUD-05", timestamp: "16 Aug 2026, 19:02", user: "SI M. Kulkarni", role: "Investigator", action: "Graph expansion executed", caseId: CASE_ID, object: "Cluster CL-02" },
  { id: "AUD-06", timestamp: "16 Aug 2026, 19:20", user: "Insp. A. Rathore", role: "Investigator", action: "Investigation report generated", caseId: CASE_ID, object: "RPT-2026-0044" },
  { id: "AUD-07", timestamp: "16 Aug 2026, 19:33", user: "DySP K. Nair", role: "Senior Officer", action: "Report reviewed", caseId: CASE_ID, object: "RPT-2026-0044" },
];

export const clusters: Cluster[] = [
  { id: "CL-01", name: "Cluster 01", entityCount: 12, centralEntity: "ENT-1092", mostActiveEntity: "AC-48291", bridges: ["ENT-1092"], domains: ["Telecom", "Financial", "Network"] },
  { id: "CL-02", name: "Cluster 02", entityCount: 8, centralEntity: "ENT-1002", mostActiveEntity: "PH-1003", bridges: ["ENT-1092", "IP-1001"], domains: ["Telecom", "Social"] },
  { id: "CL-03", name: "Cluster 03", entityCount: 21, centralEntity: "AC-8821", mostActiveEntity: "AC-8821", bridges: ["AC-12038"], domains: ["Financial"] },
];

export const hiddenRelationships: HiddenRelationship[] = [
  {
    id: "HR-01",
    title: "Potential Bridge Entity",
    entityId: "ENT-1092",
    clusterA: "Cluster 01",
    clusterB: "Cluster 02",
    strength: "HIGH",
    evidence: ["4 communication relationships", "2 financial relationships", "Activity overlap during incident window"],
  },
  {
    id: "HR-02",
    title: "Shared Session Origin Link",
    entityId: "IP-1001",
    clusterA: "Cluster 01",
    clusterB: "Cluster 02",
    strength: "MEDIUM",
    evidence: ["3 entities logged from one session origin", "Sessions within a 21-minute interval"],
  },
  {
    id: "HR-03",
    title: "Layering Path Overlap",
    entityId: "AC-12038",
    clusterA: "Cluster 02",
    clusterB: "Cluster 03",
    strength: "MEDIUM",
    evidence: ["2 onward transfer paths converge", "Pass-through ratio above 90% on both legs"],
  },
];

export const transactionVolumeSeries = [
  { time: "12 Aug", volume: 210000, flagged: 88000 },
  { time: "13 Aug", volume: 154000, flagged: 34000 },
  { time: "14 Aug", volume: 178000, flagged: 61000 },
  { time: "15 Aug", volume: 132000, flagged: 25500 },
  { time: "16 Aug 17h", volume: 96000, flagged: 0 },
  { time: "16 Aug 18h", volume: 575000, flagged: 480000 },
  { time: "16 Aug 19h", volume: 182000, flagged: 140000 },
  { time: "16 Aug 20h", volume: 74000, flagged: 12000 },
];

export const communicationVolumeSeries = [
  { time: "12 Aug", calls: 21, newLinks: 3 },
  { time: "13 Aug", calls: 34, newLinks: 4 },
  { time: "14 Aug", calls: 28, newLinks: 2 },
  { time: "15 Aug", calls: 41, newLinks: 6 },
  { time: "16 Aug 17h", calls: 12, newLinks: 1 },
  { time: "16 Aug 18h", calls: 67, newLinks: 23 },
  { time: "16 Aug 19h", calls: 39, newLinks: 8 },
  { time: "16 Aug 20h", calls: 14, newLinks: 2 },
];

export const topContacts = [
  { number: "+91 XXXXX 3210", calls: 38 },
  { number: "+91 XXXXX 4402", calls: 31 },
  { number: "+91 XXXXX 7788", calls: 19 },
  { number: "+91 XXXXX 1145", calls: 24 },
  { number: "+91 XXXXX 9931", calls: 8 },
];

export const moneyFlowChain = [
  { from: "AC-99102", to: "AC-48291", amount: 100000 },
  { from: "AC-48291", to: "AC-77218", amount: 95000 },
  { from: "AC-48291", to: "AC-12038", amount: 145000 },
  { from: "AC-12038", to: "AC-8821", amount: 140000 },
];

export const crossDomainChain = [
  { domain: "Telecom" as const, id: "PH-1001", label: "Phone +91 XXXXX 3210", note: "Authorized CDR record" },
  { domain: "Cross-Domain" as const, id: "ENT-1092", label: "Entity ENT-1092", note: "Resolved person entity" },
  { domain: "Financial" as const, id: "AC-48291", label: "Bank Account AC-48291", note: "Bank statement import" },
  { domain: "Financial" as const, id: "TXN-88011", label: "Transaction ₹95,000", note: "Flagged transfer" },
  { domain: "Financial" as const, id: "AC-77218", label: "Bank Account AC-77218", note: "Onward beneficiary" },
  { domain: "Social" as const, id: "SOC-1001", label: "Public Profile SOC-1001", note: "Public / authorized dataset" },
  { domain: "Network" as const, id: "IP-1001", label: "IP 103.x.x.41", note: "IPDR session origin" },
];

export const actionableLead = {
  entityId: "ENT-1092",
  headline:
    "Entity ENT-1092 should be reviewed as a high-priority investigative lead because it connects multiple anomalous financial and communication events within the selected incident window.",
  supporting: [
    "Bridges Cluster 01 and Cluster 02 across telecom and financial domains",
    "Linked to ₹4,80,000 moved in 9 minutes through connected accounts",
    "Communication spike and IPDR session overlap the incident window",
  ],
};

export function getEntity(id: string) {
  return entities.find((e) => e.id.toLowerCase() === id.toLowerCase());
}

export function relationshipsFor(id: string) {
  return relationships.filter((r) => r.source === id || r.target === id);
}

export function neighborsOf(id: string) {
  return relationshipsFor(id).map((r) => (r.source === id ? r.target : r.source));
}

export function anomaliesFor(id: string) {
  return anomalies.filter((a) => a.entityId === id || a.relatedEntities.includes(id));
}

export function transactionsFor(id: string) {
  return transactions.filter((t) => t.sender === id || t.receiver === id);
}

export function communicationsFor(id: string) {
  return communications.filter((c) => c.from === id || c.to === id);
}

export function timelineFor(id: string) {
  return timelineEvents.filter((e) => e.entityIds.includes(id));
}

export const inr = (n: number) => `₹${n.toLocaleString("en-IN")}`;
