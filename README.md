# Insight Navigator

MASTER PROMPT FOR LOVABLE

Build a polished, production-quality web prototype for a Police Digital Investigation Intelligence Platform based on this problem statement:

“A Single Analytics Platform that Analyzes Telecom CDR/IPDR Data, Bank Statements, and Social Media Activity to Detect Anomalies, Uncover Patterns, and Generate Actionable Insights Across Digital Footprints.”

1. PRODUCT VISION

The product is an investigator-centric intelligence platform that takes fragmented and authorized digital datasets such as:

CDR data

IPDR data

Bank statements

Financial transactions

Social-media activity

IP/device records where authorized

and combines them into a unified investigation environment.

The system should help investigators answer:

Who is connected to whom?

Which entities are potentially related?

Which transactions or communications are anomalous?

What happened around a particular incident?

Which entities are the most important investigative leads?

What hidden relationships exist across different datasets?

What actionable insights can be generated from the combined evidence?

Product motto:

“From Scattered Data to Actionable Intelligence.”

Do NOT make this look like a generic admin dashboard.

It should feel like a serious law-enforcement digital investigation / intelligence command center.

2. IMPORTANT PROTOTYPE CONSTRAINT

This is a hackathon prototype.

Use realistic synthetic/mock investigation data for demonstration.

Do NOT claim that the prototype has unrestricted access to WhatsApp, Instagram, Telegram, bank systems, telecom systems, or private databases.

Social-media and other external data should be represented as:

public/authorized data

imported datasets

synthetic investigation data

The UI should make it clear that this is an analytical and investigative support system.

Do not make definitive claims that a person is a criminal.

Use terminology such as:

“Investigative Lead”

“Potential Relationship”

“Anomaly”

“High Investigation Priority”

“Analytical Finding”

“Requires Review”

rather than “Criminal” or “Guilty.”

3. TECH STACK

Build using:

React

TypeScript

Vite

Tailwind CSS

shadcn/ui

Lucide icons

Recharts for charts

React Flow or another suitable graph visualization library for the investigation graph

Use clean component architecture.

Make the application responsive, but prioritize the desktop/laptop experience, because the hackathon judges will primarily see the desktop dashboard.

The prototype should work entirely with mock data initially.

Structure the code so a real backend/API can easily be connected later.

4. DESIGN DIRECTION

Create a premium dark intelligence-command-center UI.

Visual inspiration:

police cyber command center

digital forensics platform

intelligence analysis software

modern SOC/SIEM dashboards

Palantir-style investigative graph concepts, but do NOT copy any proprietary UI

Design language

Use:

dark navy/charcoal background

subtle blue/cyan accents

restrained red/orange/yellow for alert severity

glass/solid dark cards

thin borders

subtle shadows

professional typography

dense but readable information

minimal decorative elements

Avoid:

flashy gradients everywhere

excessive animations

cartoonish icons

generic SaaS purple dashboards

huge unnecessary cards

excessive rounded corners

stock images

The application should feel like software used by investigators.

5. APPLICATION STRUCTURE

Create the following main navigation:

Sidebar

Command Center

Cases

Investigation Graph

Timeline

Entities

Transactions

Communications

Anomalies & Alerts

Data Sources

Reports

Audit Trail

Settings

At the bottom:

Current investigator

Role

Case status

Logout

6. COMMAND CENTER / MAIN DASHBOARD

Create a highly polished landing dashboard.

Header:

Digital Investigation Command Center

Subtitle:

Cross-domain intelligence across telecom, financial and digital footprints

Top-right:

Search

Notifications

Investigator profile

KPI cards

Display:

Active Cases

24

Entities Analyzed

12,481

Relationships Discovered

38,291

Active Alerts

137

High-Priority Leads

23

Each card should include a small trend indicator.

7. ACTIVE CASE SECTION

Show investigation cases as professional cards/table rows.

Example:

CASE-2026-1024

Online Financial Fraud

Status:
Active

Priority:
HIGH

Entities:
4,281

Alerts:
31

Last Activity:
12 minutes ago

Button:

Open Investigation

Other sample cases:

Coordinated Digital Fraud

Suspicious Transaction Network

SIM/Communication Abuse

Cyber-enabled Financial Crime

8. LIVE ALERT PANEL

Create a right-side or central alert feed.

Examples:

HIGH

Transaction Burst Detected

Account AC-48291

₹4,80,000 transferred across 4 transactions within 9 minutes.

HIGH

Bridge Entity Detected

Entity ENT-1092

Connects two otherwise separate investigation clusters.

MEDIUM

Communication Spike

Phone +91 XXXXX 3210

23 new communication relationships detected within 30 minutes.

MEDIUM

Unusual Account Flow

Account AC-8821

92% of incoming funds transferred onward within the investigation window.

Each alert should have:

View Investigation

button.

9. INVESTIGATION GRAPH

This is the MOST IMPORTANT feature of the prototype.

Create a dedicated full-screen interactive graph.

Use React Flow or another graph visualization library.

Nodes:

Person

Phone

Bank Account

Social Account

IP Address

Device

Transaction

Location/Event

Edges:

CALLED

TRANSFERRED_TO

USES

OWNS

CONNECTED_TO

ASSOCIATED_WITH

LOGGED_FROM

COMMUNICATED_WITH

Example graph:

Person A
↓
Phone A
↓
Phone B
↓
Person B
↓
Bank Account B
↓
Bank Account C
↓
Social Account C

Use different node icons for different entity types.

Graph interaction

The user must be able to:

zoom

pan

click nodes

expand relationships

collapse relationships

highlight connected entities

filter node types

filter relationship types

search an entity

view relationship metadata

focus on a selected entity

When clicking a node, open a right-side detail drawer.

Example:

ENTITY ENT-1092

Type:
Person

Investigation Priority:
HIGH

Connected Entities:
17

Transactions:
12

Communications:
38

Anomalies:
5

Relationships:
7

Then show:

Why this entity is high priority

Connected to 4 anomalous accounts

Communication spike during incident window

Acts as a bridge between two clusters

Appears in 3 suspicious transaction paths

Do not state that the person is guilty.

10. ENTITY PROFILE PAGE

Create a detailed entity profile.

Example:

Entity ENT-1092

Overview

Entity Type:
Person

Investigation Priority:
HIGH

First Observed:
2026-08-12

Last Observed:
2026-08-16

Connected Identifiers

Phone:
+91 XXXXX 3210

Bank Accounts:
2

Social Accounts:
1

IP Addresses:
3

Devices:
2

Activity Summary

Calls:
38

Transactions:
12

Social Events:
16

Anomalies:
5

Relationship Network

Show a mini graph.

Activity Timeline

Show chronological events.

Analytical Findings

Show explainable findings.

11. TIMELINE RECONSTRUCTION

Create a powerful timeline page.

Header:

Incident Timeline Reconstruction

Allow the investigator to select:

Case

Entity

Start date

End date

Incident window

Example:

INCIDENT WINDOW

16 Aug 2026
18:00 – 20:00

Timeline:

18:02
Phone A → Phone B
Call duration: 4m 21s

18:15
Bank A → Bank B
₹1,00,000

18:21
Phone B → Phone C
Call duration: 2m 13s

18:31
IP A
Session detected

18:34
Bank B → Bank C
₹95,000

18:41
Social Account X
Activity detected

Each event should be clickable.

Clicking an event should open its detailed record.

12. ANOMALY DETECTION PAGE

Create a dedicated anomaly analytics page.

Tabs:

All

Telecom

Financial

Social

Network

Cross-Domain

Each anomaly should contain:

Severity

Entity

Type

Detection time

Confidence

Explanation

Related entities

View Investigation

Example:

Financial Anomaly

Transaction Burst

Entity:
AC-48291

Detected:

16 Aug 2026, 18:15

Pattern:

4 transactions

Total:

₹4,80,000

Explanation:

“Transaction volume and frequency significantly deviate from the entity's observed baseline during the selected investigation window.”

13. ANOMALY EXPLANATION

When the investigator clicks:

Explain Anomaly

show a modal:

Why was this flagged?

Signal 1
Transaction frequency is significantly above the historical baseline.

Signal 2
Multiple counterparties were involved within a short time interval.

Signal 3
The activity overlaps with the investigation incident window.

Signal 4
The receiving account is connected to another flagged entity.

Then:

Investigative relevance

“Review the connected transaction chain and associated entities.”

This is extremely important.

Do not make the AI a black box.

14. TRANSACTION INTELLIGENCE

Create a financial analytics page.

Show:

Total transaction volume

Incoming

Outgoing

Number of accounts

Suspicious transaction count

Average transaction amount

Charts:

Transaction Volume Over Time

Line chart.

Money Flow

Sankey-like or graph visualization if feasible.

Example:

Account A
→ ₹1,00,000
→ Account B
→ ₹95,000
→ Account C

Transaction table

Columns:

Timestamp

Sender

Receiver

Amount

Type

Risk/priority

Related case

Status

Filters:

Amount

Date

Account

Priority

Transaction type

15. COMMUNICATION INTELLIGENCE

Create a communication analytics page.

Show:

Total calls

Unique contacts

Communication spikes

Average duration

New relationships

High-priority communication links

Charts:

Communication Volume

Top Connected Numbers

Communication Network

Allow clicking a phone number to open its entity profile.

16. CROSS-DOMAIN CORRELATION

This is one of the most important differentiating features.

Create a page called:

Cross-Domain Intelligence

Show:

Telecom

Phone A

↓

Financial

Bank Account B

↓

Social

Social Account C

↓

Network

IP Address D

The page should explicitly communicate:

“These records are connected through shared or correlated identifiers and activity patterns.”

Show a visual chain.

Example:

Phone
  ↓
Person
  ↓
Bank Account
  ↓
Transaction
  ↓
Other Account
  ↓
Social Account
  ↓
IP


17. HIDDEN RELATIONSHIP DETECTION

Create a feature:

Discover Hidden Relationships

When clicked, show findings such as:

Potential Bridge Entity

Entity ENT-1092 connects:

Cluster A ↔ Cluster B

Strength:
HIGH

Evidence:

4 communication relationships

2 financial relationships

activity overlap during incident window

Button:

Explore Relationship

18. CLUSTER ANALYSIS

Create network clusters.

Example:

Cluster 01

12 entities

Cluster 02

8 entities

Cluster 03

21 entities

Allow:

highlight cluster

isolate cluster

view central entities

compare clusters

Show:

Most Connected Entity

Most Active Entity

Potential Bridge Entities

19. INVESTIGATION PRIORITY SCORE

Create an explainable priority score from 0–100.

Example:

ENT-1092

87 / 100

HIGH PRIORITY

Breakdown:

Communication anomalies
+18

Financial anomalies
+27

Cross-domain connections
+21

Incident-window activity
+14

Network centrality
+7

Total:
87

Make it clear:

“Priority score is an analytical aid for investigation and does not establish guilt.”

20. SMART INVESTIGATION SEARCH

Create a global search bar.

Placeholder:

Search phone, account, IP, entity, transaction...

Search examples:

+91 XXXXX 3210

AC-48291

ENT-1092

192.168.x.x

Search results should categorize matches:

Entities

Accounts

Phones

Transactions

Social Accounts

IP Addresses

Clicking a result opens the relevant investigation view.

21. CASE MANAGEMENT

Create:

New Case

Fields:

Case ID

Case name

Case type

Description

Priority

Investigator

Incident date

Status

Case types:

Financial Fraud

Cybercrime

Organized Digital Fraud

Suspicious Financial Network

Other

22. DATA SOURCES PAGE

Create a data-source management interface.

Cards:

CDR

Status:
Imported

Records:
24,812

Last Updated:
16 Aug 2026

IPDR

Status:
Imported

Records:
18,421

Bank Statements

Status:
Imported

Records:
8,942

Social Activity

Status:
Imported

Records:
14,821

Button:

Import Dataset

For the prototype, simulate the upload/import process with mock data.

23. IMPORT DATA FLOW

Create an attractive upload experience.

Step 1:

Upload Dataset

Step 2:

Detect Dataset Type

Example:

“Detected: CDR Dataset”

Step 3:

Map Fields

Caller → phone_a

Receiver → phone_b

Timestamp → timestamp

Duration → duration

Step 4:

Validate

Records:
12,482

Valid:
12,401

Warnings:
81

Step 5:

Import

Show progress.

Then:

Dataset successfully imported.

24. REPORT GENERATION

Create a:

Generate Investigation Report

button.

Report should contain:

Case information

Investigation summary

Key entities

High-priority leads

Anomalies

Transaction patterns

Communication patterns

Relationship graph summary

Timeline

Analytical findings

Data sources

For prototype purposes, generate a beautiful report preview page.

If actual PDF generation is feasible, implement it; otherwise provide a polished printable report view.

25. AUDIT TRAIL

Create an audit trail page.

Show:

16 Aug 2026 — Investigator uploaded CDR dataset

16 Aug 2026 — Entity analysis completed

16 Aug 2026 — Anomaly detection executed

16 Aug 2026 — Entity ENT-1092 reviewed

16 Aug 2026 — Investigation report generated

Each action should show:

timestamp

user

action

case

object/entity

26. ROLE-BASED ACCESS

Prototype roles:

Investigator

Can:

view cases

import data

investigate entities

view graph

analyze anomalies

generate reports

Senior Officer

Can:

view cases

review insights

review reports

view alerts

Administrator

Can:

manage users

manage system configuration

For the prototype, role switching can be simulated.

27. DEMO DATA

Populate the application with a realistic fictional investigation.

Create one primary case:

CASE-2026-1024

Online Financial Fraud Investigation

Use fictional entities:

Persons

ENT-1001

ENT-1002

ENT-1003

ENT-1004

Phones

PH-1001

PH-1002

PH-1003

Bank Accounts

AC-48291

AC-77218

AC-99102

AC-12038

Social Accounts

SOC-1001

SOC-1002

SOC-1003

IPs

IP-1001

IP-1002

IP-1003

Create enough relationships so the graph looks meaningful but remains readable.

28. PRIMARY DEMO SCENARIO

The entire application should be optimized around this story:

A suspected online financial fraud has occurred.

Investigators receive:

CDR data

IPDR data

Bank transaction records

Social activity records

The system processes the datasets.

It discovers:

12,481 entities

38,291 relationships

137 anomalies

23 high-priority leads

The investigator searches:

ENT-1092

The platform opens the entity.

The investigator sees:

multiple phone connections

financial relationships

social connections

IP relationships

anomaly indicators

The investigator opens:

Investigation Graph

and discovers that ENT-1092 acts as a potential bridge between two clusters.

Then the investigator opens:

Timeline

and sees:

18:02 — call

18:15 — ₹1,00,000 transfer

18:21 — call

18:34 — ₹95,000 transfer

18:41 — social activity

Then the system generates:

ACTIONABLE INVESTIGATIVE LEAD

“Entity ENT-1092 should be reviewed as a high-priority investigative lead because it connects multiple anomalous financial and communication events within the selected incident window.”

Then generate the investigation report.

This should be the main end-to-end demo flow.

29. MICRO-INTERACTIONS

Add subtle professional interactions:

hover states

graph node highlighting

animated loading when analyzing data

alert count transitions

expandable panels

slide-over entity details

tooltips

toast notifications

filter animations

Keep animations subtle and professional.

Do NOT over-animate the interface.

30. EMPTY STATES

Every major page should have a polished empty state.

Example:

“No investigation data available.”

Button:

Import Dataset

31. ERROR STATES

Create realistic errors:

Invalid dataset

Missing required column

Unsupported file

Data validation warning

Search result not found

Display clear explanations and recovery actions.

32. RESPONSIVENESS

Desktop is the priority.

Still make:

sidebar responsive

graph usable on smaller screens

tables horizontally scrollable

cards responsive

drawers responsive

33. ACCESSIBILITY

Use:

readable contrast

keyboard navigation where practical

semantic buttons

tooltips

accessible labels

clear severity indicators

Do not rely only on color to communicate severity.

34. COMPONENT ARCHITECTURE

Create reusable components:

Sidebar

TopBar

KPI Card

Alert Card

Case Card

Entity Card

Entity Drawer

Graph View

Timeline

DataTable

FilterBar

SearchBar

SeverityBadge

PriorityScore

DatasetUpload

InvestigationReport

EmptyState

LoadingState

ConfirmationDialog

Keep components modular.

35. DATA ARCHITECTURE

Create typed mock interfaces/types for:

Case
Entity
Phone
BankAccount
Transaction
SocialAccount
IPAddress
Device
Relationship
Communication
Anomaly
TimelineEvent
Dataset
InvestigationFinding
AuditEvent


Create a centralized mock data layer.

Do not hardcode the same values throughout multiple components.

36. UX PRINCIPLE

Every screen should answer:

“What does the investigator need to know next?”

Avoid showing meaningless metrics just to fill space.

The system should always move from:

Data → Pattern → Relationship → Explanation → Investigative Lead

37. FINAL VISUAL HIERARCHY

The most visually important features should be:

1. Investigation Graph

2. Timeline

3. Anomaly/Alert Center

4. Cross-Domain Entity Connections

5. Actionable Insights

The dashboard should make these immediately discoverable.

38. DO NOT BUILD A GENERIC CRM/ADMIN DASHBOARD

Avoid:

generic purple SaaS templates

generic employee dashboards

excessive charts

irrelevant KPIs

generic user-management-first UI

fake AI chatbot as the main feature

The core product is investigative intelligence.

39. FINAL PRODUCT POSITIONING

The application should communicate this message throughout the UI:

“Fragmented digital evidence becomes connected investigative intelligence.”

The platform should help investigators move from:

Thousands of records

↓

Connected entities

↓

Detected anomalies

↓

Reconstructed timeline

↓

Hidden relationships

↓

Actionable investigative leads

40. FINAL QUALITY BAR

Before considering the prototype complete, verify:

All sidebar pages work.

Navigation works.

Mock data is consistent across pages.

Search works.

Graph is interactive.

Clicking graph nodes opens entity details.

Timeline is interactive.

Filters work.

Alerts open relevant investigations.

Entity pages show cross-domain relationships.

Anomaly explanations are visible.

Priority scores are explainable.

Dataset import flow works as a simulation.

Case creation works as a prototype.

Report preview works.

Audit trail is populated.

Loading states exist.

Empty states exist.

Error states exist.

No broken buttons.

No placeholder “Lorem ipsum”.

No dead-end pages.

Most importantly, make the entire application feel like a real police digital-investigation intelligence product, not a college CRUD project.

The first screen should immediately communicate:

DIGITAL INVESTIGATION INTELLIGENCE PLATFORM

From Scattered Data to Actionable Intelligence.

And the primary call-to-action should be:

Open Investigation
or
Create New Case

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/6bb80ab7-0ea7-4a55-9be6-10961592a7ac).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
