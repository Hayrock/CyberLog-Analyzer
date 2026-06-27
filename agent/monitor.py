"""
Module de monitoring système.

Contient des fonctions de vérification CPU, RAM et disque.
"""

import logging
import psutil
from networking import check_port
from logs import read_log, detect_distrib
from alert import check_threshold, detect_ssh_bruteforce

logger = logging.getLogger(__name__)


def check_cpu(threshold: float) -> str:
    """
    Vérifie l'utilisation CPU et retourne un message formaté.

    Args:
        threshold (float): seuil d'alerte en pourcentage.

    Returns:
        str: état du CPU avec éventuelle alerte.
    """
    percent = psutil.cpu_percent(interval=1, percpu=False)
    check_threshold("CPU", percent, threshold)
    alert = "HIGH !" if percent > threshold else ""
    return f"CPU: {percent}% {alert}"


def check_ram(threshold: float) -> str:
    """
    Vérifie l'utilisation de la RAM et retourne un message formaté.

    Args:
        threshold (float): seuil d'alerte en pourcentage.

    Returns:
        str: état de la RAM avec éventuelle alerte.
    """
    total, _, percent, used, _, _, _, _, _, _, _ = psutil.virtual_memory()

    total_gb: float = total / 1_000_000_000
    used_gb: float = used / 1_000_000_000

    check_threshold("RAM", percent, threshold)
    alert = "HIGH !" if percent > threshold else ""
    return f"RAM: {total_gb:.3f}/{used_gb:.3f} Gb ({percent}%) {alert}"


def check_disk(threshold: float) -> str:
    """
    Vérifie l'utilisation du disque et retourne un message formaté.

    Args:
        threshold (float): seuil d'alerte en pourcentage.

    Returns:
        str: état du disque avec éventuelle alerte.
    """
    total, used, _, percent = psutil.disk_usage("/")

    total_gb: float = total / 1_000_000_000
    used_gb: float = used / 1_000_000_000

    check_threshold("DISK", percent, threshold)
    alert = "HIGH !" if percent > threshold else ""
    return f"DISK: {total_gb:.3f}/{used_gb} Gb ({percent}%) {alert}"


def main() -> None:
    """
    Point d'entrée principal du programme.

    Affiche l'état CPU, RAM et disque, vérifie les ports réseau,
    puis analyse les logs d'authentification selon la distribution
    détectée pour repérer d'éventuelles tentatives de brute-force SSH.
    Toute anomalie déclenche une alerte (CLI + fichier).
    """
    print(check_cpu(80.0))
    print(check_ram(80.0))
    print()

    print(check_disk(80.0))
    check_port()
    print()

    try:
        distrib_func = detect_distrib()
        log_lines = read_log(distrib_func)
        detect_ssh_bruteforce(log_lines)
    except (RuntimeError, PermissionError, FileNotFoundError) as exc:
        logger.error("Log analysis skipped: %s", exc)


if __name__ == "__main__":
    main()
