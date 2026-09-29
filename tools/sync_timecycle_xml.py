#!/usr/bin/env python3
"""Gera timecycle/quality.xml e timecycle/performance.xml a partir de shared/timecycle.lua."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "shared" / "timecycle.lua"
VAR_RE = re.compile(
    r"^        ([A-Za-z0-9_]+) = \{ (-?\d+\.\d+), (-?\d+\.\d+) \},$"
)
MOD_RE = re.compile(r"^    (fgm_[A-Za-z0-9_]+) = \{$")


def parse_modifiers(text: str) -> dict[str, dict[str, tuple[str, str]]]:
    modifiers: dict[str, dict[str, tuple[str, str]]] = {}
    current: str | None = None
    for line in text.splitlines():
        mod = MOD_RE.match(line)
        if mod:
            current = mod.group(1)
            modifiers[current] = {}
            continue
        if current and line == "    },":
            current = None
            continue
        if current is None:
            continue
        var = VAR_RE.match(line)
        if not var:
            if line.strip() and not line.strip().startswith("--"):
                raise SystemExit(f"linha fora do formato em {current}: {line}")
            continue
        modifiers[current][var.group(1)] = (var.group(2), var.group(3))
    if not modifiers:
        raise SystemExit("nenhum modifier encontrado")
    return modifiers


def render(names: list[str], modifiers: dict[str, dict[str, tuple[str, str]]]) -> str:
    chunks = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<timecycle_modifier_data version="1.000000">',
    ]
    for name in names:
        variables = modifiers[name]
        chunks.append(
            f'    <modifier name="{name}" numMods="{len(variables)}" userFlags="0">'
        )
        for key in sorted(variables):
            first, second = variables[key]
            chunks.append(f"        <{key}>{first} {second}</{key}>")
        chunks.append("    </modifier>")
    chunks.append("</timecycle_modifier_data>")
    chunks.append("")
    return "\n".join(chunks)


def main() -> None:
    modifiers = parse_modifiers(SOURCE.read_text(encoding="utf-8"))
    groups = {
        ROOT / "timecycle" / "quality.xml": [
            name for name in modifiers if name.startswith("fgm_quality_")
        ],
        ROOT / "timecycle" / "performance.xml": [
            name for name in modifiers if name.startswith("fgm_perf_")
        ],
    }
    check = "--check" in sys.argv
    for path, names in groups.items():
        if not names:
            raise SystemExit(f"grupo vazio para {path.name}")
        body = render(names, modifiers)
        if check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != body:
                raise SystemExit(f"{path.relative_to(ROOT)} não bate com shared/timecycle.lua")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
            print(f"escreveu {path.relative_to(ROOT)} ({len(names)} modifiers)")


if __name__ == "__main__":
    main()
