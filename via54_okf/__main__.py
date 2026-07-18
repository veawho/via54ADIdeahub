"""Allow ``python -m via54_okf …`` invocation."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())