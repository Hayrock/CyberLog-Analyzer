import sys, os
import re
from typing import Any, Union
import traceback

def parsing_arg() -> dict[str, Union[str, int]]:
    if 1 <= len(sys.argv) > 3:
        raise ValueError("Please write only name "
                         " program and path 'sudo main.py "
                         "/var/log/[FILE_NAME]' optionnal [THRESHOLD]")
    if sys.argv[1] and '/' in sys.argv[1]:
        try:
            _, var, log, file = sys.argv[1].split("/", 3)
            path_ssh = os.path.join("/", var, log, file)
            threshold = int(sys.argv[2])
            return {"PATH": path_ssh, "TRESHOLD": threshold}

        except ValueError:
            raise ValueError("Please write correctly path "
            "'/var/log/[FILE_NAME]' optionnal [THRESHOLD]")

        except IndexError:
            return 
        
        except Exception:
            raise Exception("An error appear at parsing arg !")

def read_file(arg: dict[str, Union[str, int]]):
    f = arg.get("PATH", "")
    log: list[dict[str, str]] = []
    try:
        with open(f, 'r') as file:
            raw = file.read()

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found '{f}'")

    except PermissionError:
        raise PermissionError("You dont have permission please write " \
        "'sudo python main.py /var/log/[FILE_NAME]' optionnal [THRESHOLD] ")
    
    except Exception:
        raise Exception()

    ip_format: str = r"([0-9]{1,3}\.){3}[0-9]{1,3}"
    port_format: str = r"port [0-9]{1,5}"
    con_format: str = r"Connection [a-z]"
    lines = raw.split("\n")
    for line in lines:
        if re.search("ssh", line):
            ip = re.search(ip_format, line)
            port = re.search(port_format, line)
            connexion = re.search(con_format, line)
            if ip and port and connexion:
                log.append({"IP": ip.group()})
                log.append({"PORT": port.group()})
                log.append({"CONNEXION": connexion.group()})
    print(log)
    return log


if __name__ == "__main__":
    try:
        arg = parsing_arg()
        read_file(arg)
    except Exception as e:
        print(e)
        traceback.print_exc()