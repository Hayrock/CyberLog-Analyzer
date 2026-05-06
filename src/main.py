from parser import parsing_arg
from analyzer import check_attempt


def main() -> str:
    try:
        log, threshold = parsing_arg()
        attempts = check_attempt(log, threshold)
        return ""
    except Exception:
        raise


if __name__ == "__main__":
    print(main())
