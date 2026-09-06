// API Service Layer for FastAPI Backend
// Base URL: http://127.0.0.1:8000

const API_BASE_URL = "http://127.0.0.1:8000";

export function getAuthHeaders(): HeadersInit {
  const userId =
    (typeof window !== "undefined" && localStorage.getItem("sentinel_user_id")) ||
    "investigator_01";
  return {
    "X-User-Id": userId,
  };
}

// ============================================================
// TYPE DEFINITIONS
// ============================================================

export interface CaseResponse {
  case_id: string;
  case_name: string;
  status: string;
  priority: string;
  incident_date: string;
  summary: {
    persons: number;
    calls: number;
    transactions: number;
    ipdr_events: number;
    social_events: number;
    graph_nodes: number;
    graph_edges: number;
  };
  description?: string;
}

export interface Entity {
  entity_id: string;
  name: string;
  age?: number | null;
  phones: string[];
  bank_accounts: string[];
  ip_addresses: string[];
  social_accounts: string[];
  device_ids: string[];
  connections: Array<{
    entity: string;
    relationship: string;
  }>;
}

export interface GraphNode {
  id: string;
  node_type?: string;
  entity_id?: string;
  [key: string]: any;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship?: string;
  [key: string]: any;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  node_count: number;
  edge_count: number;
}

export interface TimelineEvent {
  event_type: string;
  direction: string;
  timestamp: string;
  related_entity?: string;
  related_account?: string;
  amount?: number | null;
  duration_seconds?: number | null;
  ip_address?: string;
  device_id?: string;
  session_duration_seconds?: number | null;
  platform?: string;
  activity_type?: string;
  source: string;
  source_dataset: string;
  scenario_tag?: string;
  channel?: string;
}

export interface TimelineResponse {
  entity_id: string;
  timeline: TimelineEvent[];
  count: number;
}

export interface TransactionItem {
  transaction_id: string;
  id: string;
  timestamp: string;
  sender_account: string;
  receiver_account: string;
  sender: string;
  receiver: string;
  sender_name?: string | null;
  receiver_name?: string | null;
  sender_entity_id?: string | null;
  receiver_entity_id?: string | null;
  amount: number;
  channel: string;
  type: string;
  scenario_tag: string;
  priority: string;
  status: string;
  case_id: string;
  caseId: string;
  currency: string;
  entity_ids: string[];
}

export interface TransactionsSummary {
  total_volume: number;
  high_value_count: number;
  unique_accounts: number;
  filtered_count: number;
}

export interface TransactionsResponse {
  total: number;
  page: number;
  page_size: number;
  summary: TransactionsSummary;
  transactions: TransactionItem[];
}

export interface CommunicationItem {
  communication_id: string;
  id: string;
  cdr_id: string;
  caller: string;
  receiver: string;
  from: string;
  to: string;
  caller_entity_id?: string | null;
  receiver_entity_id?: string | null;
  caller_name?: string | null;
  receiver_name?: string | null;
  caller_phone?: string | null;
  receiver_phone?: string | null;
  timestamp: string;
  duration_seconds: number;
  duration: string;
  channel: string;
  kind: string;
  type: string;
  scenario_tag: string;
  priority: string;
  status: string;
  case_id: string;
  caseId: string;
  entity_ids: string[];
}

export interface CommunicationsSummary {
  total_calls: number;
  total_duration_seconds: number;
  avg_duration_seconds: number;
  high_priority_count: number;
  unique_contacts: number;
  filtered_count: number;
}

export interface CommunicationsResponse {
  total: number;
  page: number;
  page_size: number;
  summary: CommunicationsSummary;
  communications: CommunicationItem[];
}

export interface AuditRecord {
  audit_id: string;
  timestamp: string;
  user_id: string;
  role: string;
  action: string;
  endpoint: string;
  resource_type: string;
  status: string;
  resource_id?: string | null;
  metadata?: Record<string, any>;
}

export interface AuditResponse {
  total: number;
  audit_records: AuditRecord[];
}

// ============================================================
// API FUNCTIONS
// ============================================================

/**
 * Fetch case information
 */
export async function getCase(): Promise<CaseResponse> {
  const response = await fetch(`${API_BASE_URL}/api/case`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch case: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch entity information by ID
 */
export async function getEntity(entityId: string): Promise<Entity> {
  const response = await fetch(`${API_BASE_URL}/api/entity/${entityId}`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Entity not found: ${entityId}`);
    }
    throw new Error(`Failed to fetch entity: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch investigation graph with nodes and edges
 */
export async function getGraph(): Promise<GraphResponse> {
  const response = await fetch(`${API_BASE_URL}/api/graph`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch graph: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch timeline events for an entity
 */
export async function getEntityTimeline(entityId: string): Promise<TimelineResponse> {
  const response = await fetch(`${API_BASE_URL}/api/entity/${entityId}/timeline`, {
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Entity not found: ${entityId}`);
    }
    throw new Error(`Failed to fetch timeline: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch live transactions with filtering and pagination
 */
export async function getTransactions(params: {
  transaction_id?: string;
  entity_id?: string;
  account?: string;
  sender?: string;
  receiver?: string;
  min_amount?: number;
  max_amount?: number;
  start_time?: string;
  end_time?: string;
  channel?: string;
  scenario_tag?: string;
  sort?: string;
  page?: number;
  page_size?: number;
} = {}): Promise<TransactionsResponse> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.append(key, String(value));
    }
  });
  const url = `${API_BASE_URL}/api/transactions/?${query.toString()}`;
  const response = await fetch(url, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch transactions: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch single transaction by ID
 */
export async function getTransactionById(transactionId: string): Promise<TransactionItem> {
  const response = await fetch(`${API_BASE_URL}/api/transactions/${transactionId}`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Transaction not found: ${transactionId}`);
    }
    throw new Error(`Failed to fetch transaction: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch live communications / CDR records with filtering and pagination
 */
export async function getCommunications(params: {
  communication_id?: string;
  cdr_id?: string;
  entity_id?: string;
  caller?: string;
  receiver?: string;
  phone?: string;
  min_duration?: number;
  max_duration?: number;
  start_time?: string;
  end_time?: string;
  scenario_tag?: string;
  sort?: string;
  page?: number;
  page_size?: number;
} = {}): Promise<CommunicationsResponse> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.append(key, String(value));
    }
  });
  const url = `${API_BASE_URL}/api/communications/?${query.toString()}`;
  const response = await fetch(url, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch communications: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch single communication record by ID
 */
export async function getCommunicationById(communicationId: string): Promise<CommunicationItem> {
  const response = await fetch(`${API_BASE_URL}/api/communications/${communicationId}`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`Communication not found: ${communicationId}`);
    }
    throw new Error(`Failed to fetch communication: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch audit records
 */
export async function getAudit(params: {
  user_id?: string;
  action?: string;
  resource_type?: string;
  start_time?: string;
  end_time?: string;
  status?: string;
} = {}): Promise<AuditResponse> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) query.append(key, value);
  });
  const url = `${API_BASE_URL}/api/audit/?${query.toString()}`;
  const response = await fetch(url, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch audit logs: ${response.statusText}`);
  }
  return response.json();
}
export interface SearchResult {
  id: string;
  type: string;
  title: string;
  subtitle: string;
  entity_id?: string | null;
  route: string;
}

export interface SearchResponse {
  total: number;
  limit: number;
  offset: number;
  results: SearchResult[];
}

/**
 * Fetch unified search results.
 */
export async function getSearchResults(params: {
      q: string;
      domain?: string;
      limit?: number;
      offset?: number;
    }): Promise<SearchResponse> {
      const { q, domain, limit = 20, offset = 0 } = params;
      const query = new URLSearchParams({ q });
      if (domain) query.append('domain', domain);
      query.append('limit', String(limit));
      query.append('offset', String(offset));
      const url = `${API_BASE_URL}/api/search/?${query.toString()}`;
      const response = await fetch(url, { headers: getAuthHeaders() });
      if (!response.ok) {
        throw new Error(`Failed to fetch search results: ${response.statusText}`);
      }
      return response.json();
    }

// Fetch actionable lead
export async function getLead() {
  const response = await fetch(`${API_BASE_URL}/api/lead`, { headers: getAuthHeaders() });
  if (!response.ok) {
    throw new Error(`Failed to fetch lead: ${response.statusText}`);
  }
  return response.json();
}

// ============================================================
// RELATIONSHIPS
// ============================================================

export interface Relationship {
  id: string;
  source: string;
  source_name: string;
  target: string;
  target_name: string;
  type: string;
  observations: number;
  first_seen?: string | null;
  last_seen?: string | null;
  source_dataset?: string;
}

export interface RelationshipsResponse {
  total: number;
  limit: number;
  offset: number;
  relationships: Relationship[];
}

/**
 * Fetch hidden relationships from the investigation graph.
 */
export async function getRelationships(params: {
  entity_id?: string;
  limit?: number;
  offset?: number;
} = {}): Promise<RelationshipsResponse> {
  const query = new URLSearchParams();
  if (params.entity_id) query.append("entity_id", params.entity_id);
  query.append("limit", String(params.limit ?? 20));
  query.append("offset", String(params.offset ?? 0));
  const url = `${API_BASE_URL}/api/relationships?${query.toString()}`;
  const response = await fetch(url, { headers: getAuthHeaders() });
  if (!response.ok) {
    throw new Error(`Failed to fetch relationships: ${response.statusText}`);
  }
  return response.json();
}

// ============================================================
// INCIDENT SNAPSHOT
// ============================================================

export interface IncidentEvent {
  event_type: string;
  timestamp: string;
  source_dataset: string;
  source: string;
  entity_id?: string;
  entity_name?: string;
  // CDR fields
  caller?: string;
  caller_name?: string;
  receiver?: string;
  receiver_name?: string;
  duration_seconds?: number;
  // Transaction fields
  sender?: string;
  sender_entity_id?: string;
  sender_name?: string;
  receiver_entity_id?: string;
  amount?: number;
  channel?: string;
  // IPDR fields
  ip_address?: string;
  device_id?: string;
  session_duration_seconds?: number;
  // Social fields
  platform?: string;
  activity_type?: string;
}

export interface IncidentSnapshotResponse {
  entity_id?: string | null;
  case_id: string;
  window_start: string | null;
  window_end: string | null;
  total_events: number;
  events: IncidentEvent[];
  limit: number;
  offset: number;
}

/**
 * Fetch incident snapshot (recent events across entities).
 */
export async function getIncidentSnapshot(params: {
  entity_id?: string;
  window_hours?: number;
  limit?: number;
  offset?: number;
} = {}): Promise<IncidentSnapshotResponse> {
  const query = new URLSearchParams();
  if (params.entity_id) query.append("entity_id", params.entity_id);
  query.append("window_hours", String(params.window_hours ?? 24));
  query.append("limit", String(params.limit ?? 20));
  query.append("offset", String(params.offset ?? 0));
  const url = `${API_BASE_URL}/api/incident_snapshot?${query.toString()}`;
  const response = await fetch(url, { headers: getAuthHeaders() });
  if (!response.ok) {
    throw new Error(`Failed to fetch incident snapshot: ${response.statusText}`);
  }
  return response.json();
}

// ============================================================
// ENTITY SUMMARY
// ============================================================

export interface EntitySummaryResponse {
  entity_id: string;
  name: string;
  age?: number | null;
  accounts: string[];
  phones: string[];
  ip_addresses: string[];
  social_accounts: string[];
  device_ids: string[];
  transactions: any[];
  communications: any[];
  network: any[];
  anomalies: any[];
}

export async function getEntitySummary(
  entityId: string,
  recentLimit = 5
): Promise<EntitySummaryResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/entity/${entityId}/summary?recent_limit=${recentLimit}`,
    { headers: getAuthHeaders() }
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch entity summary: ${response.statusText}`);
  }
  return response.json();
}

// ============================================================
// NETWORK / IPDR
// ============================================================

export interface NetworkItem {
  ipdr_id: string;
  record_id: string;
  person_id: string;
  entity_id?: string | null;
  entity_ids: string[];
  entity_name?: string | null;
  ip_address: string;
  source_ip: string;
  device_id: string;
  timestamp: string;
  session_duration_seconds: number;
  duration_seconds: number;
  duration_formatted: string;
  scenario_tag: string;
  priority: string;
  status: string;
  is_shared_ip: boolean;
  is_shared_device: boolean;
  shared_ip_entities: string[];
  shared_device_entities: string[];
  shared_ip_count: number;
  shared_device_count: number;
}

export interface NetworkResponse {
  total: number;
  page: number;
  page_size: number;
  summary: {
    total_records: number;
    total_duration_seconds: number;
    avg_duration_seconds: number;
    unique_entities: number;
    unique_ips: number;
    unique_devices: number;
    shared_ip_count: number;
    shared_device_count: number;
    high_priority_count: number;
  };
  records: NetworkItem[];
}

export async function getNetwork(params: {
  ipdr_id?: string;
  entity_id?: string;
  ip_address?: string;
  device_id?: string;
  min_duration?: number;
  max_duration?: number;
  start_time?: string;
  end_time?: string;
  scenario_tag?: string;
  sort?: string;
  page?: number;
  page_size?: number;
} = {}): Promise<NetworkResponse> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.append(key, String(value));
    }
  });
  const url = `${API_BASE_URL}/api/network/?${query.toString()}`;
  const response = await fetch(url, { headers: getAuthHeaders() });
  if (!response.ok) {
    throw new Error(`Failed to fetch network records: ${response.statusText}`);
  }
  return response.json();
}

export async function getNetworkById(ipdrId: string): Promise<NetworkItem> {
  const response = await fetch(`${API_BASE_URL}/api/network/${ipdrId}`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`IPDR record not found: ${ipdrId}`);
    }
    throw new Error(`Failed to fetch IPDR record: ${response.statusText}`);
  }
  return response.json();
}

// ============================================================
// ANOMALIES
// ============================================================

export interface AnomalyFinding {
  finding_id?: string;
  id?: string;
  anomaly_type?: string;
  severity: string;
  score?: number;
  correlation_score?: number;
  entity_ids?: string[];
  explanation?: string;
  domains_involved?: string[];
  evidence_ids?: string[];
  timestamp_range?: { start: string; end: string };
  details?: Record<string, any>;
  [key: string]: any;
}

export interface AnomaliesApiResponse {
  total: number;
  summary: {
    financial: number;
    telecom: number;
    network: number;
    cross_domain: number;
  };
  anomalies: AnomalyFinding[];
}

export async function getAnomalies(params: {
  anomaly_type?: string;
  entity_id?: string;
  severity?: string;
  min_score?: number;
  source?: string;
  start_time?: string;
  end_time?: string;
  sort?: string;
} = {}): Promise<AnomaliesApiResponse> {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.append(key, String(value));
    }
  });
  const url = `${API_BASE_URL}/api/anomalies/?${query.toString()}`;
  const response = await fetch(url, { headers: getAuthHeaders() });
  if (!response.ok) {
    throw new Error(`Failed to fetch anomalies: ${response.statusText}`);
  }
  return response.json();
}

