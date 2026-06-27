"""
Network port scanning utilities.

This module provides a simple function to scan local TCP ports
on 127.0.0.1 and report which ports are open.

It is intended for basic diagnostic and development purposes,
not for production-grade network scanning.
"""

import socket


def check_port() -> None:
    """
    Scan local TCP ports (0–1023) and print open ports.

    The function attempts to connect to each port on localhost
    (127.0.0.1) using a short timeout.

    Prints:
        str: "PORT: <port> is open" for each open port found.
    """
    for port in range(1024):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.1)
            result = sock.connect_ex(("127.0.0.1", port))
            if result == 0:
                print(f"PORT: {port} is open")
