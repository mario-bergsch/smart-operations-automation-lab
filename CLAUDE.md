# CLAUDE.md — Smart Operations Automation Lab

> Projektspezifisches Gedächtnis für Claude Code Sessions in diesem Repo.

## Projekt-Kontext

**Projekt:** Smart Operations Automation Lab
**Owner:** Mario Bergsch
**Status:** In Arbeit

## Ziel

Selbst gehostete Automatisierungsumgebung: Docker-Compose-Stack (n8n, Vault-API, Monitoring) und Kubernetes-Manifeste für k3s.

## Stand (belegt durch Dateien im Repo)

| Komponente | Status |
|------------|--------|
| Docker-Compose-Stack (7 Dienste) | Vorhanden |
| n8n-Workflows (3 JSON-Exporte) | Vorhanden |
| Kubernetes-Manifeste (hermes-api, hermes-web-ui, CronJobs) | Vorhanden |
| k3s-Cluster | In Arbeit — Betrieb nicht dokumentiert |
| n8n/Monitoring auf k3s | Geplant |

## Offene Aufgaben

- [ ] k3s-Cluster fertigstellen, Nachweis ablegen (`kubectl get nodes` / `kubectl get pods -A`)
- [ ] n8n-Manifest für k3s erstellen
- [ ] Ersten Workflow auf k3s testen und Ergebnis dokumentieren

## Arbeitsregeln

- Sprache: Deutsch (außer Code/YAML/Kubernetes-Manifeste)
- Nur eintragen, was im Repo belegt ist — keine Live-URLs, Uptime- oder Leistungszahlen ohne Nachweis
- Keine internen IPs, Benutzernamen, Tunnel-IDs oder lokalen Pfade committen
- Status-Labels: Vorhanden / In Arbeit / Geplant

## Session Changelog

2026-06-06 | CLAUDE.md erstellt
2026-10-31 | Bereinigung: Merge-Konflikte gelöst, unbelegte Claims entfernt, Secrets verpflichtend, interne IPs/IDs entfernt
