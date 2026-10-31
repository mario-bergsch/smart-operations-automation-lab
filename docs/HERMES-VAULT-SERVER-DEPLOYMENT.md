---
type: guide
title: Hermes Vault Server Deployment on k3s
date: 2026-05-30
status: complete
---

# Hermes Vault Server Deployment Guide

**Objective:** Deploy Hermes Vault as a multi-device web service on k3s cluster with git sync, monitoring, and backup.

**Estimated Implementation Time:** 21-31 hours (Phases 1-6)  
**Deadline:** 2026-07-05 (aligned with Smart Operations Lab)  
**Prerequisites:** k3s cluster running with 3+ nodes, GitHub SSH access, Cloudflare account

---

## Overview

This guide deploys the complete Hermes Vault infrastructure:
- **Web UI:** React frontend at https://hermes.mbergsch.com
- **API Backend:** FastAPI at https://vault.mbergsch.com/api
- **Git Sync:** Hourly sync with GitHub (read-only)
- **Backups:** Daily tar.gz backups with 30-day retention
- **Monitoring:** Prometheus metrics + Grafana dashboards
- **External Access:** Cloudflare Tunnel (zero-trust, no port forwarding)

---

## Phase 1: Foundation & Preparation (By 2026-06-07)

### 1.1 Verify k3s Cluster

```bash
# Check cluster status
kubectl get nodes
kubectl get namespaces

# Expected: 3+ nodes in Ready state
# Output should include kube-system, default namespaces
```

### 1.2 Prepare Credentials

```bash
# GitHub SSH Deploy Key
ssh-keygen -t ed25519 -f ~/.ssh/hermes-github -N ""
cat ~/.ssh/hermes-github.pub

# Add to GitHub repo settings:
# Settings → Deploy keys → Add deploy key
# Title: hermes-k3s-git-sync
# Key: [paste public key]
# Allow write access: NO (read-only)

# Save private key as Kubernetes secret (Phase 2)
```

### 1.3 Cloudflare Tunnel Setup

```bash
# Create tunnel in Cloudflare dashboard
# https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/

# You'll get:
# - Tunnel ID (uuid)
# - Tunnel Token (secret)
# - Credentials JSON

# Export for Phase 3
export TUNNEL_ID="<uuid>"
export TUNNEL_TOKEN="<token>"
```

### 1.4 Storage Verification

```bash
# Check local-path provisioner is available
kubectl get sc
# Should include: local-path (default)

# Check available disk space
df -h /var/lib/rancher/k3s/storage/
# Minimum: 100GB recommended for vault + backups
```

---

## Phase 2: Core Deployment (By 2026-06-14)

### 2.1 Deploy Kubernetes Infrastructure

```bash
# Apply all manifests in order
cd <PFAD-ZUM-REPO>

# 1. Namespace & RBAC
kubectl apply -f kubernetes/namespace.yaml

# 2. Storage
kubectl apply -f kubernetes/pvc-vault-storage.yaml

# 3. Services (API must deploy before Web UI)
kubectl apply -f kubernetes/hermes-api/service.yaml
kubectl apply -f kubernetes/hermes-web-ui/service.yaml

# 4. Deployments (API first for readiness probe)
kubectl apply -f kubernetes/hermes-api/deployment.yaml
kubectl apply -f kubernetes/hermes-web-ui/deployment.yaml

# Verify rollout
kubectl -n hermes rollout status deployment/hermes-api --timeout=5m
kubectl -n hermes rollout status deployment/hermes-web-ui --timeout=5m
```

### 2.2 Deploy Secrets

```bash
# GitHub SSH Key
kubectl -n hermes create secret generic github-ssh-key \
  --from-file=ssh-privatekey=$HOME/.ssh/hermes-github

# Verify
kubectl -n hermes describe secret github-ssh-key
```

### 2.3 Verify Pods Running

```bash
# Check all pods are ready
kubectl -n hermes get pods -o wide

# Expected output (all Ready 1/1, Running):
# NAME                             READY   STATUS
# hermes-api-xxxxx                 1/1     Running
# hermes-api-xxxxx                 1/1     Running
# hermes-web-ui-xxxxx              1/1     Running
# hermes-web-ui-xxxxx              1/1     Running

# Check logs
kubectl -n hermes logs deployment/hermes-api
kubectl -n hermes logs deployment/hermes-web-ui
```

### 2.4 Test Internal Connectivity

```bash
# Port-forward to hermes-api
kubectl -n hermes port-forward svc/hermes-api 8000:8000 &

# Test health endpoint
curl http://localhost:8000/api/health

# Expected response:
# {
#   "status": "healthy",
#   "vault_accessible": true,
#   "git_status": "synced",
#   "timestamp": "2026-06-14T..."
# }

# Stop port-forward
pkill -f "port-forward"
```

---

## Phase 3: External Access (By 2026-06-21)

### 3.1 Create Ingress Rules

```bash
# Deploy ingress (waits for cert-manager cert)
kubectl apply -f kubernetes/hermes-web-ui/ingress.yaml

# Check ingress status
kubectl -n hermes get ingress -o wide
# May show <pending> for IP until Cloudflare tunnel is active
```

### 3.2 Deploy Cloudflare Tunnel

```bash
# Update tunnel configuration with your tunnel ID/token
# Edit: 07-Infrastructure/kubernetes/secrets/cloudflare-config.yaml
# Replace:
#   - TUNNEL_ID with your tunnel ID
#   - TUNNEL_TOKEN with your tunnel token (base64 encoded)

# For base64 encoding token:
echo -n "YOUR_TOKEN" | base64

# Deploy cloudflared daemon
kubectl -n hermes apply -f kubernetes/secrets/cloudflare-token.yaml
kubectl -n hermes apply -f cloudflare/cloudflared-deployment.yaml

# Verify tunnel is running
kubectl -n hermes get pods -l app=cloudflared
```

### 3.3 Configure DNS Records

In Cloudflare Dashboard:
```
DNS Records to create:
- hermes.mbergsch.com → Tunnel (select your tunnel)
- vault.mbergsch.com → Tunnel (select your tunnel)
```

Tunnel Ingress Rules (in cloudflared config):
```yaml
ingress:
  - hostname: hermes.mbergsch.com
    service: http://hermes-web-ui:80
  - hostname: vault.mbergsch.com
    path: /api
    service: http://hermes-api:8000
  - service: http_status:404
```

### 3.4 Test External Access

```bash
# Wait for DNS propagation (5-10 minutes)
nslookup hermes.mbergsch.com
nslookup vault.mbergsch.com

# Test HTTPS endpoints
curl -I https://hermes.mbergsch.com
# Expected: 200 OK or redirect

curl https://vault.mbergsch.com/api/health
# Expected: JSON health response
```

---

## Phase 4: Git Synchronization (By 2026-06-28)

### 4.1 Deploy Git-Sync CronJob

```bash
# Create git-sync secret with deploy key
kubectl -n hermes create secret generic git-credentials \
  --from-file=id_ed25519=$HOME/.ssh/hermes-github

# Deploy CronJob
kubectl apply -f kubernetes/cron-jobs/git-sync.yaml

# Verify CronJob created
kubectl -n hermes get cronjobs
```

### 4.2 Test Git-Sync Manually

```bash
# Trigger manual job (testing)
kubectl -n hermes create job git-sync-test --from=cronjob/git-sync

# Check job logs
kubectl -n hermes logs job/git-sync-test

# Expected log output:
# Fetching from GitHub...
# Current HEAD is ahead of origin → checking for conflicts
# No conflicts detected
# Vault synced successfully
```

### 4.3 Verify Sync Works

```bash
# Make a change in vault (locally or via GitHub)
echo "Test sync" >> /path/to/vault/test-sync.md
git -C /path/to/vault add test-sync.md
git -C /path/to/vault commit -m "test sync"
git -C /path/to/vault push origin main

# Wait for next hour (or manually trigger job)
# Then check if file appears in vault volume
kubectl -n hermes exec deployment/hermes-api -- \
  ls -la /vault/test-sync.md
```

---

## Phase 5: Backup Strategy (By 2026-07-05)

### 5.1 Deploy Backup CronJob

```bash
# Deploy daily backup
kubectl apply -f kubernetes/cron-jobs/backup-vault.yaml

# Verify CronJob
kubectl -n hermes get cronjobs
```

### 5.2 Configure Backup Destination

Choose one or more:

**Option A: Local Storage (Current)**
- Backups go to: `/var/lib/rancher/k3s/storage/hermes/backups/`
- 30-day rotation automatic

**Option B: NAS Mount (Recommended)**
```bash
# Mount NAS in k3s node (example: NFS)
# Edit: kubernetes/cron-jobs/backup-vault.yaml
# Add volume:
volumes:
  - name: nfs-backup
    nfs:
      server: 192.168.1.100  # NAS IP
      path: /export/hermes-backups
      
# Add volumeMount:
volumeMounts:
  - name: nfs-backup
    mountPath: /mnt/nfs-backups
```

**Option C: Google Drive (Via rclone)**
```bash
# Install rclone in backup container
# Configure Google Drive remote
rclone config

# Add to backup script:
tar -czf backup.tar.gz /vault
rclone copy backup.tar.gz google-drive:hermes-backups/
```

### 5.3 Test Backup & Recovery

```bash
# Trigger backup manually
kubectl -n hermes create job backup-test --from=cronjob/backup-vault

# Check backup was created
kubectl -n hermes exec deployment/hermes-api -- \
  ls -lh /vault/backups/

# Test recovery procedure:
# 1. Extract backup
tar -xzf /vault/backups/vault-2026-06-15.tar.gz -C /tmp/restore

# 2. Verify files are intact
ls -la /tmp/restore/vault/

# 3. Check git history is preserved
cd /tmp/restore/vault
git log --oneline | head -20
```

---

## Phase 6: Monitoring & Observability (By 2026-07-05)

### 6.1 Deploy Prometheus & Grafana

```bash
# Assuming Prometheus + Grafana already running on cluster
# (from Smart Operations Lab Phase 3)

# Deploy ServiceMonitor for Hermes (if using Prometheus Operator)
kubectl -n hermes apply -f monitoring/servicemonitor-hermes.yaml

# Or add scrape config to existing Prometheus ConfigMap:
kubectl -n monitoring edit configmap prometheus-config

# Add under scrape_configs:
- job_name: 'hermes-api'
  static_configs:
    - targets: ['hermes-api.hermes:8000']
  metrics_path: '/metrics'

- job_name: 'hermes-web-ui'
  static_configs:
    - targets: ['hermes-web-ui.hermes:8080']
```

### 6.2 Create Grafana Dashboards

```bash
# Import dashboard JSON
kubectl -n monitoring cp monitoring/grafana-dashboard-vault-health.json \
  grafana-pod:/var/lib/grafana/dashboards/

# Or manually in Grafana UI:
# 1. + → Import
# 2. Upload JSON from: 07-Infrastructure/monitoring/grafana-dashboard-vault-health.json
# 3. Select Prometheus datasource
# 4. Click Import

# Access Grafana
# https://grafana.mbergsch.com (via Cloudflare Tunnel)
```

### 6.3 Create Alert Rules

```bash
# Deploy AlertManager rules
kubectl -n monitoring apply -f monitoring/alert-rules.yaml

# Verify rules loaded
kubectl -n monitoring port-forward svc/prometheus 9090:9090 &
# Visit http://localhost:9090/alerts

pkill -f "port-forward"
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl -n hermes describe pod <pod-name>

# Check events
kubectl -n hermes get events --sort-by='.lastTimestamp'

# Check logs
kubectl -n hermes logs <pod-name> --previous  # If crashed
kubectl -n hermes logs <pod-name>             # Current

# Common issues:
# - ImagePullBackOff: Check Docker image in registry
# - Pending: Check PVC, node resources
# - CrashLoopBackOff: Check logs for application error
```

### Vault Files Not Syncing

```bash
# Check git-sync job logs
kubectl -n hermes logs job/git-sync-* -f

# Check SSH key
kubectl -n hermes get secret github-ssh-key -o jsonpath='{.data.ssh-privatekey}' | base64 -d

# Test git manually
kubectl -n hermes exec deployment/hermes-api -- \
  git -C /vault remote -v
```

### Cloudflare Tunnel Not Working

```bash
# Check tunnel status
kubectl -n hermes logs deployment/cloudflared

# Verify DNS resolves
nslookup hermes.mbergsch.com
nslookup vault.mbergsch.com

# Test direct access (without tunnel)
kubectl -n hermes port-forward svc/hermes-web-ui 8080:80 &
curl http://localhost:8080
pkill -f "port-forward"
```

### Backup Not Running

```bash
# Check CronJob schedule
kubectl -n hermes get cronjob backup-vault -o yaml | grep schedule

# Manually trigger backup job
kubectl -n hermes create job backup-manual --from=cronjob/backup-vault

# Check if backup file exists
kubectl -n hermes exec deployment/hermes-api -- \
  find /vault/backups -type f -name "*.tar.gz"
```

---

## Post-Deployment Checklist

- [ ] All pods running (hermes-api, hermes-web-ui, cloudflared)
- [ ] Health endpoint responding: /api/health
- [ ] Web UI accessible at https://hermes.mbergsch.com
- [ ] API accessible at https://vault.mbergsch.com/api
- [ ] Git-sync running hourly, vault synced with GitHub
- [ ] Backup CronJob running daily, backups created
- [ ] Prometheus scraping Hermes metrics
- [ ] Grafana dashboard showing vault health
- [ ] Recovery tested: backup restored successfully
- [ ] Documentation reviewed and stored in vault

---

## Maintenance Tasks

**Daily:**
- Monitor pod status: `kubectl -n hermes get pods`
- Check health endpoint: curl https://vault.mbergsch.com/api/health
- Review logs: `kubectl -n hermes logs -f deployment/hermes-api`

**Weekly:**
- Test backup recovery
- Review Grafana dashboard for anomalies
- Check disk usage: `df -h /vault`

**Monthly:**
- Review git commit history
- Validate backup retention policy
- Update dependencies (Docker images)
- Test failover (stop a pod, verify replica takes over)

---

## Reference: Component Mapping

| Component | Namespace | Type | Purpose |
|-----------|-----------|------|---------|
| hermes-api | hermes | Deployment | FastAPI backend |
| hermes-web-ui | hermes | Deployment | React frontend |
| cloudflared | hermes | Deployment | Tunnel daemon |
| git-sync | hermes | CronJob | Hourly git pulls |
| backup-vault | hermes | CronJob | Daily backups |
| hermes-web-ui | hermes | Service | Web UI access |
| hermes-api | hermes | Service | API access |
| hermes-ingress | hermes | Ingress | DNS routing |
| vault-storage | hermes | PVC | Vault data volume |
| github-ssh-key | hermes | Secret | Git credentials |

---

**Document Status:** Complete  
**Last Updated:** 2026-05-30  
**Next Review:** Nach Fertigstellung des k3s-Clusters
