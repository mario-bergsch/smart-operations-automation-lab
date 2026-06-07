# Vault API Integration für n8n Workflows

## Übersicht

Die Hermes API bietet RESTful Endpoints für Vault-Operationen. n8n kann diese nutzen um automatisierte Workflows zu erstellen.

## API Endpoints

### Health & Status
```http
GET /api/health
```
Response:
```json
{
  "status": "ready",
  "vault_accessible": true,
  "git_accessible": false,
  "vault_path": "/vault"
}
```

### Vault Search
```http
GET /api/vault/search?q={query}
```
Example:
```bash
curl "http://localhost:8000/api/vault/search?q=daily"
```

### Git Status
```http
GET /api/git/status
```

### Git Sync (Trigger)
```http
POST /api/git/sync
```

## n8n Integration

### Setup HTTP Request Node

1. **Öffne n8n Workflow Editor**
   - URL: http://localhost:5678

2. **Füge HTTP Request Node hinzu**
   - Node Type: "HTTP Request"
   - Method: GET oder POST (je nach Endpoint)
   - URL: `http://hermes-api:8000/api/{endpoint}`
   - Authentication: None (lokal, keine Auth nötig)

3. **Beispiel: Health Check**
   ```
   Method: GET
   URL: http://hermes-api:8000/api/health
   ```

## Workflow-Beispiele

### Workflow 1: Health Check mit Conditional Logic

```
Trigger (Cron) 
  ↓
HTTP GET /api/health
  ↓
IF status == "ready"
  ├→ Log "API is healthy"
  └→ POST Alert "API is down"
```

### Workflow 2: Daily Vault Backup

```
Trigger (Daily 02:00 UTC)
  ↓
HTTP GET /api/vault/search?q=*
  ↓
Code Node: Transform to backup format
  ↓
HTTP POST /api/vault/backup
  ↓
Save File to disk
  ↓
Notification: Backup completed
```

### Workflow 3: Git Sync Monitor

```
Trigger (Every 30 min)
  ↓
HTTP GET /api/health (check git_accessible)
  ↓
IF git_accessible == false
  ├→ HTTP POST /api/git/sync
  └→ Wait 5 seconds
  ↓
Notification: Sync status
```

## API Response Handling

### JSON Extraction in n8n

```javascript
// In Code Node:
return {
  timestamp: new Date().toISOString(),
  apiStatus: $json.status,
  vaultOk: $json.vault_accessible,
  gitOk: $json.git_accessible
}
```

## Testing

### Via curl (direct API test)
```bash
# Health check
curl http://localhost:8000/api/health

# Search vault
curl "http://localhost:8000/api/vault/search?q=test"
```

### Via n8n Test Node
1. Add HTTP Request node
2. Click "Test" button
3. View response in right panel

## Troubleshooting

### 503 API Unavailable
```bash
# Check if API is running
docker-compose ps hermes-api-local

# Check logs
docker-compose logs hermes-api-local

# Restart if needed
docker-compose restart hermes-api-local
```

### Connection Refused
- Ensure docker-compose services running: `make up`
- Verify port 8000 is accessible: `curl localhost:8000/api/health`

## Resources

- n8n Docs: https://docs.n8n.io
- HTTP Request Node: https://docs.n8n.io/integrations/built-in/core-nodes/n8n-nodes-base.httprequest/
