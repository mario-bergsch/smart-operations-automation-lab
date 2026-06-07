---
type: operations
title: Hermes Vault Operations Guide
date: 2026-05-30
status: complete
---

# Hermes Vault Operations Guide

**Purpose:** Day-2 operations, health monitoring, scaling procedures, and runbooks for Hermes Vault k3s deployment.

---

## Daily Operations

### Health Checks (Daily)

```bash
# Check pod status
kubectl -n hermes get pods -o wide

# Check services
kubectl -n hermes get svc

# Check ingress
kubectl -n hermes get ingress

# Check storage
kubectl -n hermes get pvc

# All-in-one status
kubectl -n hermes get all
```

**Expected state:**
- All pods: READY 1/1, STATUS Running
- Services: All CLUSTER-IP assigned
- Ingress: All hosts have valid TLS certificates
- PVC: All BOUND

### API Health Endpoint

```bash
# Check health via API
curl https://vault.mbergsch.com/api/health

# Expected response:
{
  "status": "healthy",
  "vault_accessible": true,
  "git_status": "synced",
  "timestamp": "2026-06-01T10:30:45Z"
}
```

### Log Review

```bash
# Current logs from API
kubectl -n hermes logs deployment/hermes-api --tail=50

# Current logs from Web UI
kubectl -n hermes logs deployment/hermes-web-ui --tail=50

# Previous logs (if pod crashed)
kubectl -n hermes logs deployment/hermes-api --previous

# Follow logs in real-time
kubectl -n hermes logs -f deployment/hermes-api
```

---

## Monitoring & Alerts

### Grafana Dashboard

1. Open Grafana: https://grafana.mbergsch.com
2. Navigate to: Dashboards → Hermes Vault Health
3. Monitor:
   - API Request Rate (requests/sec)
   - Request Status Distribution (2xx/4xx/5xx)
   - Response Time (p95, p99)
   - Vault file count / size

### Alert Conditions

| Alert | Threshold | Action |
|-------|-----------|--------|
| HermesAPIDown | No response for 5 minutes | Check pod logs, restart if needed |
| HermesGitSyncFailed | Failed 3 times in a row | Review SSH key, GitHub access |
| HermesBackupFailed | No backup in 48 hours | Manually trigger backup, check storage |
| HermesPVCFull | Usage >90% | Expand PVC or cleanup old backups |
| HermesPodCrashing | Restart rate >0 in 1 hour | Review logs, check resource limits |

---

## Scaling Operations

### Increase Web UI Replicas

```bash
# Scale to 3 replicas
kubectl -n hermes scale deployment hermes-web-ui --replicas=3

# Monitor rollout
kubectl -n hermes rollout status deployment/hermes-web-ui

# Revert if issues
kubectl -n hermes rollout undo deployment/hermes-web-ui
```

### Increase API Backend Replicas

```bash
# Scale API to 3 replicas
kubectl -n hermes scale deployment hermes-api --replicas=3

# Verify new pods are healthy
kubectl -n hermes logs deployment/hermes-api --tail=20 -f
```

### Increase Storage

```bash
# Check current size
kubectl -n hermes get pvc vault-storage -o jsonpath='{.spec.resources.requests.storage}'

# Expand to 100Gi (if storage class supports expansion)
kubectl -n hermes patch pvc vault-storage -p '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}'

# Verify expansion
kubectl -n hermes get pvc vault-storage
```

---

## Backup & Recovery

### Manual Backup

```bash
# Trigger immediate backup
kubectl -n hermes create job backup-manual-$(date +%s) --from=cronjob/backup-vault

# Check if backup was created
kubectl -n hermes exec deployment/hermes-api -- \
  ls -lh /vault/backups/ | tail -5
```

### Recovery from Backup

```bash
# List available backups
kubectl -n hermes exec deployment/hermes-api -- ls -lh /vault/backups/

# Restore from specific backup (example)
kubectl -n hermes exec deployment/hermes-api -- sh -c \
  'cd /vault && tar -xzf /vault/backups/vault-2026-05-31.tar.gz --strip-components=1'

# Verify restoration
kubectl -n hermes exec deployment/hermes-api -- git -C /vault log --oneline | head -10

# If corrupted, restore from GitHub instead
kubectl -n hermes exec deployment/hermes-api -- sh -c \
  'cd /vault && git reset --hard origin/main'
```

### Complete Disaster Recovery

```bash
# If PVC is completely lost:

# 1. Delete corrupted PVC
kubectl -n hermes delete pvc vault-storage

# 2. Recreate PVC (will be empty)
kubectl -n hermes apply -f kubernetes/pvc-vault-storage.yaml

# 3. Restart API pod (will mount new PVC)
kubectl -n hermes rollout restart deployment/hermes-api

# 4. Populate from GitHub
kubectl -n hermes exec -it deployment/hermes-api -- sh
# Inside pod shell:
cd /vault
git clone --depth 1 git@github.com:user/hermes-master.git .
git log --oneline | head -5

# 5. Verify
curl https://hermes.mbergsch.com
```

---

## Troubleshooting Runbooks

### Issue: API Pod CrashLoopBackOff

```bash
# 1. Get recent logs
kubectl -n hermes logs deployment/hermes-api --previous

# 2. Describe pod for events
kubectl -n hermes describe pod -l app=hermes-api

# 3. Check resource limits (if OOMKilled)
kubectl -n hermes set resources deployment/hermes-api \
  --requests=memory=512Mi,cpu=200m --limits=memory=1Gi,cpu=500m

# 4. Restart deployment
kubectl -n hermes rollout restart deployment/hermes-api
```

### Issue: Git-Sync CronJob Not Running

```bash
# 1. Verify CronJob exists
kubectl -n hermes get cronjob git-sync

# 2. Check schedule
kubectl -n hermes get cronjob git-sync -o jsonpath='{.spec.schedule}'

# 3. Manually trigger to test
kubectl -n hermes create job git-sync-test-$(date +%s) --from=cronjob/git-sync
kubectl -n hermes logs job/git-sync-test-* -f
```

### Issue: PVC Running Out of Space

```bash
# 1. Check usage
kubectl -n hermes exec deployment/hermes-api -- df -h /vault

# 2. Cleanup old backups (>30 days)
kubectl -n hermes exec deployment/hermes-api -- sh -c \
  'find /vault/backups -name "*.tar.gz" -mtime +30 -delete'

# 3. If still full: Expand PVC
kubectl -n hermes patch pvc vault-storage \
  -p '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}'
```

### Issue: DNS Not Resolving

```bash
# 1. Verify DNS
nslookup hermes.mbergsch.com
nslookup vault.mbergsch.com

# 2. Check Cloudflare tunnel is running
kubectl -n hermes get pods -l app=cloudflared

# 3. Check tunnel logs
kubectl -n hermes logs deployment/cloudflared -f

# 4. Verify ingress
kubectl -n hermes get ingress
```

---

## Maintenance Schedule

### Weekly

```bash
# 1. Review backup count (should be ~7)
kubectl -n hermes exec deployment/hermes-api -- \
  find /vault/backups -type f -name "*.tar.gz" | wc -l

# 2. Check disk usage
kubectl -n hermes exec deployment/hermes-api -- du -sh /vault

# 3. Review pod restart count
kubectl -n hermes get pods -o json | \
  jq '.items[] | {name: .metadata.name, restarts: .status.containerStatuses[0].restartCount}'
```

### Monthly

```bash
# 1. Test recovery from backup
tar -xzf /vault/backups/vault-2026-05-01.tar.gz -C /tmp/restore-test

# 2. Review Grafana trends
# Check for performance anomalies

# 3. Verify git history still intact
git -C /tmp/restore-test/vault log --oneline | head -20
```

---

**Status:** Complete | **Last Updated:** 2026-05-30 | **Version:** 1.0
