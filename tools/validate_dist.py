#!/usr/bin/env python3
"""Confere o pacote local: manifesto, shaders originais e ausência de resource de servidor."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REQUIRED_DOCS = [
    "INSTALACAO.md",
    "DESINSTALACAO.md",
    "BACKUP.md",
    "COMPATIBILIDADE.md",
    "LICENCAS.md",
    "ARQUITETURA.md",
    "INTEGRACAO_INSTALADOR.md",
]
FORBIDDEN_NAMES = {
    "fxmanifest.lua",
    "server.cfg",
    "__resource.lua",
}
THIRD_PARTY_MARKERS = (
    "LumaSharpen",
    "qUINT",
    "BloomAndLensFlares",
    "SweetFX",
    "Technicolor",
)


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    for name in REQUIRED_DOCS:
        if not (ROOT / "docs" / name).is_file():
            fail(f"documento ausente: docs/{name}")

    for edition in ("quality", "performance"):
        folder = DIST / edition
        manifest_path = folder / "manifest.json"
        if not manifest_path.is_file():
            fail(f"manifesto ausente: {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("kind") != "client-local":
            fail(f"{edition}: kind precisa ser client-local")
        if manifest.get("edition") != edition:
            fail(f"{edition}: edition do manifesto não confere")
        sources = []
        for entry in manifest["files"]:
            source = folder / entry["source"]
            if not source.is_file():
                fail(f"origem inexistente: {source}")
            if "backup_if_exists" not in entry or "restore_on_uninstall" not in entry:
                fail(f"entrada sem backup/restauração: {entry['source']}")
            if not entry["destination"].startswith("{fivem_plugins}/"):
                fail(f"destino fora da pasta local do FiveM: {entry['destination']}")
            if entry["destination_dir"] != entry["destination"].rsplit("/", 1)[0]:
                fail(f"pasta de destino não confere: {entry['source']}")
            if entry["restore_on_uninstall"] != "restore_backup_or_delete":
                fail(f"política de restauração inesperada: {entry['source']}")
            sources.append(source)
            text = source.read_text(encoding="utf-8", errors="replace") if source.suffix in {".fx", ".ini", ".json", ".md"} else ""
            for marker in THIRD_PARTY_MARKERS:
                if marker in text:
                    fail(f"referência de shader de terceiros em {source}: {marker}")
            if source.suffix == ".fx" and '#include "ReShade.fxh"' in text:
                fail(f"shader depende do pacote de terceiros ReShade.fxh: {source}")
            if source.suffix == ".fx" and '#include "FGM.fxh"' not in text:
                fail(f"shader sem cabeçalho local: {source}")
        preset = folder / manifest["preset"]
        if not preset.is_file():
            fail(f"preset ausente: {preset}")
        preset_text = preset.read_text(encoding="utf-8")
        for technique in preset_text.split("Techniques=", 1)[1].splitlines()[0].split(","):
            filename = technique.split("@", 1)[1]
            if not (folder / "reshade-shaders" / "Shaders" / "FGM" / filename).is_file():
                fail(f"técnica aponta para shader ausente: {technique}")
        if edition == "performance" and "FGM_Bloom" in preset_text:
            fail("performance não pode ativar o bloom pesado")
        if edition == "quality" and "FGM_Bloom@FGM_Bloom.fx" not in preset_text:
            fail("quality precisa incluir bloom")
        header = folder / "reshade-shaders" / "Shaders" / "FGM" / "FGM.fxh"
        if not header.is_file():
            fail(f"{edition}: cabeçalho local ausente")
        if edition == "performance" and (folder / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Bloom.fx").exists():
            fail("performance não deve carregar o shader de bloom")
        destinations = [entry["destination"] for entry in manifest["files"]]
        if manifest.get("backup_files") != destinations or manifest.get("restore_on_uninstall") != destinations:
            fail(f"{edition}: listas de backup e restauração divergem dos arquivos")
        lut = next(folder.glob("reshade-shaders/Textures/FGM/*.png"))
        signature = lut.read_bytes()[:8]
        if signature != b"\x89PNG\r\n\x1a\n":
            fail(f"LUT inválida: {lut}")
        for path in folder.rglob("*"):
            if path.name in FORBIDDEN_NAMES:
                fail(f"arquivo de servidor dentro do pacote: {path}")

    banned = [ROOT / "fxmanifest.lua", ROOT / "server.cfg", ROOT / "client", ROOT / "server"]
    for path in banned:
        if path.exists():
            fail(f"resto de resource de servidor: {path}")
    print("pacote local ok")


if __name__ == "__main__":
    sys.exit(main())
