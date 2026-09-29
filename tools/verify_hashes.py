#!/usr/bin/env python3
"""Recalcula o SHA-256 de cada arquivo listado nos manifestos."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(folder: Path) -> None:
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        source = folder / entry["source"]
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != entry["sha256"]:
            raise SystemExit(f"hash divergente: {source}")
        if source.stat().st_size != entry["bytes"]:
            raise SystemExit(f"tamanho divergente: {source}")


def main() -> None:
    for edition in ("quality", "performance"):
        check(ROOT / "dist" / edition)
        title = edition.capitalize()
        check(ROOT / "release" / "FGM-v1.0.0" / title)
    print("hashes ok")


if __name__ == "__main__":
    main()
