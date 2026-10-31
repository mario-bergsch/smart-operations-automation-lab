#!/bin/bash
# Update Cloudflare Tunnel Config für Smart Operations Lab
# Führe auf k3s-master aus mit: bash /tmp/update-cloudflare-config.sh

set -e

# Werte per Umgebungsvariable setzen, z. B.:
#   TUNNEL_ID=... MASTER_IP=... bash update-cloudflare-config.sh
TUNNEL_ID="${TUNNEL_ID:?TUNNEL_ID setzen (cloudflared tunnel list)}"
MASTER_IP="${MASTER_IP:?MASTER_IP setzen}"
CREDS_FILE="${CREDS_FILE:-$HOME/.cloudflared/${TUNNEL_ID}.json}"
CONFIG_FILE="/etc/cloudflared/config.yml"

echo "🔧 Updating Cloudflare Tunnel Configuration..."

# Backup
sudo cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%s)"
echo "✅ Backup erstellt"

# Neue Config
sudo tee "$CONFIG_FILE" > /dev/null <<EOF
tunnel: $TUNNEL_ID
credentials-file: $CREDS_FILE

ingress:
  # AI Services
  - hostname: ai.mbergsch.com
    service: http://10.43.166.176:80

  # Automation (n8n)
  - hostname: n8n.mbergsch.com
    service: http://${MASTER_IP}:5678

  # Monitoring (Grafana)
  - hostname: grafana.mbergsch.com
    service: http://${MASTER_IP}:3000

  # Monitoring (Prometheus)
  - hostname: prometheus.mbergsch.com
    service: http://${MASTER_IP}:9090

  # Logging (Loki)
  - hostname: loki.mbergsch.com
    service: http://${MASTER_IP}:3100

  # Hermes Vault API
  - hostname: vault-api.mbergsch.com
    service: http://${MASTER_IP}:8000

  # Default fallback
  - service: http_status:404
EOF

echo "✅ Config aktualisiert"
echo ""
echo "📋 Neue Services:"
echo "   - prometheus.mbergsch.com → ${MASTER_IP}:9090"
echo "   - loki.mbergsch.com → ${MASTER_IP}:3100"
echo "   - vault-api.mbergsch.com → ${MASTER_IP}:8000"
echo ""
echo "🔄 Restarting cloudflared..."
sudo systemctl restart cloudflared

sleep 2

# Verify
if sudo systemctl is-active cloudflared > /dev/null; then
    echo "✅ cloudflared läuft"
else
    echo "❌ cloudflared nicht aktiv - Fehler prüfen:"
    sudo systemctl status cloudflared
fi

echo ""
echo "🎉 Update abgeschlossen!"
echo ""
echo "Teste die Services:"
echo "  curl https://prometheus.mbergsch.com"
echo "  curl https://loki.mbergsch.com"
echo "  curl https://vault-api.mbergsch.com"
