def check_attempt(log: list[dict[str, str]], threshold: int) -> dict[str, int]:
    attempts: dict[str, int] = {}

    for connexion in log:
        ip = connexion.get("IP", "")
        if ip not in attempts:
            attempts[ip] = 0
        attempts[ip] += 1
        if attempts[ip] > threshold:
            print(f"ALERT: BruteForce '{ip}'"
                  f" on SSH. Attempt: {attempts[ip]}")
    return attempts
