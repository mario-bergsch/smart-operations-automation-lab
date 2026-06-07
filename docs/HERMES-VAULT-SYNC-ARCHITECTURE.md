---
type: architecture
title: Hermes Vault Synchronization Architecture
date: 2026-05-30
status: complete
---

# Hermes Vault Synchronization Architecture

**Purpose:** Document the data flow, conflict resolution, and disaster recovery strategy for Hermes Vault across Mac (V1/V2) and k3s (server).

---

## System Overview

Data sync flows from Mac (edits) → GitHub (source of truth) → k3s (read-only replica) → Web UI (users).

**Three Sources:**
- Mac local vault: where humans edit
- GitHub: authoritative history and central sync point
- k3s cluster: read-only copy served via web UI and API

---

## Data Flow Paths

### Path 1: Mac → GitHub → k3s (Primary)

Mac user edits vault, commits to GitHub, k3s pulls hourly.

**Latency:** 0-60 seconds (STARTUP-SYNC immediate, k3s sync within 1 hour max)

**Process:**
1. User edits file in Obsidian on Mac
2. STARTUP-SYNC triggered: git add → commit → push
3. GitHub receives commit
4. k3s CronJob runs hourly: git fetch origin → git reset --hard
5. Web UI serves updated files

---

### Path 2: k3s → Backup → Recovery

Daily automatic backups protect against data loss.

**Backup CronJob (daily at 02:00 UTC):**
- tar -czf vault-YYYY-MM-DD.tar.gz /vault
- Excludes large .git/objects directory
- Stores in /vault/backups/ with 30-day rotation

**Recovery:**
- Extract backup: tar -xzf backups/vault-2026-05-31.tar.gz
- Verify git history: git log --oneline | head -20
- Or recover from GitHub: git reset --hard origin/main

**Recovery Time:** 5-15 minutes

---

## Conflict Resolution Strategy

### Scenario 1: Offline Mac, Remote Changes in GitHub

**Problem:** Mac A offline, User on Mac B pushes to GitHub, Mac A comes online with stale vault

**Resolution:**
- k3s pulls from GitHub (read-only, no conflicts possible)
- When Mac A comes online, STARTUP-SYNC detects it's behind
- User chooses: merge (git pull) or reset (git reset --hard origin/main)
- After resolve: git push origin main

---

### Scenario 2: Concurrent Edits (Both Mac A & B)

**Problem:** Both Macs edit same file, both try to push

**Solution:**
- First push succeeds
- Second push rejected: "not fast-forward"
- Second Mac pulls first: git fetch → git pull --rebase origin main
- If conflicts, manual merge required
- After resolve: git push origin main

---

### Scenario 3: k3s Cannot Reach GitHub

**Problem:** SSH key expired, network down, or GitHub unavailable

**Safeguards:**
- CronJob retries on next hour (within 1 hour lag max)
- Health check alerts if sync fails 3+ times
- Manual fix: update SSH key or resolve network
- Vault continues serving from last synced state (read-only safe)

---

## Key Design Principles

1. **Read-Only on k3s:** Only git fetch + git reset --hard, never commits
2. **GitHub as Source of Truth:** Mac is edit source, GitHub is history source
3. **No Merge Conflicts at k3s:** Reset strategy prevents conflicts
4. **Human Decision-Making:** Conflict resolution happens on Mac (where human can decide)
5. **Backup Independence:** Backups don't depend on git history (tar.gz + full extraction)

---

## Monitoring & Alerting

**Metrics tracked:**
- Last successful git-sync (alerting if >2 hours old)
- Last backup (alerting if >48 hours old)
- Vault health check (api/health endpoint)
- PVC disk usage (alerting if >80% full)

**Alert Rules:**
- HermesGitSyncFailed: Fires if sync fails 3 times in a row
- HermesBackupFailed: Fires if no backup for 48 hours
- HermesVaultHealthBad: Fires if api/health returns vault_accessible: false
- HermesPodCrashing: Fires if pod restart rate increases

---

**Status:** Complete | **Version:** 1.0
