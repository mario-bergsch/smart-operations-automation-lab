# Slack Integration Setup

## 15 Minuten Setup

### Step 1: Slack Workspace erstellen (kostenlos)
```
https://slack.com/create
→ Workspace Name: "Hermes Lab"
→ E-Mail: smartops@mbergsch.com
```

### Step 2: Slack App erstellen

1. Gehe zu: https://api.slack.com/apps
2. Klick "Create New App" → "From Scratch"
3. App Name: **"Hermes Bot"**
4. Workspace: Select your workspace
5. **Create App**

### Step 3: Bot Token generieren

1. Im App Dashboard gehen zu: **Features → OAuth & Permissions**
2. Unter "Scopes" → "Bot Token Scopes" folgende hinzufügen:
   ```
   - chat:write
   - files:write
   - users:read
   ```
3. **Install to Workspace**
4. Klick "Allow"
5. **Copy Bot User OAuth Token** (beginnt mit `xoxb-...`)

### Step 4: Token speichern
```bash
# In .env datei:
SLACK_BOT_TOKEN=xoxb-XXXXX...

# Oder direkt in n8n:
Credentials → New → Slack Bot
→ Paste Token
```

### Step 5: Test im Slack
```
Schreibe in #general Channel:
@Hermes Bot test

Bot sollte antworten wenn Workflow aktiv ist
```

## In n8n verwenden

```
Workflow Node:
Type: Slack
Action: Send Message
Channel: #alerts
Message: Alert text
```

## Troubleshooting

### Bot nicht sichtbar
→ App Home → Add app to workspace

### Token Error
→ OAuth → Regenerate Token

---

**Danach:** Token in .env speichern
