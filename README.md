# Sentinel Monitor

Outil de supervision Linux en ligne de commande : surveille l'état d'une
machine (CPU / RAM / disque), scanne les ports locaux ouverts, et analyse
les logs d'authentification système pour détecter des tentatives de
brute-force SSH. Toute anomalie déclenche une alerte (console + fichier).

Projet personnel développé pour comprendre, de bout en bout, comment un
outil de monitoring/alerting type Datadog ou Wazuh fonctionne sous le
capot — collecte de métriques, parsing de logs, détection de patterns
d'attaque, dispatch d'alertes.

## Fonctionnalités

- **Monitoring système** : utilisation CPU, RAM et disque via `psutil`,
  avec seuil d'alerte configurable (80% par défaut)
- **Scan réseau local** : détection des ports TCP ouverts sur
  `127.0.0.1` (0–1023) via `socket`
- **Détection multi-distribution** : lecture automatique du bon fichier
  de log selon la distribution (`/etc/os-release`) — familles Debian
  (Ubuntu, Mint, Kali, Raspbian) et Fedora (RHEL, CentOS, Rocky, AlmaLinux)
- **Détection de brute-force SSH** : parsing des lignes `Failed
  password` dans `auth.log` / `secure`, regroupement par IP source,
  alerte si une IP dépasse un seuil de tentatives échouées
- **Alerting** : chaque anomalie (seuil système dépassé ou brute-force
  détecté) est affichée en CLI et journalisée dans `alerts.log` avec
  horodatage
- **Logging structuré** : niveaux différenciés (console INFO, console
  WARNING+, fichier complet avec fichier/ligne d'origine)

## Stack technique

- Python 3.12, bibliothèque standard (`socket`, `re`, `logging`,
  `pathlib`, `collections.Counter`) + `psutil` pour les métriques système
- Qualité de code : `flake8`, `mypy --strict`, `pyright`, `pylint`,
  `black` (voir `make lint`)
- `Makefile` pour l'installation (venv), l'exécution et le lint

## Structure

```
sentinel-monitor/
├── agent/
│   ├── monitor.py      # point d'entrée, métriques système
│   ├── networking.py   # scan de ports locaux
│   ├── logs.py         # détection distribution + lecture des logs
│   └── alert.py        # seuils + détection brute-force + dispatch alertes
├── requirements.txt
└── Makefile
```

## Installation et utilisation

```bash
make install   # crée le venv et installe les dépendances
make run       # lance le programme (nécessite sudo pour lire auth.log)
make lint      # flake8, mypy --strict, pyright, pylint, black
```

Ou manuellement :

```bash
pip install -r requirements.txt
sudo python agent/monitor.py
```

## Exemple de sortie

```
CPU: 12.4%
RAM: 4.192/1.823 Gb (43.5%)

DISK: 270.553/124.302 Gb (45.9%)
PORT: 22 is open
PORT: 80 is open

[ALERT] [2026-06-25 10:32:48] Possible SSH brute-force from 45.33.32.156: 5 failed login attempts
```

## Limites connues

- Lecture des logs nécessite des droits root (`/var/log/auth.log` n'est
  pas lisible par un utilisateur standard)
- Détection brute-force basée sur un pattern regex simple, pas de
  fenêtre temporelle (compte le total d'échecs, pas le débit/minute)
- Pas encore de persistance entre exécutions (chaque lancement repart
  de zéro sur l'analyse des logs)
- Pas de conteneurisation Docker ni de service systemd à ce stade —
  l'outil s'utilise en exécution manuelle ou via cron

## Pistes d'évolution

- Webhook (Discord/Slack) en plus de l'alerte fichier
- Service systemd pour exécution en tâche de fond continue
- Fenêtre glissante (ex: 5 tentatives en moins de 60s) plutôt qu'un
  compteur cumulatif
