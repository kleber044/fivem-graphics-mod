#!/usr/bin/env python3
"""Aplica ou remove uma edição FGM numa pasta plugins, seguindo manifest.json.

Não mexe em ReShade.ini, dxgi.dll, CitizenFX.ini nem em arquivos do GTA.
Serve para o instalador futuro e para o teste local deste repositório.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "{fivem_plugins}/"


def load_manifest(edition: str) -> tuple[Path, dict]:
    folder = ROOT / "dist" / edition
    path = folder / "manifest.json"
    if not path.is_file():
        raise SystemExit(f"manifesto ausente: {path}. Rode tools/build_dist.py.")
    return folder, json.loads(path.read_text(encoding="utf-8"))


def relative_destination(destination: str) -> Path:
    if not destination.startswith(TOKEN):
        raise SystemExit(f"destino sem token de plugins: {destination}")
    return Path(destination[len(TOKEN) :])


def install(edition: str, plugins: Path, backup_root: Path) -> Path:
    folder, manifest = load_manifest(edition)
    if manifest.get("kind") != "client-local":
        raise SystemExit("manifesto não é client-local")
    plugins.mkdir(parents=True, exist_ok=True)
    receipt_dir = backup_root / edition
    receipt_path = receipt_dir / "receipt.json"
    if receipt_path.exists():
        raise SystemExit(f"já existe instalação registrada em {receipt_path}")
    receipt_dir.mkdir(parents=True, exist_ok=True)
    installed = []
    for entry in manifest["files"]:
        source = folder / entry["source"]
        if not source.is_file():
            raise SystemExit(f"origem ausente: {source}")
        relative = relative_destination(entry["destination"])
        target = plugins / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        backed_up = False
        if target.exists():
            if not entry.get("backup_if_exists"):
                raise SystemExit(f"destino existe e o manifesto não pede backup: {target}")
            backup_path = receipt_dir / "files" / relative
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_path)
            backed_up = True
        shutil.copy2(source, target)
        installed.append({"destination": entry["destination"], "backed_up": backed_up})
    receipt = {
        "edition": edition,
        "plugins": str(plugins),
        "files": installed,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt_path


def uninstall(edition: str, plugins: Path, backup_root: Path) -> None:
    _, manifest = load_manifest(edition)
    receipt_dir = backup_root / edition
    receipt_path = receipt_dir / "receipt.json"
    if not receipt_path.is_file():
        raise SystemExit(f"recibo de instalação ausente: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("edition") != edition:
        raise SystemExit("recibo não pertence a esta edição")
    by_dest = {item["destination"]: item for item in receipt["files"]}
    for entry in reversed(manifest["files"]):
        item = by_dest.get(entry["destination"])
        if item is None:
            raise SystemExit(f"recibo sem o arquivo {entry['destination']}")
        relative = relative_destination(entry["destination"])
        target = plugins / relative
        backup_path = receipt_dir / "files" / relative
        if item["backed_up"]:
            if not backup_path.is_file():
                raise SystemExit(f"backup ausente: {backup_path}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, target)
        elif target.exists():
            target.unlink()
    shutil.rmtree(receipt_dir)


def self_test() -> None:
    edition = "quality"
    folder, manifest = load_manifest(edition)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        plugins = root / "plugins"
        backup = root / "backup"
        plugins.mkdir()
        seed = plugins / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Sharp.fx"
        seed.parent.mkdir(parents=True)
        seed.write_text("shader-do-jogador", encoding="utf-8")
        untouched = plugins / "ReShade.ini"
        untouched.write_text("config-do-jogador", encoding="utf-8")
        dll = plugins / "dxgi.dll"
        dll.write_bytes(b"reshade")
        install(edition, plugins, backup)
        if untouched.read_text(encoding="utf-8") != "config-do-jogador":
            raise SystemExit("ReShade.ini foi alterado")
        if dll.read_bytes() != b"reshade":
            raise SystemExit("dxgi.dll foi alterado")
        preset = plugins / manifest["preset"]
        if not preset.is_file():
            raise SystemExit("preset não foi instalado")
        installed_shader = seed.read_text(encoding="utf-8")
        if installed_shader == "shader-do-jogador":
            raise SystemExit("shader existente não foi substituído")
        if "FGM_Sharp" not in installed_shader:
            raise SystemExit("shader instalado não é o FGM")
        lut = next((plugins / "reshade-shaders" / "Textures" / "FGM").glob("*.png"))
        if lut.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise SystemExit("LUT instalada inválida")
        expected = folder / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Lut.fx"
        copied = plugins / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Lut.fx"
        if copied.read_bytes() != expected.read_bytes():
            raise SystemExit("cópia do shader diverge da origem")
        uninstall(edition, plugins, backup)
        if seed.read_text(encoding="utf-8") != "shader-do-jogador":
            raise SystemExit("backup do shader não foi restaurado")
        if (plugins / manifest["preset"]).exists():
            raise SystemExit("preset permaneceu depois da desinstalação")
        if (plugins / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Lut.fx").exists():
            raise SystemExit("shader novo permaneceu depois da desinstalação")
        if untouched.read_text(encoding="utf-8") != "config-do-jogador":
            raise SystemExit("ReShade.ini mudou na desinstalação")
    print("instalação local ok")


def main() -> None:
    parser = argparse.ArgumentParser(description="Aplica o manifesto FGM numa pasta plugins.")
    parser.add_argument("action", choices=("install", "uninstall", "self-test"))
    parser.add_argument("--edition", choices=("quality", "performance"))
    parser.add_argument("--plugins", type=Path)
    parser.add_argument("--backup", type=Path)
    args = parser.parse_args()
    if args.action == "self-test":
        self_test()
        return
    if args.edition is None or args.plugins is None or args.backup is None:
        raise SystemExit("install e uninstall exigem --edition, --plugins e --backup")
    if args.action == "install":
        path = install(args.edition, args.plugins, args.backup)
        print(f"instalado: {path}")
    else:
        uninstall(args.edition, args.plugins, args.backup)
        print("removido")


if __name__ == "__main__":
    sys.exit(main())
