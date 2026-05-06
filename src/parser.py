import sys
import os
import re
from typing import Any


def parsing_arg() -> tuple[list[dict[str, str]], int]:
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        raise ValueError("Usage: 'sudo main.py "
                         "/var/log/[FILE_NAME]' optionnal [THRESHOLD]")

    path = os.path.normpath(sys.argv[1])

    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    threshold = int(sys.argv[2]) if len(sys.argv) == 3 else 5

    return read_file({"PATH": path, "THRESHOLD": threshold})


def read_file(arg: dict[str, Any]) -> tuple[list[dict[str, str]], int]:
    f = arg.get("PATH", "")
    threshold = arg.get("THRESHOLD", 0)
    try:
        with open(f, 'r') as file:
            raw = file.read()

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found '{f}'")

    except PermissionError:
        raise PermissionError("You dont have permission please write "
                              "'sudo python main.py /var/log/[FILE_NAME]'"
                              " optionnal [THRESHOLD]")

    except Exception:
        raise Exception()

    ip_format: str = r"([0-9]{1,3}\.){3}[0-9]{1,3}"
    con_format: str = r"(Failed|Accepted)"
    date_format: str = r"^\w+\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}"
    log: list[dict[str, str]] = []
    lines = raw.split("\n")
    for line in lines:
        if re.search("ssh", line):
            ip = re.search(ip_format, line)
            connexion = re.search(con_format, line)
            date = re.search(date_format, line)
            if ip and connexion and date:
                log.append({"IP": ip.group(),
                            "CONNEXION": connexion.group(),
                            "DATE": date.group()})
    return (log, threshold)
