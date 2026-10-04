#!/usr/bin/env python3
"""Desinstala uma instalação simulada e confere a restauração do backup."""

from __future__ import annotations

import shutil
from pathlib import Path

from fgm_testlib import ROOT, assert_ok, fake_runtime, make_fivem, run_installer
from install_test import SETTINGS, settings_for

DIST = ROOT / "dist"


def main() -> None:
    base = Path("/tmp/fgm-uninstall-test")
    if base.exists():
        shutil.rmtree(base)
    root = base / "FiveM.app"
    make_fivem(root)
    citizen = (root / "CitizenFX.ini").read_bytes()
    plugins = root / "plugins"
    plugins.mkdir()
    user_shader = plugins / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Sharp.fx"
    user_shader.parent.mkdir(parents=True)
    user_shader.write_text("USER-SHADER", encoding="utf-8")
    original_ini = b"[GENERAL]\r\nPresetPath=.\\MyPreset.ini\r\nKeepMe=1\r\n"
    (plugins / "ReShade.ini").write_bytes(original_ini)
    (plugins / "MyPreset.ini").write_text("terceiro\r\n", encoding="utf-8")
    runtime = base / "runtime.dll"
    fake_runtime(runtime)
    game_settings = settings_for(root)
    original_settings = game_settings.read_bytes()
    installed = run_installer(["-Command", "install", "-Edition", "quality", "-FiveMRoot", str(root), "-PackageRoot", str(DIST), "-RuntimeDll", str(runtime), "-SettingsXml", str(game_settings)])
    assert_ok(installed, "FGM install ok edition=ultra")
    if not (plugins / "dxgi.dll").is_file():
        raise SystemExit("runtime não foi colocada")
    removed = run_installer(["-Command", "uninstall", "-FiveMRoot", str(root)])
    assert_ok(removed, "FGM uninstall ok")
    if user_shader.read_text(encoding="utf-8") != "USER-SHADER":
        raise SystemExit("shader original não voltou")
    if (plugins / "ReShade.ini").read_bytes() != original_ini:
        raise SystemExit("ReShade.ini não foi restaurado byte a byte")
    if (plugins / "dxgi.dll").exists():
        raise SystemExit("dxgi.dll criado pelo FGM continuou depois da remoção")
    if (plugins / "FGM-Ultra.ini").exists():
        raise SystemExit("preset do FGM continuou instalado")
    if (plugins / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Bloom.fx").exists():
        raise SystemExit("shader criado pelo FGM continuou instalado")
    if (plugins / "MyPreset.ini").read_bytes() != b"terceiro\r\n":
        raise SystemExit("preset de terceiro foi apagado")
    if (root / "CitizenFX.ini").read_bytes() != citizen:
        raise SystemExit("CitizenFX.ini mudou na desinstalação")
    if game_settings.read_bytes() != original_settings:
        raise SystemExit("settings.xml não voltou ao original")
    if original_settings != SETTINGS.encode("utf-8"):
        raise SystemExit("o teste não partiu do settings original")
    if (root / "FGM-state.json").exists():
        raise SystemExit("estado permaneceu depois da desinstalação")
    if not (root / "FGM-Backup").is_dir():
        raise SystemExit("backup foi apagado")

    reuse = base / "reuse.app"
    make_fivem(reuse)
    (reuse / "plugins").mkdir()
    existing = reuse / "plugins" / "dxgi.dll"
    fake_runtime(existing, "6.5.0")
    blob = existing.read_bytes()
    reused = run_installer(["-Command", "install", "-Edition", "performance", "-FiveMRoot", str(reuse), "-PackageRoot", str(DIST), "-RuntimeDll", str(runtime), "-SettingsXml", str(settings_for(reuse))])
    assert_ok(reused, "FGM install ok edition=low")
    cleared = run_installer(["-Command", "uninstall", "-FiveMRoot", str(reuse)])
    assert_ok(cleared, "FGM uninstall ok")
    if existing.read_bytes() != blob:
        raise SystemExit("ReShade que já existia foi removido")
    print("desinstalação ok")


if __name__ == "__main__":
    main()
