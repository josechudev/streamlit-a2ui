"""Check that two wheels hold the same files with the same content.

Usage: ``python scripts/compare_wheels.py A.whl B.whl``

Compares every member by name and SHA-256 digest. Nothing is ignored: the
RECORD, WHEEL and METADATA files are compared too. Only file times and
compression, which do not change what is installed, are not compared.
Exits 1 and lists the differences otherwise. Standard library only, so it
runs in any CI step.
"""

from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path


def digests(wheel: Path) -> dict[str, str]:
    with zipfile.ZipFile(wheel) as archive:
        return {
            info.filename: hashlib.sha256(archive.read(info)).hexdigest()
            for info in archive.infolist()
            if not info.is_dir()
        }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    first, second = Path(argv[1]), Path(argv[2])
    a, b = digests(first), digests(second)
    problems = [f"only in {first}: {n}" for n in sorted(a.keys() - b.keys())]
    problems += [f"only in {second}: {n}" for n in sorted(b.keys() - a.keys())]
    problems += [
        f"content differs: {n}" for n in sorted(a.keys() & b.keys()) if a[n] != b[n]
    ]
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(f"identical: {len(a)} files, same names and SHA-256 digests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
