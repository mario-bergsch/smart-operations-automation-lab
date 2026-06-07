# n8n Slack Integration Setup für Hermes Lab

Drei Optionen zur Slack-Integration in n8n. Wähle eine Methode.

---

## Option 1: Vollautomatisiert via Python (Empfohlen)

### Voraussetzungen
```bash
pip install selenium webdriver-manager
```

### Ausführung
```bash
cd 07-Infrastructure/docker
python3 setup-slack-automation.py
```

**Was passiert:**
- Python öffnet automatisch Chrome
- Erstellt Slack-Credential mit deinem Token
- Erstellt Test-Workflow
- Du kannst zusehen und weitere Anpassungen machen
- Browser bleibt offen zum Testen

---

## Option 2: Manuell via n8n UI (Schritt für Schritt)

### Schritt 1: n8n öffnen
```
http://localhost:5678
```

### Schritt 2: Slack-Credential erstellen

1. **Bottom Left:** Zahnrad-Icon klicken → "Credentials"
2. **Top Right:** "+ New" klicken
3. **Credentials Type:** Suche "Slack" → wähle "Slack API"
4. **Credential Name:** `Hermes Lab Slack Bot`
5. **Bot Token:** Paste your Slack Bot token:
   ```
   xoxb-YOUR-BOT-TOKEN-HERE
   ```
6. **Save** klicken

### Schritt 3: Test-Workflow erstellen

1. **Top Left:** "+ New" → "Workflow"
2. **Workflow Name:** `Hermes Lab - Slack Test`
3. **Canvas:** Double-Click auf leere Fläche
4. **Node hinzufügen:** Suche "Slack" → wähle "Slack" → "Send a message"
5. **Node konfigurieren:**
   - **Authentication:** Wähle "Hermes Lab Slack Bot"
   - **Channel:** `#general`
   - **Message:** 
     ```
     Test message from Hermes Lab 🚀
     
     If you see this, Slack integration is working!
     ```
6. **Save** klicken
7. **Workflow aktivieren:** Toggle "Active" am Top Right
8. **Test:** "Execute Workflow" klicken

---

## Option 3: Bash-Script (wenn n8n API konfiguriert)

```bash
cd 07-Infrastructure/docker
bash setup-slack-automation.sh
```

**Hinweis:** Benötigt n8n API-Authentication. Nur wenn du Zugang hast.

---

## Nach dem Setup

### Test in Slack
1. Öffne dein Slack Workspace
2. Channel `#general`
3. Deine Test-Nachricht sollte dort sein
4. Falls nicht: Check n8n Workflow Logs

### Nächste Schritte
- Weitere Workflows mit Slack-Notifications erstellen
- Email-Alerts konfigurieren
- Prometheus/Grafana Monitoring aktivieren

---

## Troubleshooting

### Python-Script startet nicht
```bash
# Abhängigkeiten installieren
pip install selenium webdriver-manager

# Chrome/Chromium muss installiert sein
# macOS: brew install chromium
# Linux: apt-get install chromium-browser
# Windows: Kommt mit Chrome
```

### Slack Token nicht gültig
- Token überprüfen: `xoxb-11238909308435...`
- Im Slack Workspace eingeloggt sein
- Bot in Channel einladen: `/invite @Hermes Bot` in #general

### n8n Workflow nicht aktiviert
- Im UI kontrollieren, ob Toggle "Active" an ist
- Credentials sind verbunden?

---

## Konfiguration ändern

Falls du einen anderen Token oder Channel brauchst, editiere:
- **setup-slack-automation.py:** Zeilen 13-15
- **setup-slack-automation.sh:** Zeilen 14-17

Oder verwende Option 2 (manuell) für maximale Flexibilität.
