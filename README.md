# Smart Operations Automation Lab

**Status:** 🔄 In Development | **Phase:** Infrastructure Build (Deadline: 2026-06-30)

A Kubernetes-based automation platform for smart operations workflows. Building the infrastructure to deploy, test, and scale AI-driven workflow automation in production environments.

---

## Vision

Deploy smart operations workflows (like AI Shift Handover) into a production-ready platform:

- **Reliable:** Kubernetes-based high availability
- **Scalable:** Handle multiple shifts, facilities, and workflows
- **Observable:** Prometheus metrics, logs, alerts
- **Extensible:** n8n for low-code automation, Claude AI for intelligence

---

## Current Status (as of 2026-06-04)

| Component | Status | Target |
|-----------|--------|--------|
| **Phase 1: Infrastructure** | 🔄 In Progress | 2026-06-15 |
| Proxmox Cluster (3 nodes) | ✅ Complete | 2026-05-31 |
| k3s Kubernetes | 🔄 In Progress | 2026-06-15 |
| Persistent Storage | 🔄 Planned | 2026-06-15 |
| **Phase 2: Core Services** | 🔄 Planned | 2026-06-25 |
| n8n Workflow Engine | 🔄 Planned | 2026-06-20 |
| Monitoring Stack (Prometheus/Grafana) | 🔄 Planned | 2026-06-25 |
| Harbor Container Registry | 🔄 Planned | 2026-06-25 |
| **Phase 3: Operations** | 🔄 Planned | 2026-06-30 |
| Alerting & Escalations | 🔄 Planned | 2026-06-30 |
| Workflow Deployments | 🔄 Planned | 2026-06-30 |
| Production Monitoring | 🔄 Planned | 2026-06-30 |

---

## Architecture

```
┌─────────────────────────────────────┐
│    Smart Operations Platform        │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  Kubernetes (k3s on Proxmox)        │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Namespace: automation        │  │
│  │ ├─ n8n (Workflows)           │  │
│  │ ├─ MongoDB (State)           │  │
│  │ └─ Redis (Cache)             │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Namespace: monitoring        │  │
│  │ ├─ Prometheus                │  │
│  │ ├─ Grafana                   │  │
│  │ └─ Alertmanager              │  │
│  └──────────────────────────────┘  │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Namespace: registry          │  │
│  │ └─ Harbor (Container Images) │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
           ↓
     ┌─────────────────┐
     │ Persistent      │
     │ Volume Claims   │
     └─────────────────┘
```

---

## What's Planned (Phase 2-3)

### Workflows

**Shift Handover Automation**
```
New shift notes detected
  ↓
n8n triggers Claude AI SBAR/RCA prompts
  ↓
Generate structured reports
  ↓
Post to Slack #shift-reports
  ↓
Archive to Obsidian knowledge base
```

**Smart KPI Reporting**
- Aggregate production data from SAP/MES
- Calculate real-time OEE
- Auto-escalate when metrics exceed thresholds

**Quality Issue Automation**
- Parse quality problems
- Trigger RCA workflow
- Assign to teams
- Track closure time

### Monitoring & Alerts

- Production metrics dashboard (Grafana)
- Workflow execution logs (Loki)
- Alert routing to Slack/Email
- SLA tracking

---

## Getting Started (Phase 2)

### Prerequisites
- Proxmox cluster (3 nodes, 8+ GB RAM each)
- Linux admin knowledge
- Docker experience (helpful but not required)

### Deploy (when Phase 2 ready)

```bash
# 1. Set up k3s cluster
curl -sfL https://get.k3s.io | sh -

# 2. Create namespaces
kubectl create ns automation
kubectl create ns monitoring

# 3. Deploy n8n
kubectl apply -f kubernetes/n8n-deployment.yaml

# 4. Deploy Monitoring
kubectl apply -f kubernetes/monitoring-stack.yaml

# 5. Check status
kubectl get pods --all-namespaces
```

Full deployment guide coming July 2026.

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Orchestration** | Kubernetes (k3s) | Container orchestration |
| **Workflow Engine** | n8n | Low-code workflow builder |
| **AI Integration** | Claude API (Anthropic) | Intelligent decision making |
| **Monitoring** | Prometheus + Grafana | Metrics and dashboards |
| **Logging** | Loki (optional Phase 3) | Centralized logs |
| **Registry** | Harbor | Private container images |
| **Notifications** | Slack, Email, SMS | Alert delivery |
| **Language** | Python, JavaScript | Workflow scripting |

---

## Repository Structure

```
smart-operations-automation-lab/
├── README.md (this file)
├── LICENSE (MIT)
├── /kubernetes/
│   ├── namespace.yaml (k3s setup)
│   ├── pvc-storage.yaml (persistent volumes)
│   ├── n8n-deployment.yaml
│   ├── n8n-service.yaml
│   ├── prometheus-deployment.yaml
│   ├── grafana-deployment.yaml
│   └── harbor-deployment.yaml
├── /workflows/
│   ├── shift-handover-automation.json
│   ├── smart-kpi-reporting.json
│   └── quality-escalation.json
├── /monitoring/
│   ├── prometheus-config.yaml
│   ├── grafana-dashboards.yaml
│   └── alerting-rules.yaml
├── /docs/
│   ├── DEPLOYMENT.md
│   ├── OPERATIONS.md
│   └── ROADMAP.md
└── /scripts/
    └── setup-cluster.sh
```

---

## Roadmap

### Phase 1: Foundation (May - June 2026) ✅
- [x] Proxmox cluster setup
- [ ] k3s cluster initialization
- [ ] Storage configuration

### Phase 2: Services (June - July 2026) 🔄
- [ ] n8n deployment
- [ ] Monitoring stack (Prometheus/Grafana)
- [ ] Container registry (Harbor)
- [ ] Network policies

### Phase 3: Operations (July - September 2026) 📋
- [ ] First workflow deployment (Shift Handover)
- [ ] SAP OData integration
- [ ] Production monitoring
- [ ] Team training & documentation

### Phase 4: Scale (September+ 2026) 📋
- [ ] Multi-cluster setup
- [ ] Disaster recovery
- [ ] Advanced analytics

---

## For Recruiters / Companies

This lab demonstrates:

- **Infrastructure as Code:** Kubernetes manifests, declarative infrastructure
- **Platform Engineering:** Building production-ready automation platforms
- **DevOps Practices:** Monitoring, logging, alerting, scaling
- **Integration Design:** Connecting disparate systems (n8n, Claude, SAP, Slack)
- **Manufacturing Focus:** Domain expertise in production operations

Interested in Smart Operations Platform as a Service? Let's talk.

---

## License

MIT License - See LICENSE file

---

**Created:** 2026-06-04  
**Status:** Active Development  
**Deadline:** 2026-06-30 (Phase 1-3)
