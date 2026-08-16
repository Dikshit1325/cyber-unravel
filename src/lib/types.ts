export type Severity = "HIGH" | "MEDIUM" | "LOW";
export type Domain = "Telecom" | "Financial" | "Social" | "Network" | "Cross-Domain";
export type EntityType =
  | "Person"
  | "Phone"
  | "Bank Account"
  | "Social Account"
  | "IP Address"
  | "Device"
  | "Transaction"
  | "Location";

export type RelationshipType =
  | "CALLED"
  | "TRANSFERRED_TO"
  | "USES"
  | "OWNS"
  | "CONNECTED_TO"
  | "ASSOCIATED_WITH"
  | "LOGGED_FROM"
  | "COMMUNICATED_WITH";

export interface Case {
  id: string;
  name: string;
  type: string;
  status: "Active" | "Under Review" | "Closed";
  priority: Severity;
  entities: number;
  alerts: number;
  lastActivity: string;
  investigator: string;
  incidentDate: string;
  description: string;
}

export interface PriorityFactor {
  label: string;
  points: number;
}

export interface Entity {
  id: string;
  label: string;
  type: EntityType;
  domain: Domain;
  priority: Severity;
  score: number;
  scoreBreakdown: PriorityFactor[];
  firstObserved: string;
  lastObserved: string;
  cluster: string;
  identifiers: { label: string; value: string }[];
  activity: { calls: number; transactions: number; socialEvents: number; anomalies: number };
  findings: string[];
  caseId: string;
}

export interface Relationship {
  id: string;
  source: string;
  target: string;
  type: RelationshipType;
  weight: number;
  firstSeen: string;
  observations: number;
  note: string;
}

export interface Transaction {
  id: string;
  timestamp: string;
  sender: string;
  receiver: string;
  amount: number;
  type: "IMPS" | "NEFT" | "UPI" | "RTGS" | "Cash Deposit";
  priority: Severity | "NORMAL";
  caseId: string;
  status: "Requires Review" | "Reviewed" | "Cleared";
}

export interface Communication {
  id: string;
  timestamp: string;
  from: string;
  to: string;
  duration: string;
  kind: "Voice Call" | "SMS" | "IPDR Session";
  newRelationship: boolean;
  priority: Severity | "NORMAL";
}

export interface Anomaly {
  id: string;
  title: string;
  domain: Domain;
  severity: Severity;
  entityId: string;
  entityLabel: string;
  detectedAt: string;
  confidence: number;
  pattern: string;
  explanation: string;
  signals: string[];
  relevance: string;
  relatedEntities: string[];
}

export interface TimelineEvent {
  id: string;
  time: string;
  date: string;
  domain: Domain;
  title: string;
  detail: string;
  entityIds: string[];
  severity?: Severity;
}

export interface Dataset {
  id: string;
  name: string;
  kind: "CDR" | "IPDR" | "Bank Statements" | "Social Activity";
  status: "Imported" | "Processing" | "Validation Warnings";
  records: number;
  lastUpdated: string;
  source: string;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  user: string;
  role: string;
  action: string;
  caseId: string;
  object: string;
}

export interface Cluster {
  id: string;
  name: string;
  entityCount: number;
  centralEntity: string;
  mostActiveEntity: string;
  bridges: string[];
  domains: Domain[];
}

export interface HiddenRelationship {
  id: string;
  title: string;
  entityId: string;
  clusterA: string;
  clusterB: string;
  strength: Severity;
  evidence: string[];
}
