"""
System monitoring and log analysis module.

This module provides functions to:
- Detect the Linux distribution of the system
- Read system log files depending on the distribution
- Log system information using a structured logging system

Supported distributions:
- Debian family: debian, ubuntu, linuxmint, kali, raspbian
- Fedora family: fedora, rhel, centos, rocky, almalinux

It is designed for system diagnostics and basic monitoring purposes.
"""

import os
import logging
from pathlib import Path

# Créer un logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Log tous les niveaux à partir de DEBUG

# Créer un handler pour les logs INFO (sans ligne et fichier)
info_handler = logging.StreamHandler()
info_handler.setLevel(logging.INFO)
info_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
info_handler.setFormatter(info_formatter)

# Créer un handler pour les logs WARNING,
# ERROR, CRITICAL (avec ligne et fichier)
debug_handler = logging.StreamHandler()
debug_handler.setLevel(logging.WARNING)
FORMATTER_1 = "%(asctime)s - %(levelname)s - %(message)s"
FORMATTER_2 = " in %(filename)s at line %(lineno)s"
debug_formatter = logging.Formatter(FORMATTER_1 + FORMATTER_2)
debug_handler.setFormatter(debug_formatter)

# Créer un FileHandler pour enregistrer les logs dans un fichier
# Le chemin est relatif à l'emplacement de ce module, pas au répertoire
# courant : le programme fonctionne donc peu importe d'où il est lancé.
LOG_FILE_PATH = Path(__file__).resolve().parent / "app_logs.log"
file_handler = logging.FileHandler(LOG_FILE_PATH)
HANDLER_1 = "%(asctime)s - %(levelname)s - %(message)s"
HANDLER_2 = " in %(filename)s at line %(lineno)s"
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(HANDLER_1 + HANDLER_2)
file_handler.setFormatter(file_formatter)

# Ajouter les handlers au logger
logger.addHandler(info_handler)
logger.addHandler(debug_handler)
logger.addHandler(file_handler)


def detect_distrib() -> str:
    """
    Detect the Linux distribution by reading /etc/os-release.

    Returns:
        str: Linux distribution ID (e.g. 'ubuntu', 'fedora').

    Raises:
        FileNotFoundError: If /etc/os-release cannot be found.
        Exception: For unexpected errors during file reading or parsing.
    """
    path = os.path.join("/", "etc", "os-release")
    try:
        logger.info("Trying to access %s", path)
        with open(path, "r", encoding="UTF-8") as file:
            data = file.read()
            logger.info("File content successfully read from %s", path)
            fields: dict[str, str] = {}
            for line in data.split("\n"):
                if not line or line.startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                fields[name] = value.strip('"')

            distrib_id = fields.get("ID", "")
            logger.info("Linux distribution: %s", distrib_id.capitalize())
            return distrib_id

    except FileNotFoundError as exc:
        logger.error("File not found at '/etc/os-release'.")
        raise FileNotFoundError(
            "The file '/etc/os-release' could not be found."
        ) from exc
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        raise


def read_log(distrib: str) -> list[str]:
    """
    Read system log file depending on the detected Linux distribution.

    Args:
        distrib (str): Linux distribution name (e.g. 'ubuntu', 'fedora').

    Returns:
        list[str]: Lines of the log file, in order.

    Raises:
        RuntimeError: If distribution is not supported.
        PermissionError: If access to log file is denied.
        FileNotFoundError: If the log file does not exist.
        Exception: For unexpected errors during file reading.
    """
    debian_family = ("debian", "ubuntu", "linuxmint", "kali", "raspbian")
    fedora_family = ("fedora", "rhel", "centos", "rocky", "almalinux")

    if distrib in debian_family:
        log_filename = "auth.log"
    elif distrib in fedora_family:
        log_filename = "secure"
    else:
        logger.critical(
            "Your linux distribution ('%s') is not compatible with "
            "program. Only Debian-family and Fedora-family "
            "distributions are supported.",
            distrib,
        )
        raise RuntimeError(f"Unsupported Linux distribution: {distrib}")

    logger.info("Your distribution is compatible with program.")
    data = os.path.join("/", "var", "log", log_filename)
    try:
        logger.info("Trying to access file %s", data)
        with open(data, "r", encoding="utf-8") as file:
            lines = file.readlines()
            logger.info("File content successfully read from %s", data)
            return lines
    except PermissionError as exc:
        logger.error(
            "Please relaunch the program with proper permissions, "
            "e.g. 'sudo python [PROGRAM_NAME].py'"
        )
        raise PermissionError(
            "Permission denied while trying to access the log file."
        ) from exc
    except FileNotFoundError as exc:
        logger.error("File not found at '%s'.", data)
        raise FileNotFoundError(f"Log file {data} not found.") from exc
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        raise
