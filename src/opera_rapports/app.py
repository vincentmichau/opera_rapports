from __future__ import annotations

import sys

from opera_rapports.gui.main_window import run


def main() -> int:
    """Application entry point."""
    return run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
