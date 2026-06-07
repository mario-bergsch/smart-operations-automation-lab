# n8n Setup & Workflows für Hermes

## Status: Docker Compose aktiv

Alle Services laufen unter `docker-compose up -d`:
- **n8n**: http://localhost:5678
- **n8n Database**: postgresql://n8n:n8n-dev-password@localhost:5432/n8n
- **Hermes API**: http://localhost:8000
- **Web UI**: http://localhost:8080

## Step 1: n8n Initial Setup (UI)

1. Öffne http://localhost:5678
2. Erstelle Admin-Benutzer (Email/Password)
3. Melde dich an
4. Gehe zu Settings → API → API Keys
5. Generiere einen persönlichen API Key
6. Speichern für Workflow-Automation

## Step 2: Erste Workflows

### Workflow 1: Health Check (Hermes API)

**Trigger:** Every 5 minutes
**Nodes:**
1. **Trigger**: Cron Job (0 */5 * * * * = every 5 min)
2. **HTTP Request**: GET http://hermes-api:8000/api/health
3. **Condition**: Prüfe ob status === "ready"
4. **Notification**: Slack/Email bei Fehler

**Ziel:** Kontinuierliche Überwachung der API

### Workflow 2: Vault Backup

**Trigger:** Daily at 02:00 UTC
**Nodes:**
1. **Trigger**: Cron Job (0 2 * * *)
2. **HTTP Request**: GET /api/vault/search?q=*
3. **Save File**: Speichern als JSON
4. **Notification**: Status an Slack

**Ziel:** Tägliches Backup der Vault-Daten

### Workflow 3: Git Sync Monitor

**Trigger:** Every 30 minutes
**Nodes:**
1. **Trigger**: Cron Job
2. **HTTP Request**: GET /api/git/status
3. **Condition**: Prüfe auf pending commits
4. **HTTP Request**: POST /api/git/sync
5. **Notification**: Sync-Status

**Ziel:** Automatische Git Synchronisation überwachen

## Workflow Management

### Via Web UI (empfohlen für initial setup)
```bash
# n8n öffnen und manuell Workflows erstellen
open http://localhost:5678
```

### Via API (nach API Key generiert)
```bash
# API Key exportieren
export N8N_API_KEY="dein_api_key"

# Workflow erstellen
curl -X POST http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

## Workflows Exportieren/Importieren

n8n Workflows sind JSON:
```json
{
  "name": "Health Check",
  "nodes": [...],
  "connections": {...}
}
```

## Next Steps

1. **UI Setup**: http://localhost:5678 aufrufen und Admin-User erstellen
2. **API Key**: Settings → API Keys → neuen Key generieren
3. **First Workflow**: Health Check Workflow manuell erstellen oder via API deployen
4. **Slack Integration**: (Optional) Slack App für Notifications einrichten

## Troubleshooting

### n8n zeigt "Database error"
```bash
# Datenbank-Status prüfen
docker-compose logs hermes-n8n-db

# Datenbank neustarten
docker-compose restart hermes-n8n-db
```

### API Key funktioniert nicht
```bash
# n8n Logs prüfen
docker-compose logs hermes-n8n | grep -i api

# Container neustarten
docker-compose restart hermes-n8n
```

### Workflow lädt nicht
```bash
# Workflow-Datei validieren
curl http://localhost:5678/api/v1/workflows?filter={name:YourWorkflow} \
  -H "X-N8N-API-KEY: $N8N_API_KEY"
```
