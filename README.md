[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

# Smart Operations Automation Lab

Persönliches Lern- und Portfolio-Projekt: Konfiguration für eine selbst gehostete Automatisierungsumgebung mit n8n, einer eigenen Vault-API (FastAPI) und Monitoring (Prometheus/Grafana). Ziel ist, Workflows aus der Produktionslogistik (z. B. Schichtübergabe) lokal zu automatisieren.

---

## Was dieses Repo enthält

| Bereich | Inhalt | Pfad |
|---------|--------|------|
| Docker Compose | 7 Dienste: n8n, PostgreSQL, hermes-api, hermes-web-ui, Prometheus, Grafana, cloudflared | `docker/docker-compose.yml` |
| Vault-API | FastAPI-Dienst mit API-Key-Auth und Prometheus-Metriken | `docker/hermes-api/` |
| Web-UI | Node.js-Oberfläche für die Vault-API | `docker/hermes-web-ui/` |
| n8n-Workflows | 3 exportierte Workflows: Health Check, Vault Backup, Git Sync Monitor | `docker/workflows/` |
| Kubernetes | Manifeste für hermes-api, hermes-web-ui, PVC und 2 CronJobs (Backup, Git-Sync) | `kubernetes/` |
| Doku | Setup-Anleitungen für k3s, Vault-Sync, n8n, Slack, E-Mail | `docs/`, `docker/*.md` |

---

## Status

| Komponente | Status | Beleg |
|------------|--------|-------|
| Docker-Compose-Stack | Konfiguration vorhanden | `docker/docker-compose.yml` |
| n8n-Workflows | Als JSON exportiert | `docker/workflows/` |
| Kubernetes-Manifeste | Vorhanden, YAML syntaktisch gültig | `kubernetes/` |
| k3s-Cluster | In Arbeit — Betrieb nicht im Repo dokumentiert | — |
| n8n auf k3s | Geplant (kein Manifest vorhanden) | — |
| Monitoring auf k3s | Geplant (kein Manifest vorhanden) | — |

Status-Labels: **Vorhanden** = Datei im Repo · **In Arbeit** = begonnen, nicht belegt · **Geplant** = noch nicht begonnen.

---

## Schnellstart (lokal mit Docker)

```bash
cd docker
cp .env.example .env      # Werte setzen — ohne gesetzte Secrets startet der Stack nicht
make up                   # oder: docker compose up -d
make health
```

Danach erreichbar (lokal):

- n8n: http://localhost:5678
- Grafana: http://localhost:3001
- hermes-web-ui: http://localhost:8080
- Prometheus: http://localhost:9090
- hermes-api: http://localhost:8000/api/health

Details: [`docker/README.md`](docker/README.md)

---

## Kubernetes (k3s)

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/ -R
kubectl get pods -A
```

Anleitung für den Cluster-Aufbau: [`docs/DEPLOYMENT-GUIDE.md`](docs/DEPLOYMENT-GUIDE.md)

---

## Nächste Schritte

- [ ] k3s-Cluster fertigstellen und Betrieb dokumentieren (`kubectl get nodes` als Nachweis)
- [ ] Manifeste für n8n und Monitoring auf k3s erstellen
- [ ] Schichtübergabe-Workflow aus [ai-shift-handover-system](https://github.com/mario-bergsch/ai-shift-handover-system) als n8n-Workflow umsetzen

---

## Lizenz

MIT — siehe [LICENSE](LICENSE)

**Maintainer:** Mario Bergsch
