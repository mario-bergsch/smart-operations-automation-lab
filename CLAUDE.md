# CLAUDE.md — Smart Operations Automation Lab

> Projektspezifisches Gedächtnis für Claude Code Sessions in diesem Repo.

## Projekt-Kontext

**Projekt:** Smart Operations Automation Lab
**Owner:** Mario Bergsch
**Status:** Abgeschlossen (Juni 2026), nicht mehr in Entwicklung

## Ziel

Selbst gehostete Automatisierungsumgebung: Docker-Compose-Stack (n8n, Vault-API, Monitoring) und Kubernetes-Manifeste für k3s.

## Stand (belegt durch Dateien im Repo)

| Komponente | Status |
|------------|--------|
| Docker-Compose-Stack (7 Dienste) | Vorhanden |
| n8n-Workflows (3 JSON-Exporte) | Vorhanden |
| Kubernetes-Manifeste (hermes-api, hermes-web-ui, CronJobs) | Vorhanden |
| k3s-Cluster | Nicht fertiggestellt |
| n8n/Monitoring auf k3s | Nicht umgesetzt |

## Offene Aufgaben

Keine — Projekt abgeschlossen.



## Arbeitsregeln

- Sprache: Deutsch (außer Code/YAML/Kubernetes-Manifeste)
- Nur eintragen, was im Repo belegt ist — keine Live-URLs, Uptime- oder Leistungszahlen ohne Nachweis
- Keine internen IPs, Benutzernamen, Tunnel-IDs oder lokalen Pfade committen
- Status-Labels: Vorhanden / Nicht fertiggestellt / Nicht umgesetzt

## Session Changelog

2026-06-06 | CLAUDE.md erstellt
2026-10-31 | Bereinigung: Merge-Konflikte gelöst, unbelegte Claims entfernt, Secrets verpflichtend, interne IPs/IDs entfernt
