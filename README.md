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

## Key Features

- **Kubernetes-native:** k3s on Proxmox for lightweight, production-ready orchestration
- **Workflow Automation:** n8n for low-code, event-driven workflow pipelines
- **AI Integration:** Claude API for intelligent report generation and decision support
- **Full Observability:** Prometheus + Grafana dashboards, Alertmanager for incident routing
- **Shift Handover Automation:** SBAR/RCA reports generated automatically from shift notes
- **Scalable Architecture:** Namespace isolation, persistent storage, Harbor container registry

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

## Getting Started

### Prerequisites
- Proxmox cluster (3 nodes, 8+ GB RAM each)
- Linux admin knowledge
- Docker experience (helpful but not required)

### Deploy

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

## How to Use / Examples

### Check Platform Status
```bash
kubectl get pods --all-namespaces
kubectl get nodes
```

### Trigger Shift Handover Workflow (Phase 2)
```bash
curl -X POST http://n8n.smart-ops.local/webhook/shift-handover \\
  -H "Content-Type: application/json" \\
  -d '{"shift": "morning", "notes": "Line 3 stopped at 06:45 due to material jam. Resolved 07:10."}'
```

### View Dashboards
- Grafana: `http://grafana.smart-ops.local`
- Prometheus: `http://prometheus.smart-ops.local`
- n8n UI: `http://n8n.smart-ops.local`

### Working Example
See [ai-shift-handover-system](https://github.com/mario-bergsch/ai-shift-handover-system) for a fully working example of AI-powered shift report generation (MVP validated, 12/12 tests passed).

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

## Roadmap

### Phase 1: Foundation (May - June 2026)
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

---

## For Recruiters / Companies

- **Infrastructure as Code:** Kubernetes manifests, declarative infrastructure
- **Platform Engineering:** Building production-ready automation platforms
- **DevOps Practices:** Monitoring, logging, alerting, scaling
- **Manufacturing Focus:** Domain expertise in production operations

Interested in Smart Operations Platform as a Service? Let's talk.

---

## License

MIT License - See LICENSE file

---

**Created:** 2026-06-04
**Status:** Active Development
**Deadline:** 2026-06-30 (Phase 1-3)
