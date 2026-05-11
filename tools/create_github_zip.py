from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "opera_rapports_github.zip"


def tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [ROOT / line for line in output.splitlines() if line]


def create_zip(target: Path = DEFAULT_OUTPUT) -> Path:
    if target.exists():
        target.unlink()
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in tracked_files():
            archive.write(path, path.relative_to(ROOT))
    return target


if __name__ == "__main__":
    created = create_zip()
    print(created)
