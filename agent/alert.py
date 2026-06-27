"""
Alerting module.

Provides:
- Brute-force SSH detection by parsing auth log lines
- A simple alert dispatcher that prints to the console (CLI)
  and appends every alert to a persistent alert log file.

This module is intentionally dependency-free (standard library only)
so it stays easy to read, test, and extend.
"""

import re
import logging
from collections import Counter
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# Fichier où chaque alerte est ajoutée (une ligne par alerte),
# en plus de l'affichage console. Chemin relatif au module pour
# fonctionner peu importe le répertoire de lancement.
ALERT_FILE_PATH = Path(__file__).resolve().parent / "alerts.log"

# Une ligne "Failed password ... from <IP> ..." dans auth.log ressemble à :
# "Jun 25 10:32:11 host sshd[1234]:
# Failed password for root from 10.0.0.5 port 51514 ssh2"
FAILED_SSH_PATTERN = re.compile(
    r"Failed password for (?:invalid user )?\S+ "
    r"from (?P<ip>\d{1,3}(?:\.\d{1,3}){3})"
)


def send_alert(message: str) -> None:
    """
    Dispatch an alert through every configured channel.

    Currently:
        - CLI: printed immediately with a clear [ALERT] prefix
        - File: appended to alerts.log with a timestamp

    Args:
        message (str): human-readable alert description.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"

    print(f"[ALERT] {line}")
    logger.warning(message)

    try:
        with open(ALERT_FILE_PATH, "a", encoding="utf-8") as file:
            file.write(line + "\n")
    except OSError as exc:
        logger.error("Could not write to alert file: %s", exc)


def check_threshold(label: str, value: float, threshold: float) -> None:
    """
    Raise an alert if a metric exceeds its threshold.

    Args:
        label (str): metric name, e.g. "CPU", "RAM", "DISK".
        value (float): current measured value (percentage).
        threshold (float): alert threshold (percentage).
    """
    text1 = f"{label} usage critical: "
    if value > threshold:
        send_alert(text1 + f"{value}% (threshold: {threshold}%)")


def detect_ssh_bruteforce(
    log_lines: list[str], max_attempts: int = 4
) -> dict[str, int]:
    """
    Detect repeated failed SSH login attempts per source IP.

    Args:
        log_lines (list[str]): lines from an auth log (auth.log / secure).
        max_attempts (int): number of failures from a single IP before
            it is considered a brute-force attempt.

    Returns:
        dict[str, int]: mapping of suspicious IP -> failed attempt count.
            Only IPs at or above max_attempts are included.
    """
    failed_attempts: Counter[str] = Counter()

    for line in log_lines:
        match = FAILED_SSH_PATTERN.search(line)
        if match:
            failed_attempts[match.group("ip")] += 1

    suspicious = {
        ip: count
        for ip, count in failed_attempts.items()
        if count >= max_attempts
    }

    for ip, count in suspicious.items():
        send_alert(
            f"Possible SSH brute-force from "
            f"{ip}: {count} failed login attempts"
        )

    return suspicious
