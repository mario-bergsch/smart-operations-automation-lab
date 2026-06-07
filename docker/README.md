# Hermes Local Lab - Docker Compose Setup

Complete local development environment for Hermes Vault with n8n workflow automation.

## Quick Start

```bash
# Start all services
make up

# Check health
make health

# View logs
make logs

# Stop services
make down
```

## Services

### Core Services
- **hermes-api** (8000): FastAPI backend for vault operations
- **hermes-web-ui** (8080): Web interface for vault access
- **n8n** (5678): Workflow automation platform
- **PostgreSQL** (5432): Database for n8n workflows

### Volumes
- `vault-data`: Vault files
- `n8n-data`: n8n configuration and execution data
- `n8n-db-data`: PostgreSQL data

## Setup Guide

### Step 1: Start Services
```bash
cd 07-Infrastructure/docker
make up
make health
```

### Step 2: n8n Initial Setup
1. Open http://localhost:5678
2. Create admin user (email/password)
3. Login and go to Settings → API
4. Generate API key for workflow automation

### Step 3: Import Workflows
1. In n8n, go to File → Import
2. Select workflow JSON from `workflows/` directory
3. Save and activate each workflow

## Available Commands

```bash
make help          # Show all available commands
make up            # Start services
make down          # Stop services
make logs          # View all logs
make status        # Show service status
make health        # Health check all services
make test          # Run API tests
make clean         # Remove containers and volumes
```

## Workflows

### 1. Health Check (Every 5 minutes)
- Monitors Hermes API health status
- Checks vault and git accessibility

### 2. Vault Backup (Daily 02:00 UTC)
- Exports all vault data
- Creates timestamped backup

### 3. Git Sync Monitor (Every 30 minutes)
- Checks git synchronization status
- Triggers sync if needed

## Directory Structure

```
07-Infrastructure/docker/
├── docker-compose.yml
├── Makefile
├── README.md (this file)
├── N8N-SETUP.md
├── VAULT-API-INTEGRATION.md
├── hermes-api/
├── hermes-web-ui/
└── workflows/
    ├── 1-health-check.json
    ├── 2-vault-backup.json
    └── 3-git-sync-monitor.json
```

## API Endpoints

### Health
```
GET /api/health
Response: { status, vault_accessible, git_accessible, vault_path }
```

### Search
```
GET /api/vault/search?q={query}
Response: { results: [...] }
```

## Troubleshooting

### Services not starting
```bash
make clean
make up
```

### API not responding
```bash
make logs-api
curl http://localhost:8000/api/health
```

### n8n issues
```bash
make logs-n8n
docker-compose restart hermes-n8n
```

## Documentation

- [[N8N-SETUP.md]] - n8n setup guide
- [[VAULT-API-INTEGRATION.md]] - API integration details
- [[01-Daily/2026-05-30.md]] - Session notes
