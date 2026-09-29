#!/usr/bin/env python3
"""Ajuda os testes do instalador a falar com o PowerShell."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PWSH = Path("/tmp/pwsh/pwsh")
INSTALLER = ROOT / "tools" / "Instalar-FGM.ps1"


def fake_runtime(path: Path, version: str = "6.8.0", reshade: bool = True) -> None:
    payload = b"not-a-reshade-proxy"
    if reshade:
        payload = b"ReShade\x00" + "FileVersion".encode("utf-16le") + b"\x00\x00" + version.encode("utf-16le")
    path.write_bytes(payload)


def run_installer(args: list[str]) -> subprocess.CompletedProcess[str]:
    if not PWSH.is_file():
        raise SystemExit(f"PowerShell de teste ausente: {PWSH}")
    return subprocess.run(
        [str(PWSH), "-NoProfile", "-File", str(INSTALLER), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def make_fivem(root: Path, citizen: str = "UseAudio=true\r\n") -> None:
    root.mkdir(parents=True)
    (root / "CitizenFX.ini").write_bytes(citizen.encode("utf-8"))


def assert_ok(result: subprocess.CompletedProcess[str], needle: str) -> None:
    if result.returncode != 0 or needle not in result.stdout:
        raise SystemExit(result.stdout + "\n" + result.stderr)
