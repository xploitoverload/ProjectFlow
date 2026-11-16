# ProjectFlow

[![CI/CD Pipeline](https://github.com/xploitoverload/ProjectFlow/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/xploitoverload/ProjectFlow/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Security: Argon2id | AES-256-GCM](https://img.shields.io/badge/Security-Argon2id%20%7C%20AES--256--GCM-blueviolet.svg)](https://github.com/P-H-C/phc-winner-argon2)
[![Ledger: SHA--256 Blockchain](https://img.shields.io/badge/Audit-Cryptographic%20Blockchain%20Ledger-emerald.svg)](#-tamper-evident-blockchain-audit-ledger)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> **High-Performance, Self-Hosted Jira/Linear Alternative Built with Systems-Grade Security Discipline.**  
> Featuring biometric Facial ID authentication, memory-hard Argon2id hashing, pluggable cryptographic architecture, and a tamper-evident SHA-256 blockchain audit ledger.

<p align="center">
  <img src="docs/images/cyberhound_hero_banner.png" alt="ProjectFlow Cyberhound Engine" width="100%">
</p>

---

## ⚡ Why ProjectFlow?

Most project trackers are either heavy enterprise beasts consuming gigabytes of RAM or fragile web apps with superficial security. **ProjectFlow** is engineered with kernel-grade discipline:

- 🚀 **Blazingly Fast**: Lightweight, responsive Kanban boards with sub-20ms queries and instant workflow transitions.
- 🛡️ **Ring 0 Security Philosophy**:
  - **Biometric Facial Recognition**: Hardware-accelerated local facial embeddings (128-d vectors) with anti-spoofing liveness detection.
  - **Pluggable Cryptographic Provider System**: Freedom to choose or plug in Argon2id, PBKDF2-SHA512, Scrypt, Bcrypt, or custom enterprise algorithms.
  - **Tamper-Evident SHA-256 Blockchain Ledger**: Every administrative, security, and authentication event is cryptographically chained ($hash_n = \text{SHA256}(hash_{n-1} + \text{event})$), detecting database tampering immediately.
  - **Zero-Bypass Access Control**: 100% route coverage with cryptographic session fingerprinting, replay-attack-resistant HMAC request signing, and strict object-level access controls (IDOR prevention).
- 📊 **Real-World Agile Workflows**: Native support for Epics, Sprints, Kanban Board drag-and-drop, Issue dependencies, and Encrypted Comments.
- 🐳 **1-Command Docker Deployment**: Ready to run out of the box on Linux, macOS, and container clusters.

---

## 🚀 Quickstart

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/xploitoverload/ProjectFlow.git
cd ProjectFlow

# Run with docker-compose
docker compose up -d
```
Access the application at `http://localhost:5000`.

### Option 2: Local Setup

```bash
# 1. Clone repository
git clone https://github.com/xploitoverload/ProjectFlow.git
cd ProjectFlow

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python run.py
```

---

## 🛡️ Systems-Grade Security & Cryptographic Core

### 1. Cyberhound Authentication & Biometric Scanner Gate
Redesigned authentication portal featuring the ProjectFlow Cyberhound identity, glowing neon crimson telemetry, and hardware biometric facial ID integration.

### 2. Ring-0 Cyberhound Neural Biometric Gate
On-device hardware optical sensor tracking neural facial landmarks at 60 FPS. Features dynamic challenge-response anti-spoofing (eye-aspect-ratio blink analysis, micro-motion entropy, and Laplacian texture frequency analysis) combined with 128-dimensional Euclidean tensor matching ($D \le 0.45$). All biometric embeddings are encrypted with AES-256 before disk storage and linked to the tamper-evident SHA-256 audit ledger.

### 3. Tamper-Evident SHA-256 Blockchain Audit Ledger
All security events, permission escalations, and logins are committed to an append-only cryptographic blockchain ledger. Each block links back to the preceding block:

$$\text{record\_hash}_i = \text{SHA256}(\text{prev\_hash}_{i-1} \,\|\, \text{user\_id} \,\|\, \text{action} \,\|\, \text{payload} \,\|\, \text{timestamp})$$

Any direct database tampering, row modification, or row deletion permanently invalidates the cryptographic chain and triggers an immediate alert during integrity verification (`/api/v1/audit/ledger/verify`).

### 4. Pluggable Cryptographic Engine & Zero-Bypass Access Control
ProjectFlow implements a modular Cryptographic Service Provider Interface (`app/crypto/`) allowing deployers to choose or implement their own hashing algorithms and authenticated ciphers:

- **Built-in Hashing Providers**:
  - `argon2id` *(Default - OWASP Gold Standard memory-hard hashing)*
  - `pbkdf2_sha512` *(FIPS 140-2 / NIST SP 800-132 compliant with 600,000 iterations)*
  - `scrypt` *(RFC 7914 memory-hard key derivation)*
  - `bcrypt` *(Configurable enterprise work factor)*
  - `custom` *(Pluggable provider hook supporting custom HSM, Blake3, or Post-Quantum algorithms)*
- **Authenticated AEAD Field Ciphers**:
  - `aes_256_gcm` *(NIST SP 800-38D with 96-bit nonce & 128-bit tag)*
  - `chacha20_poly1305` *(RFC 8439 high-performance stream cipher)*
  - `fernet` *(Backward-compatible symmetric token cipher)*
- **Zero-Friction Transparent Auto-Migration**:
  - When switching hashing algorithms, existing users' passwords are automatically verified and re-hashed into the new active algorithm on their next login with zero downtime.
- **Pluggable Custom Provider Example**:
  ```python
  from app.crypto import crypto_manager, CustomHasherProvider

  class QuantumResistantHasher(CustomHasherProvider):
      name = "my_custom_hasher"
      def hash(self, password: str) -> str:
          ...
      def verify(self, password: str, hashed: str) -> bool:
          ...

  crypto_manager.register_hasher("my_custom_hasher", QuantumResistantHasher())
  ```
- **Zero-Bypass Ring-0 Enforcement**:
  - 100% route coverage with cryptographic session fingerprinting (`AuthService`), replay-attack resistant HMAC signatures (`X-Request-Signature`), strict object-level access controls (IDOR prevention), and instantaneous session invalidation.

---

## 📸 Complete ProjectFlow Visual Showcase

> **Click on any arrow (▶) button below to expand the full visual tour of that subsystem.**

<details>
<summary><b>▶ 🛡️ 1. Identity, Authentication & Biometric Scanner Nodes (Click to Expand)</b></summary>
<br>

#### 🔐 Sign In Portal with Cyberhound Identity
High-assurance authentication entrypoint featuring dynamic theme controls, rate limiting, and instant biometric trigger.
<p align="center">
  <img src="docs/images/login_portal.png" alt="Cyberhound Sign In Portal" width="100%">
</p>

#### 🔬 In-Page Biometric Scanner Modal Overlay
Direct in-page WebRTC optical sensor scanner modal allowing one-click biometric verification without navigating away.
<p align="center">
  <img src="docs/images/login_biometric_modal.png" alt="Login Biometric Scanner Modal" width="100%">
</p>

#### ⚡ Ring-0 Cyberhound Neural Biometric Gate
60 FPS hardware facial telemetry with 68-point neural landmark constellation overlay, scanning laser bar, and challenge-response liveness detection.
<p align="center">
  <img src="docs/images/biometric_facial_gate.png" alt="Ring-0 Neural Biometric Facial Gate" width="100%">
</p>

#### 📝 Account Registration Portal
New engineer onboarding portal with real-time password strength validation, department selection, and cryptographic email encryption.
<p align="center">
  <img src="docs/images/registration_portal.png" alt="Registration Portal" width="100%">
</p>

#### 🔑 Self-Service Password Recovery
Enumeration-resistant password reset dispatch workflow with time-locked, single-use cryptographic tokens.
<p align="center">
  <img src="docs/images/forgot_password.png" alt="Password Recovery Portal" width="100%">
</p>

#### 🎯 Optical Biometric Enrollment & Setup Guide
Interactive calibration guide for enrolling primary optical sensors, setting confidence thresholds, and testing anti-spoofing detection.
<p align="center">
  <img src="docs/images/facial_setup_guide.png" alt="Biometric Enrollment Setup Guide" width="100%">
</p>

</details>

---

<details>
<summary><b>▶ 📊 2. Engineering & Delivery Workspace Nodes (Click to Expand)</b></summary>
<br>

#### 🏠 Unified Engineering Delivery Command Hub
Active sprint velocity telemetry, burndown progress, cross-project workload distribution, and real-time event streams.
<p align="center">
  <img src="docs/images/workspace_dashboard.png" alt="Workspace Command Dashboard" width="100%">
</p>

#### 📋 Agile Kanban Board
Interactive drag-and-drop workflow board with sub-20ms transitions, swimlanes, custom statuses, card tags, and instant filter toggling.
<p align="center">
  <img src="docs/images/agile_kanban_board.png" alt="Agile Kanban Board" width="100%">
</p>

#### 🗓️ Interactive Roadmap & Gantt Engine
Drag-and-drop task scheduling across Day, Week, Month, and Quarter views with real-time SVG dependency connectors and Critical Path Method (CPM) calculation.
<p align="center">
  <img src="docs/images/gantt_roadmap_timeline.png" alt="Interactive Roadmap and Gantt Engine" width="100%">
</p>

#### 🕸️ Directed Topological Dependency Graph
Graph visualizer linking issues across projects with cycle prevention, direction indicators, and topological conflict detection.
<p align="center">
  <img src="docs/images/topological_dependency_graph.png" alt="Topological Dependency Graph" width="100%">
</p>

#### 👥 Resource Capacity & Utilization Planner
Contributor workload normalization, weekly allocation heatmaps, and automatic over-capacity warning indicators.
<p align="center">
  <img src="docs/images/resource_capacity_planner.png" alt="Resource Capacity Planner" width="100%">
</p>

#### 🎯 Strategic Portfolio Roadmaps
Cross-project strategic initiative planning, delivery progress rollups, and multi-team health tracking.
<p align="center">
  <img src="docs/images/strategic_portfolio_roadmap.png" alt="Strategic Portfolio Roadmap" width="100%">
</p>

#### 📦 Sprint Grooming & Backlog Prioritization
Issue ranking, velocity point estimation, and drag-and-drop backlog prioritization.
<p align="center">
  <img src="docs/images/project_backlog_sprints.png" alt="Sprint Backlog Grooming" width="100%">
</p>

#### 🔍 Issue Navigator & Multi-Filter Omnibox
Advanced issue query engine with multi-parameter filtering by status, priority, assignee, tags, and milestone associations.
<p align="center">
  <img src="docs/images/issues_navigator.png" alt="Issue Navigator and Filters" width="100%">
</p>

#### 📈 Velocity Analytics & Cumulative Flow
Real-time sprint velocity charts, cumulative flow diagrams, and historical burndown metrics.
<p align="center">
  <img src="docs/images/reports_velocity_analytics.png" alt="Reports and Velocity Analytics" width="100%">
</p>

#### 📅 Schedule Planning & Milestones Calendar
Calendar-based milestone schedule, release dates, and scheduled issue delivery timelines.
<p align="center">
  <img src="docs/images/calendar_schedule_planning.png" alt="Calendar Planning View" width="100%">
</p>

#### 🎫 ITIL Service Desk & Support Ticket Hub
Customer and internal service request management with SLA tracking, priority queues, and customer communication threads.
<p align="center">
  <img src="docs/images/service_desk_tickets.png" alt="ITIL Service Desk Tickets" width="100%">
</p>

#### ⚡ Workflow Automation Engine
Visual rules engine automating issue assignments, status transitions, notifications, and webhooks upon state changes.
<p align="center">
  <img src="docs/images/workflow_automation_engine.png" alt="Workflow Automation Engine" width="100%">
</p>

</details>

---

<details>
<summary><b>▶ 📁 3. Project Lifecycle & Code Governance Nodes (Click to Expand)</b></summary>
<br>

#### 🏢 Project Overview & Executive Summary Hub
Centralized project homepage with health metrics, milestone status, team assignments, and delivery summaries.
<p align="center">
  <img src="docs/images/project_overview_hub.png" alt="Project Overview Hub" width="100%">
</p>

#### 🏃 Sprint Cycles & Lifecycle Management
Active, planned, and completed sprint orchestration with velocity forecasting and scope creep monitoring.
<p align="center">
  <img src="docs/images/project_sprints_management.png" alt="Sprint Cycles Management" width="100%">
</p>

#### 🏆 Epic Roadmaps & Milestone Tracking
High-level epic management grouping related user stories into strategic delivery increments.
<p align="center">
  <img src="docs/images/project_epics_management.png" alt="Epic Roadmaps Management" width="100%">
</p>

#### 📑 Project Issue Catalog & Work Items
Comprehensive catalog of work items, bugs, tasks, and stories scoped to the active project.
<p align="center">
  <img src="docs/images/project_issues_catalog.png" alt="Project Issue Catalog" width="100%">
</p>

#### 📉 Sprint Velocity & Burndown Charts
Real-time burndown analytics comparing ideal vs. actual sprint trajectory.
<p align="center">
  <img src="docs/images/project_velocity_reports.png" alt="Sprint Velocity Reports" width="100%">
</p>

#### 🛡️ Project Security Governance & Access Auditing
Project-level security controls, role assignments, sensitive field encryption audit, and access history.
<p align="center">
  <img src="docs/images/project_security_governance.png" alt="Project Security Governance" width="100%">
</p>

#### 🔗 Git & VCS Code Integrations
GitHub, GitLab, and Gitea webhook synchronization linking commits, pull requests, and branch builds directly to issues.
<p align="center">
  <img src="docs/images/project_vcs_code_integrations.png" alt="Git and VCS Code Integrations" width="100%">
</p>

#### 🚀 CI/CD Deployments & Release Pipelines
Deployment tracking across development, staging, and production environments with commit traceability.
<p align="center">
  <img src="docs/images/project_deployments_pipeline.png" alt="CI/CD Deployment Pipelines" width="100%">
</p>

#### 🏁 Release Management & Artifact Milestones
SemVer release tagging, changelog generation, and milestone delivery status.
<p align="center">
  <img src="docs/images/project_releases_milestones.png" alt="Release Milestones Management" width="100%">
</p>

#### 🏷️ Taxonomy, Labels & Categorization Tags
Customizable project taxonomy tags, color palettes, and component categorization.
<p align="center">
  <img src="docs/images/project_labels_tags.png" alt="Project Labels and Tags" width="100%">
</p>

#### 🔄 State Machine Workflow Diagrams
Visual representation of permitted issue states and transition constraints.
<p align="center">
  <img src="docs/images/project_workflow_diagram.png" alt="State Machine Workflow Diagram" width="100%">
</p>

#### ⚙️ Project Settings & Configurations
Project keys, lead designations, default assignees, and integration secrets.
<p align="center">
  <img src="docs/images/project_settings_config.png" alt="Project Configuration and Settings" width="100%">
</p>

</details>

---

<details>
<summary><b>▶ ⚙️ 4. Enterprise Administration & Cryptographic Governance Nodes (Click to Expand)</b></summary>
<br>

#### 🎛️ Admin System Overview & Command Plane
Comprehensive administrative telemetry monitoring system health, active sessions, database connections, and worker threads.
<p align="center">
  <img src="docs/images/admin_command_dashboard.png" alt="Admin Command Dashboard" width="100%">
</p>

#### ⛓️ Tamper-Evident SHA-256 Blockchain Audit Ledger
Append-only cryptographic ledger tracking every administrative action with sequential block hash linking.
<p align="center">
  <img src="docs/images/admin_sha256_audit_ledger.png" alt="Tamper-Evident SHA-256 Audit Ledger" width="100%">
</p>

#### 🛡️ Security Policies & Governance Center
Enterprise security policies, session timeout parameters, brute-force lockout thresholds, and cipher preferences.
<p align="center">
  <img src="docs/images/admin_security_policies.png" alt="Security Policies and Center" width="100%">
</p>

#### 👥 User & Privilege Administration (RBAC)
Granular user privilege administration, role assignment, account unlocking, and active session termination.
<p align="center">
  <img src="docs/images/admin_user_privileges_rbac.png" alt="User Privileges and RBAC" width="100%">
</p>

#### 🏢 Team Allocations & Permissions
Team modeling, member associations, and cross-project permissions.
<p align="center">
  <img src="docs/images/admin_teams_allocation.png" alt="Team Allocations and Permissions" width="100%">
</p>

#### 🗄️ Database Health, Indexing & Storage Engine
Live database status, connection pools, index performance, and disk usage telemetry.
<p align="center">
  <img src="docs/images/admin_database_health.png" alt="Database Health and Storage" width="100%">
</p>

#### 💾 Backup, Point-in-Time Restore & Snapshots
Automated database snapshot creation, export, and point-in-time disaster recovery.
<p align="center">
  <img src="docs/images/admin_backup_restore.png" alt="Database Backup and Restore" width="100%">
</p>

#### 🤖 Enterprise Automation Rules & Triggers
Global event-driven automation rules managing system alerts, escalations, and cross-project sync.
<p align="center">
  <img src="docs/images/admin_automation_rules.png" alt="Admin Automation Rules" width="100%">
</p>

#### 🧬 Facial ID Hardware & Biometric Vault Settings
Vault configurations for facial recognition confidence thresholds, anti-spoofing parameters, and vector revocations.
<p align="center">
  <img src="docs/images/admin_facial_id.png" alt="Facial ID Vault Settings" width="100%">
</p>

#### 🔌 Third-Party Webhooks & Integrations
Slack, Microsoft Teams, Jira sync, and custom webhook endpoint configurations.
<p align="center">
  <img src="docs/images/admin_third_party_integrations.png" alt="Third-Party Integrations and Webhooks" width="100%">
</p>

#### 📆 Enterprise Change Management Calendar
Scheduled system maintenance windows, freeze periods, and deployment change approvals.
<p align="center">
  <img src="docs/images/admin_change_calendar.png" alt="Change Management Calendar" width="100%">
</p>

#### 🔧 Diagnostic & Maintenance Utilities
Cache invalidation, orphan record cleanup, and diagnostic ping utilities.
<p align="center">
  <img src="docs/images/admin_maintenance_tools.png" alt="Maintenance and Diagnostics Tools" width="100%">
</p>

#### 🔎 Global Index Search Omnibox
Full-text index search administration across issues, comments, projects, and users.
<p align="center">
  <img src="docs/images/admin_global_index_search.png" alt="Global Index Search Omnibox" width="100%">
</p>

#### 👥 Organization Team Directory
Visual directory of teams, leadership contacts, and member assignments.
<p align="center">
  <img src="docs/images/team_directory.png" alt="Organization Team Directory" width="100%">
</p>

#### ⚙️ User Profile & Account Preferences
Personal profile settings, avatar customization, dark/light theme toggle, and personal notifications.
<p align="center">
  <img src="docs/images/user_profile_settings.png" alt="User Profile Settings" width="100%">
</p>

</details>

---

## 📡 RESTful API & Automation Engine

ProjectFlow includes an enterprise-grade RESTful API authenticated via cryptographically signed Bearer tokens:

```bash
# 1. Obtain Bearer Token
curl -X POST http://localhost:5000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "AdminPassword123!"}'

# 2. Verify Cryptographic SHA-256 Blockchain Audit Ledger Integrity (Ring 0)
curl -X GET http://localhost:5000/api/v1/audit/ledger/verify \
  -H "Authorization: Bearer <TOKEN>"

# 3. Create Project & Issues
curl -X POST http://localhost:5000/api/v1/projects \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Kernel Hypervisor", "key": "KHM", "workflow_type": "agile"}'

# 4. Fetch Sprint Burndown & Velocity Analytics
curl -X GET http://localhost:5000/api/v1/analytics/burndown/1 \
  -H "Authorization: Bearer <TOKEN>"
```

---

## 🤝 Contributing

Contributions are welcome! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming conventions, pre-commit standards, and pull request guidelines.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/amazing-feature`)
3. Commit your Changes (`git commit -m 'Add amazing feature'`)
4. Push to the Branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Developed with systems precision by [Kalpesh Solanki (@xploitoverload)](https://github.com/xploitoverload).
