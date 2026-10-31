---
type: guide
title: Smart Operations Lab - Deployment Guide
created: 2026-06-07
status: complete
---

# Deployment Guide - Smart Operations Lab

**Schritt-für-Schritt Anleitung für Cluster-Setup**

---

## Quick Start (30 Min)

### Voraussetzungen
- Proxmox Host (8+ cores, 32GB RAM)
- 2 Ubuntu 22.04 LTS VMs (Master + Worker)
- GitHub Account + Cloudflare Account
- kubectl, helm, ssh

### Setup

```bash
# 1. SSH Config
cat >> ~/.ssh/config <<EOF
Host k3s-master
    HostName <MASTER-IP>
    User <USER>
    IdentityFile ~/.ssh/id_ed25519
EOF

# 2. Master k3s
ssh k3s-master
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
TOKEN=$(sudo cat /var/lib/rancher/k3s/server/node-token)

# 3. Worker k3s
ssh k3s-worker
curl -sfL https://get.k3s.io | K3S_URL=https://<MASTER-IP>:6443 \
  K3S_TOKEN=$TOKEN sh -

# 4. Deploy Services
ssh k3s-master "kubectl apply -f /tmp/kubernetes/" 

# 5. Cloudflare Tunnel
# See detailed instructions below
```

---

## Phase 1: Infrastructure Setup

### Network Configuration

```bash
# Master: /etc/netplan/00-installer-config.yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - <MASTER-IP>/24
      gateway4: <GATEWAY-IP>
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]

# Apply
sudo netplan apply
```

### Resource Scaling (Optional)

```bash
# Expand Storage on Master
ssh k3s-master

# Check current size
lsblk

# Expand with LVM
sudo sgdisk -e /dev/sda
sudo parted /dev/sda resizepart 3 100%
sudo pvresize /dev/sda3
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv
```

---

## Phase 2: k3s Cluster

### Master Installation

```bash
ssh k3s-master

curl -sfL https://get.k3s.io | sh -s - \
  --write-kubeconfig-mode 644 \
  --flannel-backend=vxlan \
  --storage-driver=local

sudo systemctl status k3s
TOKEN=$(sudo cat /var/lib/rancher/k3s/server/node-token)
```

### Worker Installation

```bash
ssh k3s-worker

curl -sfL https://get.k3s.io | K3S_URL=https://<MASTER-IP>:6443 \
  K3S_TOKEN=<paste-token> sh -

sudo systemctl status k3s-agent
```

### Verify Cluster

```bash
ssh k3s-master

# Setup kubectl for mario user
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown mario:mario ~/.kube/config

export KUBECONFIG=~/.kube/config
kubectl get nodes
kubectl get pods -A
```

---

## Phase 3: Core Services

### Namespaces

```bash
kubectl create namespace ingress-nginx
kubectl create namespace monitoring
kubectl create namespace logging
kubectl create namespace hermes
kubectl create namespace automation
```

### Storage

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: vault-storage-pvc
  namespace: hermes
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 50Gi
EOF
```

### Helm Setup

```bash
helm repo add stable https://charts.helm.sh/stable
helm repo add jetstack https://charts.jetstack.io
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### cert-manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.crds.yaml

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.13.0
```

### Deploy Application Manifests

```bash
# Copy manifests
scp -r 07-Infrastructure/kubernetes k3s-master:/tmp/

# Deploy on master
ssh k3s-master

export KUBECONFIG=~/.kube/config

kubectl apply -f /tmp/kubernetes/namespace.yaml
kubectl apply -f /tmp/kubernetes/pvc-vault-storage.yaml
kubectl apply -f /tmp/kubernetes/hermes-web-ui/
kubectl apply -f /tmp/kubernetes/hermes-api/
kubectl apply -f /tmp/kubernetes/cron-jobs/

# Verify
kubectl get pods -n hermes
kubectl get pvc -A
```

---

## Phase 4: Monitoring Stack

### Prometheus + Grafana

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.retention=7d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=5Gi

# Verify
kubectl get pods -n monitoring
kubectl get svc -n monitoring
```

### Access Grafana

```bash
# Temporary access
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Then visit http://localhost:3000
# Default: admin / prom-operator
```

### Loki Logging (Optional)

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install loki grafana/loki-stack \
  --namespace logging \
  --create-namespace \
  --set loki.persistence.enabled=true \
  --set loki.persistence.size=5Gi
```

---

## Phase 5: External Access

### Cloudflare Tunnel

```bash
ssh k3s-master

# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/download/2024.6.0/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Login and create tunnel (Cloudflare dashboard)
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create smart-operations-lab

# Get tunnel ID
cloudflared tunnel list
```

### Tunnel Configuration

```bash
# Create config
sudo tee /etc/cloudflared/config.yml > /dev/null <<EOF
tunnel: <your-tunnel-id>
credentials-file: ~/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: ai.mbergsch.com
    service: http://10.43.166.176:80
  - hostname: n8n.mbergsch.com
    service: http://<MASTER-IP>:5678
  - hostname: grafana.mbergsch.com
    service: http://<MASTER-IP>:3000
  - hostname: prometheus.mbergsch.com
    service: http://<MASTER-IP>:9090
  - hostname: loki.mbergsch.com
    service: http://<MASTER-IP>:3100
  - hostname: vault-api.mbergsch.com
    service: http://<MASTER-IP>:8000
  - service: http_status:404
EOF

# Start service
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
sudo systemctl status cloudflared
```

### DNS Setup (Cloudflare Dashboard)

1. Create CNAME records pointing to tunnel:
   - `ai.mbergsch.com`
   - `n8n.mbergsch.com`
   - `grafana.mbergsch.com`
   - `prometheus.mbergsch.com`
   - `loki.mbergsch.com`
   - `vault-api.mbergsch.com`

2. Enable Cloudflare proxy (orange cloud)

---

## Troubleshooting

### Pod Issues

```bash
# Check logs
kubectl logs -n hermes [pod-name]
kubectl describe pod -n hermes [pod-name]

# Check events
kubectl get events -n hermes --sort-by='.lastTimestamp'

# High memory/cpu
kubectl top nodes
kubectl top pods -A
```

### Storage Issues

```bash
# Check PVC status
kubectl get pvc -A
kubectl describe pvc -n hermes vault-storage-pvc

# Check disk usage
df -h /var/lib/rancher/k3s/storage
du -sh /var/lib/rancher/k3s/storage/*
```

### Cloudflare Issues

```bash
# Check tunnel
sudo systemctl status cloudflared
sudo journalctl -u cloudflared -f

# Verify config
sudo cat /etc/cloudflared/config.yml
cloudflared tunnel list

# Test connectivity
curl https://your-service.mbergsch.com
```

---

## Maintenance

```bash
# Weekly: Check health
kubectl get nodes
kubectl get pods -A --field-selector=status.phase!=Running

# Monthly: Backup
sudo k3s etcd-snapshot save
ls /var/lib/rancher/k3s/server/db/snapshots/

# Quarterly: Update k3s
sudo systemctl stop k3s
curl -sfL https://get.k3s.io | sh -
sudo systemctl start k3s
```

---

**Last Updated:** 2026-06-07  
**Status:** Anleitung (Betrieb nicht im Repo dokumentiert)
