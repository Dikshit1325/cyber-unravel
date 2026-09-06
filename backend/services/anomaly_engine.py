"""
anomaly_engine.py
=================
Deterministic, rule-based anomaly detection engine.

Operates on pre-loaded investigation data (see cache_manager.py).

Four detection modules:
  1. Financial   — transactions.csv
  2. Telecom     — cdr.csv
  3. Network     — ipdr.csv
  4. Cross-Domain — multi-dataset temporal correlation

Every finding:
  - Has a unique finding_id
  - Carries a 0-100 anomaly score (not a probability of guilt or crime)
  - Is labelled LOW / MEDIUM / HIGH / CRITICAL based on score
  - References only real, existing evidence IDs
  - Contains a plain-language explanation

Ground-truth / scenario tags are NEVER read or imported here.
No entity IDs are hardcoded.
"""
from __future__ import annotations

import hashlib
import itertools
from datetime import timedelta
from typing import Any

import pandas as pd

# ============================================================
# SEVERITY MAPPING
# ============================================================

def _severity(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def _finding_id(prefix: str, key: str) -> str:
    """Stable, collision-resistant finding identifier."""
    digest = hashlib.sha1(key.encode()).hexdigest()[:8].upper()
    return f"{prefix}-{digest}"


# ============================================================
# 1. FINANCIAL ANOMALY DETECTOR
# ============================================================

class FinancialAnomalyDetector:
    """
    Detects suspicious patterns in bank transaction data.

    Thresholds are keyword-configurable so tests can inject
    deterministic values without hardcoding business logic.
    """

    DEFAULT_CONFIG: dict[str, Any] = {
        # Z-score threshold for high-value transfers
        "high_value_z_score": 2.0,
        # Rapid transfer: N transactions within window (minutes)
        "rapid_transfer_count": 3,
        "rapid_transfer_window_minutes": 60,
        # Structuring: N transactions within window, amounts within ratio of each other
        "structuring_count": 3,
        "structuring_window_minutes": 1440,  # 24 h
        "structuring_amount_variance_ratio": 0.30,
        # Multi-hop chain window (minutes)
        "multihop_window_minutes": 120,
        # Minimum chain length for multi-hop finding
        "multihop_min_length": 3,
    }

    def __init__(self, transactions: pd.DataFrame, entity_mapping: pd.DataFrame,
                 config: dict[str, Any] | None = None):
        cfg = dict(self.DEFAULT_CONFIG)
        if config:
            cfg.update(config)
        self._cfg = cfg

        # Parse timestamps once
        tx = transactions.copy()
        if not tx.empty and "timestamp" in tx.columns:
            tx["timestamp"] = pd.to_datetime(tx["timestamp"], errors="coerce")
            tx = tx.dropna(subset=["timestamp"])
        self._tx = tx

        # Build account -> person_id lookup from entity_mapping
        self._acct_to_person: dict[str, str] = {}
        for _, row in entity_mapping.iterrows():
            pid = str(row["person_id"]).strip()
            acct = str(row["bank_account"]).strip()
            self._acct_to_person[acct] = pid

    # ----------------------------------------------------------
    # HIGH_VALUE_TRANSFER
    # ----------------------------------------------------------

    def detect_high_value_transfers(self) -> list[dict]:
        findings = []
        tx = self._tx
        if tx.empty:
            return findings

        mean = tx["amount"].mean()
        std = tx["amount"].std()
        if std == 0:
            return findings

        threshold_z = self._cfg["high_value_z_score"]
        threshold_amount = mean + threshold_z * std

        suspicious = tx[tx["amount"] > threshold_amount]

        for _, row in suspicious.iterrows():
            sender = str(row["sender_account"]).strip()
            receiver = str(row["receiver_account"]).strip()
            amount = float(row["amount"])
            z = (amount - mean) / std

            score = min(100, 40 + round(z * 10))
            entity_ids = list({
                self._acct_to_person.get(sender, sender),
                self._acct_to_person.get(receiver, receiver),
            })

            key = f"HVT:{row['transaction_id']}"
            findings.append({
                "finding_id": _finding_id("FIN", key),
                "anomaly_type": "HIGH_VALUE_TRANSFER",
                "entity_ids": entity_ids,
                "timestamp_range": {
                    "start": row["timestamp"].isoformat(),
                    "end": row["timestamp"].isoformat(),
                },
                "score": score,
                "severity": _severity(score),
                "explanation": (
                    f"Transaction {row['transaction_id']} for {amount:,.0f} is {z:.1f} "
                    f"standard deviations above the dataset mean ({mean:,.0f}). "
                    f"This is a potential investigative signal warranting review."
                ),
                "supporting_transaction_ids": [str(row["transaction_id"])],
            })

        return findings

    # ----------------------------------------------------------
    # RAPID_TRANSFERS
    # ----------------------------------------------------------

    def detect_rapid_transfers(self) -> list[dict]:
        findings = []
        tx = self._tx
        if tx.empty:
            return findings

        window = timedelta(minutes=self._cfg["rapid_transfer_window_minutes"])
        min_count = self._cfg["rapid_transfer_count"]

        all_accounts = sorted(set(tx["sender_account"].unique()) | set(tx["receiver_account"].unique()))

        for acct in all_accounts:
            acct_tx = tx[
                (tx["sender_account"] == acct) | (tx["receiver_account"] == acct)
            ].sort_values("timestamp")

            if len(acct_tx) < min_count:
                continue

            records = acct_tx.to_dict("records")
            current_group = [records[0]]
            groups = []
            for r in records[1:]:
                if r["timestamp"] - current_group[-1]["timestamp"] <= window:
                    current_group.append(r)
                else:
                    groups.append(current_group)
                    current_group = [r]
            if current_group:
                groups.append(current_group)

            for g in groups:
                if len(g) >= min_count:
                    group_ids = sorted(list(set(str(x["transaction_id"]) for x in g)))
                    count = len(group_ids)
                    score = min(100, 30 + count * 8)
                    entity_id = self._acct_to_person.get(acct, acct)
                    t_start = min(x["timestamp"] for x in g)
                    t_end = max(x["timestamp"] for x in g)
                    key = f"RT:{acct}:{','.join(group_ids)}"

                    findings.append({
                        "finding_id": _finding_id("FIN", key),
                        "anomaly_type": "RAPID_TRANSFERS",
                        "entity_ids": [entity_id],
                        "timestamp_range": {
                            "start": t_start.isoformat(),
                            "end": t_end.isoformat(),
                        },
                        "score": score,
                        "severity": _severity(score),
                        "explanation": (
                            f"Account {acct} was involved in {count} transactions "
                            f"within {self._cfg['rapid_transfer_window_minutes']} minutes "
                            f"(between {t_start} and {t_end}). "
                            f"This pattern may indicate rapid funds movement."
                        ),
                        "supporting_transaction_ids": group_ids,
                    })

        return findings

    # ----------------------------------------------------------
    # POTENTIAL_STRUCTURING
    # ----------------------------------------------------------

    def detect_potential_structuring(self) -> list[dict]:
        """
        Detects repeated same-direction transactions with similar amounts
        within a configurable time window.

        This flag is a potential investigative signal, not a determination
        of illegal activity.
        """
        findings = []
        tx = self._tx
        if tx.empty:
            return findings

        window = timedelta(minutes=self._cfg["structuring_window_minutes"])
        min_count = self._cfg["structuring_count"]
        var_ratio = self._cfg["structuring_amount_variance_ratio"]

        for sender in sorted(tx["sender_account"].unique()):
            sent = tx[tx["sender_account"] == sender].sort_values("timestamp")
            if len(sent) < min_count:
                continue

            records = sent.to_dict("records")
            used_indices = set()

            for i in range(len(records)):
                if i in used_indices:
                    continue
                ref_amount = records[i]["amount"]
                group = [records[i]]
                group_indices = [i]

                for j in range(i + 1, len(records)):
                    if records[j]["timestamp"] - records[i]["timestamp"] > window:
                        break
                    diff_ratio = abs(records[j]["amount"] - ref_amount) / ref_amount
                    if diff_ratio <= var_ratio:
                        group.append(records[j])
                        group_indices.append(j)

                if len(group) >= min_count:
                    used_indices.update(group_indices)
                    group_ids = sorted(list(set(str(x["transaction_id"]) for x in group)))
                    score = min(100, 45 + len(group_ids) * 7)
                    entity_id = self._acct_to_person.get(sender, sender)
                    t_start = min(x["timestamp"] for x in group)
                    t_end = max(x["timestamp"] for x in group)
                    avg_amount = sum(x["amount"] for x in group) / len(group)
                    key = f"STR:{sender}:{','.join(group_ids)}"

                    findings.append({
                        "finding_id": _finding_id("FIN", key),
                        "anomaly_type": "POTENTIAL_STRUCTURING",
                        "entity_ids": [entity_id],
                        "timestamp_range": {
                            "start": t_start.isoformat(),
                            "end": t_end.isoformat(),
                        },
                        "score": score,
                        "severity": _severity(score),
                        "explanation": (
                            f"Account {sender} sent {len(group_ids)} transactions with "
                            f"similar amounts (avg {avg_amount:,.0f}, within {int(var_ratio*100)}% variance) "
                            f"over {self._cfg['structuring_window_minutes']//60} hours. "
                            f"This pattern is a potential investigative signal and does not "
                            f"confirm any wrongdoing."
                        ),
                        "supporting_transaction_ids": group_ids,
                    })

        return findings

    # ----------------------------------------------------------
    # MULTI_HOP_TRANSFER
    # ----------------------------------------------------------

    def detect_multi_hop_transfers(self) -> list[dict]:
        """
        Detects fund chains: A → B → C (or longer) within a time window.
        Suppresses sub-chains to report maximal meaningful fund chains.
        """
        findings = []
        tx = self._tx
        if tx.empty:
            return findings

        window = timedelta(minutes=self._cfg["multihop_window_minutes"])
        min_len = self._cfg["multihop_min_length"]

        from collections import defaultdict
        sender_map: dict[str, list] = defaultdict(list)
        for _, row in tx.iterrows():
            sender_map[str(row["sender_account"])].append(
                (row["timestamp"], str(row["receiver_account"]), str(row["transaction_id"]))
            )

        raw_chains = []

        def _find_chains(current_acct, chain_accts, chain_txids, chain_start):
            if len(chain_accts) >= min_len:
                raw_chains.append((list(chain_accts), list(chain_txids), chain_start))
            if len(chain_accts) >= 6:  # prevent runaway recursion
                return

            for ts, next_acct, tx_id in sender_map.get(current_acct, []):
                if ts < chain_start or ts - chain_start > window:
                    continue
                if next_acct in chain_accts:
                    continue  # no cycles
                _find_chains(next_acct, chain_accts + [next_acct], chain_txids + [tx_id], chain_start)

        for sender in sorted(sender_map.keys()):
            for ts, receiver, tx_id in sender_map[sender]:
                _find_chains(receiver, [sender, receiver], [tx_id], ts)

        # Filter for maximal chains (suppress sub-chains whose transaction IDs are proper subsets)
        maximal_chains = []
        for i, c1 in enumerate(raw_chains):
            set1 = set(c1[1])
            is_sub = False
            for j, c2 in enumerate(raw_chains):
                if i == j:
                    continue
                set2 = set(c2[1])
                if set1.issubset(set2) and len(set1) < len(set2):
                    is_sub = True
                    break
            if not is_sub:
                maximal_chains.append(c1)

        # Group by unique maximal account sequence to merge transaction IDs deterministically
        chain_groups = defaultdict(lambda: {"accts": [], "txids": set(), "start": None})
        for accts, txids, start in maximal_chains:
            key = "->".join(accts)
            entry = chain_groups[key]
            entry["accts"] = accts
            entry["txids"].update(txids)
            if entry["start"] is None or start < entry["start"]:
                entry["start"] = start

        for key in sorted(chain_groups.keys()):
            entry = chain_groups[key]
            chain_accts = entry["accts"]
            txids = sorted(list(entry["txids"]))
            entity_ids = sorted(list({
                self._acct_to_person.get(a, a) for a in chain_accts
            }))
            score = min(100, 50 + len(chain_accts) * 8 + len(txids) * 2)
            t_start = entry["start"]
            t_end = tx[tx["transaction_id"].isin(txids)]["timestamp"].max()

            findings.append({
                "finding_id": _finding_id("FIN", "MH:" + key + ":" + ",".join(txids)),
                "anomaly_type": "MULTI_HOP_TRANSFER",
                "entity_ids": entity_ids,
                "timestamp_range": {
                    "start": t_start.isoformat(),
                    "end": t_end.isoformat(),
                },
                "score": score,
                "severity": _severity(score),
                "explanation": (
                    f"Fund chain detected: {' → '.join(chain_accts)} "
                    f"({len(chain_accts)} hops) with {len(txids)} supporting transactions within "
                    f"{self._cfg['multihop_window_minutes']} minutes. "
                    f"Multi-hop transfers may warrant further review."
                ),
                "supporting_transaction_ids": txids,
            })

        return findings

    # ----------------------------------------------------------
    # COMBINED
    # ----------------------------------------------------------

    def detect_all(self) -> list[dict]:
        results = []
        results.extend(self.detect_high_value_transfers())
        results.extend(self.detect_rapid_transfers())
        results.extend(self.detect_potential_structuring())
        results.extend(self.detect_multi_hop_transfers())
        return results


# ============================================================
# 2. TELECOM ANOMALY DETECTOR
# ============================================================

class TelecomAnomalyDetector:
    """
    Detects suspicious call patterns in CDR data.
    Baseline thresholds are computed from the dataset.
    """

    DEFAULT_CONFIG: dict[str, Any] = {
        # Calls per day Z-score to flag as spike
        "frequency_spike_z_score": 2.0,
        # Hour range considered abnormal (23:00 – 05:00)
        "abnormal_hour_start": 23,
        "abnormal_hour_end": 5,
        # Burst: N calls within window (minutes) from same caller
        "burst_count": 4,
        "burst_window_minutes": 30,
        # Unusual contact: caller talks to >= N distinct people in 1 day
        "unusual_contact_threshold": 5,
    }

    def __init__(self, cdr: pd.DataFrame, config: dict[str, Any] | None = None):
        cfg = dict(self.DEFAULT_CONFIG)
        if config:
            cfg.update(config)
        self._cfg = cfg

        df = cdr.copy()
        if not df.empty and "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.dropna(subset=["timestamp"])
            df["date"] = df["timestamp"].dt.date
            df["hour"] = df["timestamp"].dt.hour
        self._cdr = df

    # ----------------------------------------------------------
    # CALL_FREQUENCY_SPIKE
    # ----------------------------------------------------------

    def detect_call_frequency_spike(self) -> list[dict]:
        findings = []
        cdr = self._cdr
        if cdr.empty:
            return findings

        daily_counts = cdr.groupby(["caller", "date"]).size().reset_index(name="count")
        stats = daily_counts.groupby("caller")["count"].agg(["mean", "std"]).reset_index()
        stats.columns = ["caller", "mean", "std"]
        # Drop entities where std is 0 or NaN (only 1 day of data)
        stats = stats[stats["std"].notna() & (stats["std"] > 0)]

        threshold = self._cfg["frequency_spike_z_score"]

        for _, person_stats in stats.iterrows():
            caller = person_stats["caller"]
            person_daily = daily_counts[daily_counts["caller"] == caller]
            spikes = person_daily[
                (person_daily["count"] - person_stats["mean"]) / person_stats["std"] > threshold
            ]

            for _, spike_row in spikes.iterrows():
                day_str = str(spike_row["date"])
                day_calls = cdr[(cdr["caller"] == caller) & (cdr["date"] == spike_row["date"])]
                z = (spike_row["count"] - person_stats["mean"]) / person_stats["std"]
                score = min(100, 40 + round(z * 8))

                findings.append({
                    "finding_id": _finding_id("TEL", f"CFS:{caller}:{day_str}"),
                    "anomaly_type": "CALL_FREQUENCY_SPIKE",
                    "entity_ids": [caller],
                    "timestamp_range": {
                        "start": day_str,
                        "end": day_str,
                    },
                    "score": score,
                    "severity": _severity(score),
                    "explanation": (
                        f"{caller} made {int(spike_row['count'])} calls on {day_str}, "
                        f"which is {z:.1f} standard deviations above their daily average "
                        f"({person_stats['mean']:.1f}). This is an above-baseline activity spike."
                    ),
                    "supporting_cdr_ids": list(day_calls["cdr_id"].astype(str)),
                })

        return findings

    # ----------------------------------------------------------
    # ABNORMAL_HOUR_CALL
    # ----------------------------------------------------------

    def detect_abnormal_hour_calls(self) -> list[dict]:
        findings = []
        cdr = self._cdr
        if cdr.empty:
            return findings

        h_start = self._cfg["abnormal_hour_start"]
        h_end = self._cfg["abnormal_hour_end"]

        # Hours >= h_start (e.g. 23) OR < h_end (e.g. 5) are abnormal
        if h_start > h_end:
            abnormal = cdr[(cdr["hour"] >= h_start) | (cdr["hour"] < h_end)]
        else:
            abnormal = cdr[(cdr["hour"] >= h_start) & (cdr["hour"] < h_end)]

        if abnormal.empty:
            return findings

        # Group by caller, summarise
        for caller, group in abnormal.groupby("caller"):
            count = len(group)
            score = min(100, 20 + count * 5)
            t_start = group["timestamp"].min()
            t_end = group["timestamp"].max()

            findings.append({
                "finding_id": _finding_id("TEL", f"AHC:{caller}"),
                "anomaly_type": "ABNORMAL_HOUR_CALL",
                "entity_ids": [str(caller)],
                "timestamp_range": {
                    "start": t_start.isoformat(),
                    "end": t_end.isoformat(),
                },
                "score": score,
                "severity": _severity(score),
                "explanation": (
                    f"{caller} made {count} call(s) during unusual hours "
                    f"(between {h_start}:00 and {h_end:02d}:00). "
                    f"Late-night or early-morning communications may warrant closer review."
                ),
                "supporting_cdr_ids": list(group["cdr_id"].astype(str)),
            })

        return findings

    # ----------------------------------------------------------
    # COMMUNICATION_BURST
    # ----------------------------------------------------------

    def detect_communication_burst(self) -> list[dict]:
        findings = []
        cdr = self._cdr
        if cdr.empty:
            return findings

        window = timedelta(minutes=self._cfg["burst_window_minutes"])
        min_count = self._cfg["burst_count"]

        seen_keys: set[str] = set()

        for caller, group in cdr.groupby("caller"):
            group = group.sort_values("timestamp")
            times = list(group["timestamp"])
            ids = list(group["cdr_id"])

            for i in range(len(times)):
                group_ids = [ids[i]]
                for j in range(i + 1, len(times)):
                    if times[j] - times[i] <= window:
                        group_ids.append(ids[j])
                    else:
                        break

                if len(group_ids) >= min_count:
                    key = str(caller) + ":" + ",".join(sorted(group_ids))
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)

                    burst_rows = group[group["cdr_id"].isin(group_ids)]
                    count = len(group_ids)
                    score = min(100, 35 + count * 5)
                    t_start = burst_rows["timestamp"].min()
                    t_end = burst_rows["timestamp"].max()

                    findings.append({
                        "finding_id": _finding_id("TEL", f"CB:{key}"),
                        "anomaly_type": "COMMUNICATION_BURST",
                        "entity_ids": [str(caller)],
                        "timestamp_range": {
                            "start": t_start.isoformat(),
                            "end": t_end.isoformat(),
                        },
                        "score": score,
                        "severity": _severity(score),
                        "explanation": (
                            f"{caller} made {count} calls within "
                            f"{self._cfg['burst_window_minutes']} minutes "
                            f"(between {t_start} and {t_end}). "
                            f"Communication bursts may indicate coordinated activity."
                        ),
                        "supporting_cdr_ids": group_ids,
                    })

        return findings

    # ----------------------------------------------------------
    # UNUSUAL_CONTACT_PATTERN
    # ----------------------------------------------------------

    def detect_unusual_contact_pattern(self) -> list[dict]:
        findings = []
        cdr = self._cdr
        if cdr.empty:
            return findings

        threshold = self._cfg["unusual_contact_threshold"]
        daily_contacts = (
            cdr.groupby(["caller", "date"])["receiver"]
            .nunique()
            .reset_index(name="distinct_receivers")
        )

        flagged = daily_contacts[daily_contacts["distinct_receivers"] >= threshold]

        for _, row in flagged.iterrows():
            caller = row["caller"]
            day = row["date"]
            count = int(row["distinct_receivers"])
            day_calls = cdr[(cdr["caller"] == caller) & (cdr["date"] == day)]
            score = min(100, 30 + count * 5)

            findings.append({
                "finding_id": _finding_id("TEL", f"UCP:{caller}:{day}"),
                "anomaly_type": "UNUSUAL_CONTACT_PATTERN",
                "entity_ids": [str(caller)],
                "timestamp_range": {
                    "start": str(day),
                    "end": str(day),
                },
                "score": score,
                "severity": _severity(score),
                "explanation": (
                    f"{caller} contacted {count} distinct entities on {day}, "
                    f"which exceeds the threshold of {threshold}. "
                    f"Wide fan-out communication patterns may be an investigative signal."
                ),
                "supporting_cdr_ids": list(day_calls["cdr_id"].astype(str)),
            })

        return findings

    # ----------------------------------------------------------
    # COMBINED
    # ----------------------------------------------------------

    def detect_all(self) -> list[dict]:
        results = []
        results.extend(self.detect_call_frequency_spike())
        results.extend(self.detect_abnormal_hour_calls())
        results.extend(self.detect_communication_burst())
        results.extend(self.detect_unusual_contact_pattern())
        return results


# ============================================================
# 3. NETWORK ANOMALY DETECTOR
# ============================================================

class NetworkAnomalyDetector:
    """
    Detects shared infrastructure across entities using IPDR data.

    Shared infrastructure is NOT proof of wrongdoing.
    All findings use neutral language.
    """

    DEFAULT_CONFIG: dict[str, Any] = {
        # Minimum distinct persons sharing an IP before flagging
        "shared_ip_min_persons": 2,
        # Minimum distinct persons sharing a device before flagging
        "shared_device_min_persons": 2,
    }

    def __init__(self, ipdr: pd.DataFrame, entity_mapping: pd.DataFrame,
                 config: dict[str, Any] | None = None):
        cfg = dict(self.DEFAULT_CONFIG)
        if config:
            cfg.update(config)
        self._cfg = cfg

        df = ipdr.copy()
        if not df.empty and "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.dropna(subset=["timestamp"])
        self._ipdr = df
        self._entity_mapping = entity_mapping

    # ----------------------------------------------------------
    # SHARED_IP
    # ----------------------------------------------------------

    def detect_shared_ip(self) -> list[dict]:
        findings = []
        ipdr = self._ipdr
        if ipdr.empty:
            return findings

        min_persons = self._cfg["shared_ip_min_persons"]

        ip_groups = ipdr.groupby("ip_address")

        for ip_addr, group in ip_groups:
            distinct_persons = group["person_id"].unique()
            if len(distinct_persons) < min_persons:
                continue

            score = min(100, 40 + len(distinct_persons) * 10)
            t_start = group["timestamp"].min()
            t_end = group["timestamp"].max()

            findings.append({
                "finding_id": _finding_id("NET", f"SIP:{ip_addr}"),
                "anomaly_type": "SHARED_IP",
                "entity_ids": [str(p) for p in distinct_persons],
                "infrastructure_identifier": str(ip_addr),
                "timestamp_range": {
                    "start": t_start.isoformat(),
                    "end": t_end.isoformat(),
                },
                "score": score,
                "severity": _severity(score),
                "explanation": (
                    f"Potential shared infrastructure: {len(distinct_persons)} entities "
                    f"({', '.join(str(p) for p in distinct_persons)}) were observed "
                    f"using IP address {ip_addr}. "
                    f"Shared IPs may indicate co-location or a shared network, "
                    f"and are not themselves evidence of wrongdoing."
                ),
                "supporting_ipdr_ids": list(group["ipdr_id"].astype(str)),
            })

        return findings

    # ----------------------------------------------------------
    # SHARED_DEVICE
    # ----------------------------------------------------------

    def detect_shared_device(self) -> list[dict]:
        findings = []
        ipdr = self._ipdr
        if ipdr.empty or "device_id" not in ipdr.columns:
            return findings

        min_persons = self._cfg["shared_device_min_persons"]

        for device_id, group in ipdr.groupby("device_id"):
            distinct_persons = group["person_id"].unique()
            if len(distinct_persons) < min_persons:
                continue

            score = min(100, 50 + len(distinct_persons) * 15)
            t_start = group["timestamp"].min()
            t_end = group["timestamp"].max()

            findings.append({
                "finding_id": _finding_id("NET", f"SDEV:{device_id}"),
                "anomaly_type": "SHARED_DEVICE",
                "entity_ids": [str(p) for p in distinct_persons],
                "infrastructure_identifier": str(device_id),
                "timestamp_range": {
                    "start": t_start.isoformat(),
                    "end": t_end.isoformat(),
                },
                "score": score,
                "severity": _severity(score),
                "explanation": (
                    f"Potential shared infrastructure: {len(distinct_persons)} entities "
                    f"({', '.join(str(p) for p in distinct_persons)}) were associated "
                    f"with device {device_id}. "
                    f"A shared device may indicate physical co-location or device sharing."
                ),
                "supporting_ipdr_ids": list(group["ipdr_id"].astype(str)),
            })

        return findings

    # ----------------------------------------------------------
    # COMBINED
    # ----------------------------------------------------------

    def detect_all(self) -> list[dict]:
        results = []
        results.extend(self.detect_shared_ip())
        results.extend(self.detect_shared_device())
        return results


# ============================================================
# 4. CROSS-DOMAIN CORRELATOR
# ============================================================

class CrossDomainCorrelator:
    """
    Correlates events across CDR, Bank, IPDR, and Social
    using a configurable temporal proximity window.

    Finds entity-centric multi-domain event bursts.
    Does NOT hardcode any scenario or entity ID.
    """

    DEFAULT_CONFIG: dict[str, Any] = {
        # Temporal window in minutes
        "correlation_window_minutes": 30,
        # Minimum number of distinct domains to trigger a finding
        "min_domains": 2,
        # Minimum total events in the window to trigger a finding
        "min_total_events": 3,
    }

    def __init__(self, cdr: pd.DataFrame, transactions: pd.DataFrame,
                 ipdr: pd.DataFrame, social: pd.DataFrame,
                 entity_mapping: pd.DataFrame,
                 config: dict[str, Any] | None = None):
        cfg = dict(self.DEFAULT_CONFIG)
        if config:
            cfg.update(config)
        self._cfg = cfg

        # Build account -> person_id and reverse maps
        self._acct_to_person: dict[str, str] = {}
        for _, row in entity_mapping.iterrows():
            pid = str(row["person_id"]).strip()
            acct = str(row["bank_account"]).strip()
            self._acct_to_person[acct] = pid

        # Unify all events into a per-person timeline
        # Each event: {"person_id", "timestamp", "domain", "event_id"}
        self._all_events: list[dict] = []
        self._ingest_cdr(cdr)
        self._ingest_transactions(transactions)
        self._ingest_ipdr(ipdr)
        self._ingest_social(social)

        df = pd.DataFrame(self._all_events)
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.dropna(subset=["timestamp"])
        self._events_df = df

    def _ingest_cdr(self, cdr: pd.DataFrame) -> None:
        for _, row in cdr.iterrows():
            ts = row["timestamp"]
            for pid in [str(row["caller"]), str(row["receiver"])]:
                self._all_events.append({
                    "person_id": pid,
                    "timestamp": ts,
                    "domain": "TELECOM",
                    "event_id": str(row["cdr_id"]),
                })

    def _ingest_transactions(self, transactions: pd.DataFrame) -> None:
        for _, row in transactions.iterrows():
            sender_pid = self._acct_to_person.get(str(row["sender_account"]).strip())
            receiver_pid = self._acct_to_person.get(str(row["receiver_account"]).strip())
            for pid in filter(None, [sender_pid, receiver_pid]):
                self._all_events.append({
                    "person_id": pid,
                    "timestamp": row["timestamp"],
                    "domain": "FINANCIAL",
                    "event_id": str(row["transaction_id"]),
                })

    def _ingest_ipdr(self, ipdr: pd.DataFrame) -> None:
        for _, row in ipdr.iterrows():
            self._all_events.append({
                "person_id": str(row["person_id"]),
                "timestamp": row["timestamp"],
                "domain": "NETWORK",
                "event_id": str(row["ipdr_id"]),
            })

    def _ingest_social(self, social: pd.DataFrame) -> None:
        if social is None or social.empty:
            return
        for _, row in social.iterrows():
            self._all_events.append({
                "person_id": str(row["person_id"]),
                "timestamp": row["timestamp"],
                "domain": "SOCIAL",
                "event_id": str(row["social_event_id"]),
            })

    # ----------------------------------------------------------
    # DETECT CROSS-DOMAIN BURSTS
    # ----------------------------------------------------------

    def detect_cross_domain_bursts(self) -> list[dict]:
        findings = []
        df = self._events_df
        if df.empty:
            return findings

        window = timedelta(minutes=self._cfg["correlation_window_minutes"])
        min_domains = self._cfg["min_domains"]
        min_events = self._cfg["min_total_events"]

        for person_id in sorted(df["person_id"].unique()):
            person_events = df[df["person_id"] == person_id].sort_values("timestamp")
            times = list(person_events["timestamp"])
            event_ids = list(person_events["event_id"])
            domains = list(person_events["domain"])

            candidates = []
            for i in range(len(times)):
                c_ids = [event_ids[i]]
                c_doms = {domains[i]}
                for j in range(i + 1, len(times)):
                    if times[j] - times[i] <= window:
                        c_ids.append(event_ids[j])
                        c_doms.add(domains[j])
                    else:
                        break

                if len(c_ids) >= min_events and len(c_doms) >= min_domains:
                    candidates.append((set(c_ids), c_doms, times[i]))

            # Filter for maximal event sets (suppress sub-windows whose event IDs are proper subsets)
            maximal = []
            for i, c1 in enumerate(candidates):
                is_sub = False
                for j, c2 in enumerate(candidates):
                    if i == j:
                        continue
                    if c1[0].issubset(c2[0]) and len(c1[0]) < len(c2[0]):
                        is_sub = True
                        break
                if not is_sub:
                    maximal.append(c1)

            # Deduplicate by event set
            seen_sets = set()
            for ev_set, dom_set, start_t in maximal:
                key = tuple(sorted(ev_set))
                if key in seen_sets:
                    continue
                seen_sets.add(key)

                ev_ids = sorted(list(ev_set))
                dom_list = sorted(list(dom_set))
                window_rows = person_events[person_events["event_id"].isin(ev_ids)]
                t_start = window_rows["timestamp"].min()
                t_end = window_rows["timestamp"].max()

                domain_event_ids: dict[str, list[str]] = {}
                for _, ev in window_rows.iterrows():
                    domain_event_ids.setdefault(ev["domain"], []).append(ev["event_id"])
                for d in domain_event_ids:
                    domain_event_ids[d] = sorted(list(set(domain_event_ids[d])))

                score = min(100, 40 + len(dom_list) * 12 + len(ev_ids) * 2)
                f_key = f"XD:{person_id}:{','.join(ev_ids)}"

                findings.append({
                    "finding_id": _finding_id("XD", f_key),
                    "anomaly_type": "CROSS_DOMAIN_ACTIVITY_BURST",
                    "entity_ids": [str(person_id)],
                    "domains_involved": dom_list,
                    "start_time": t_start.isoformat(),
                    "end_time": t_end.isoformat(),
                    "event_ids": ev_ids,
                    "correlation_score": score,
                    "severity": _severity(score),
                    "explanation": (
                        f"Entity {person_id} had {len(ev_ids)} events across "
                        f"{len(dom_list)} domain(s) ({', '.join(dom_list)}) "
                        f"within a {self._cfg['correlation_window_minutes']}-minute correlation window "
                        f"({t_start} to {t_end}). "
                        f"Multi-domain temporal co-occurrence is a potential investigative signal."
                    ),
                    "supporting_event_ids_by_domain": domain_event_ids,
                })

        return findings

    def detect_all(self) -> list[dict]:
        return self.detect_cross_domain_bursts()


# ============================================================
# TOP-LEVEL ENTRY POINT
# ============================================================

class AnomalyEngine:
    """
    Unified anomaly detection engine.

    Call detect_all() to run all four detection modules.

    Accepts the investigation data dict produced by load_all_data()
    and the entity_mapping DataFrame.

    Does NOT reload CSVs; caller is responsible for providing data
    (typically via CacheManager).
    """

    def __init__(self, data: dict[str, pd.DataFrame],
                 config: dict[str, Any] | None = None):
        self._config = config or {}
        transactions = data.get("transactions", pd.DataFrame())
        cdr = data.get("cdr", pd.DataFrame())
        ipdr = data.get("ipdr", pd.DataFrame())
        social = data.get("social", pd.DataFrame())
        entity_mapping = data.get("entity_mapping", pd.DataFrame())

        self._financial = FinancialAnomalyDetector(transactions, entity_mapping, config)
        self._telecom = TelecomAnomalyDetector(cdr, config)
        self._network = NetworkAnomalyDetector(ipdr, entity_mapping, config)
        self._cross_domain = CrossDomainCorrelator(
            cdr, transactions, ipdr, social, entity_mapping, config
        )

    def detect_financial(self) -> list[dict]:
        return self._financial.detect_all()

    def detect_telecom(self) -> list[dict]:
        return self._telecom.detect_all()

    def detect_network(self) -> list[dict]:
        return self._network.detect_all()

    def detect_cross_domain(self) -> list[dict]:
        return self._cross_domain.detect_all()

    def detect_all(self) -> dict[str, list[dict]]:
        """Run all four detection modules and return categorised findings."""
        financial = self.detect_financial()
        telecom = self.detect_telecom()
        network = self.detect_network()
        cross_domain = self.detect_cross_domain()

        all_findings = financial + telecom + network + cross_domain
        all_findings.sort(key=lambda f: f.get("score", f.get("correlation_score", 0)), reverse=True)

        return {
            "financial": financial,
            "telecom": telecom,
            "network": network,
            "cross_domain": cross_domain,
            "all": all_findings,
            "summary": {
                "financial_count": len(financial),
                "telecom_count": len(telecom),
                "network_count": len(network),
                "cross_domain_count": len(cross_domain),
                "total": len(all_findings),
            },
        }
