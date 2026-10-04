#!/usr/bin/env python3
"""Recalcula o SHA-256 de cada arquivo listado nos manifestos."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITIONS = ("ultra", "high", "medium", "low")
TITLES = {"ultra": "Ultra", "high": "High", "medium": "Medium", "low": "Low"}


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
    for edition in EDITIONS:
        check(ROOT / "dist" / edition)
        check(ROOT / "release" / "FGM-v2.0.0" / TITLES[edition])
    print("hashes ok")


if __name__ == "__main__":
    main()
