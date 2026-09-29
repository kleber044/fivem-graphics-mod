#!/usr/bin/env python3
"""Instalação simulada: duas vezes, troca de edição, conflito, hash e runtime."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from fgm_testlib import INSTALLER, ROOT, PWSH, assert_ok, fake_runtime, make_fivem, run_installer

DIST = ROOT / "dist"


def install(root: Path, edition: str, runtime: Path | None = None) -> subprocess.CompletedProcess[str]:
    args = ["-Command", "install", "-Edition", edition, "-FiveMRoot", str(root), "-PackageRoot", str(DIST)]
    if runtime:
        args.extend(["-RuntimeDll", str(runtime)])
    return run_installer(args)


def main() -> None:
    base = Path("/tmp/fgm-install-test")
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
    (plugins / "MyPreset.ini").write_text("[GENERAL]\r\nPresetPath=.\\MyPreset.ini\r\n", encoding="utf-8")
    (plugins / "ReShade.ini").write_bytes(b"[GENERAL]\r\nPresetPath=.\\MyPreset.ini\r\nKeepMe=1\r\n")
    runtime = base / "runtime.dll"
    fake_runtime(runtime)
    kept = (plugins / "MyPreset.ini").read_bytes()

    result = install(root, "quality", runtime)
    assert_ok(result, "FGM install ok edition=quality")
    if (root / "CitizenFX.ini").read_bytes() != citizen:
        raise SystemExit("CitizenFX.ini mudou na instalação")
    if (plugins / "MyPreset.ini").read_bytes() != kept:
        raise SystemExit("preset de terceiro foi alterado")
    state = json.loads((root / "FGM-state.json").read_text(encoding="utf-8"))
    if state["edition"] != "quality":
        raise SystemExit("estado não gravou quality")
    ini = (plugins / "ReShade.ini").read_text(encoding="utf-8")
    if "PresetPath=.\\FGM-Quality.ini" not in ini or "KeepMe=1" not in ini:
        raise SystemExit(f"ReShade.ini não preservou a chave do usuário:\n{ini}")
    if not (plugins / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Bloom.fx").is_file():
        raise SystemExit("bloom da Quality ausente")
    if "USER-SHADER" in user_shader.read_text(encoding="utf-8"):
        raise SystemExit("shader do usuário não foi substituído")
    backup = next((root / "FGM-Backup").glob("*/files/reshade-shaders/Shaders/FGM/FGM_Sharp.fx"))
    if backup.read_text(encoding="utf-8") != "USER-SHADER":
        raise SystemExit("backup do shader original está errado")

    again = install(root, "quality", runtime)
    assert_ok(again, "FGM repair ok edition=quality")
    if backup.read_text(encoding="utf-8") != "USER-SHADER":
        raise SystemExit("a segunda instalação sobrescreveu o backup original")

    switched = run_installer(["-Command", "switch", "-Edition", "performance", "-FiveMRoot", str(root), "-PackageRoot", str(DIST), "-RuntimeDll", str(runtime)])
    assert_ok(switched, "FGM switch ok edition=performance")
    if (plugins / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Bloom.fx").exists():
        raise SystemExit("bloom continuou ativo na Performance")
    perf_lut = (plugins / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Lut.fx").read_text(encoding="utf-8")
    if "fgm_performance_lut.png" not in perf_lut:
        raise SystemExit("LUT da Performance não entrou")
    if "FGM-Performance.ini" not in (plugins / "ReShade.ini").read_text(encoding="utf-8"):
        raise SystemExit("preset não trocou para Performance")
    if (plugins / "FGM-Quality.ini").exists():
        raise SystemExit("preset Quality continuou instalado")
    if backup.read_text(encoding="utf-8") != "USER-SHADER":
        raise SystemExit("troca de edição perdeu o backup original")

    back = run_installer(["-Command", "switch", "-Edition", "quality", "-FiveMRoot", str(root), "-PackageRoot", str(DIST), "-RuntimeDll", str(runtime)])
    assert_ok(back, "FGM switch ok edition=quality")
    if not (plugins / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Bloom.fx").is_file():
        raise SystemExit("volta para Quality não recolocou o bloom")
    if (plugins / "fgm_performance_lut.png").exists() or (plugins / "reshade-shaders" / "Textures" / "FGM" / "fgm_performance_lut.png").exists():
        raise SystemExit("LUT da Performance ficou para trás")

    bloom = plugins / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Bloom.fx"
    bloom.unlink()
    repaired = run_installer(["-Command", "repair", "-FiveMRoot", str(root), "-PackageRoot", str(DIST), "-RuntimeDll", str(runtime)])
    assert_ok(repaired, "FGM repair ok edition=quality")
    if not bloom.is_file():
        raise SystemExit("reparo não devolveu o bloom")

    foreign_root = base / "foreign.app"
    make_fivem(foreign_root)
    foreign_plugins = foreign_root / "plugins"
    foreign_plugins.mkdir()
    foreign_dll = foreign_plugins / "dxgi.dll"
    fake_runtime(foreign_dll, reshade=False)
    before = foreign_dll.read_bytes()
    failed = install(foreign_root, "quality", runtime)
    if failed.returncode == 0:
        raise SystemExit("dxgi de outro programa não deveria ser substituído")
    if foreign_dll.read_bytes() != before or (foreign_root / "FGM-state.json").exists():
        raise SystemExit("conflito alterou o FiveM")

    missing = base / "nao-existe.app"
    missed = install(missing, "quality", runtime)
    if missed.returncode == 0 or missing.exists():
        raise SystemExit("instalador criou pasta para um FiveM inexistente")

    empty = base / "vazio.app"
    empty.mkdir()
    emptied = install(empty, "quality", runtime)
    if emptied.returncode == 0 or (empty / "plugins").exists():
        raise SystemExit("pasta sem CitizenFX.ini foi tratada como FiveM")

    broken = base / "broken-package"
    shutil.copytree(DIST / "quality", broken / "quality")
    shader = broken / "quality" / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Lut.fx"
    shader.write_bytes(shader.read_bytes() + b"\n")
    broken_root = base / "broken.app"
    make_fivem(broken_root)
    bad = run_installer(["-Command", "install", "-Edition", "quality", "-FiveMRoot", str(broken_root), "-PackageRoot", str(broken), "-RuntimeDll", str(runtime)])
    if bad.returncode == 0 or (broken_root / "FGM-state.json").exists() or (broken_root / "plugins").exists():
        raise SystemExit("pacote com hash inválido foi instalado")

    reuse_root = base / "reuse.app"
    make_fivem(reuse_root)
    (reuse_root / "plugins").mkdir()
    existing = reuse_root / "plugins" / "dxgi.dll"
    fake_runtime(existing, "6.1.0")
    existing_bytes = existing.read_bytes()
    reused = install(reuse_root, "quality", runtime)
    assert_ok(reused, "FGM install ok edition=quality")
    if existing.read_bytes() != existing_bytes:
        raise SystemExit("ReShade compatível foi substituído")
    if (reuse_root / "plugins" / "ReShade-BSD-3-Clause.txt").exists():
        raise SystemExit("licença foi copiada em cima de uma instalação reutilizada")

    d3d_root = base / "d3d.app"
    make_fivem(d3d_root)
    (d3d_root / "plugins").mkdir()
    d3d = d3d_root / "plugins" / "d3d11.dll"
    fake_runtime(d3d, "6.2.0")
    d3d_install = install(d3d_root, "performance", runtime)
    assert_ok(d3d_install, "FGM install ok edition=performance")
    if (d3d_root / "plugins" / "dxgi.dll").exists():
        raise SystemExit("foi criado um segundo hook ao lado do d3d11 do ReShade")

    old_root = base / "old.app"
    make_fivem(old_root)
    (old_root / "plugins").mkdir()
    old = old_root / "plugins" / "dxgi.dll"
    fake_runtime(old, "4.9.0")
    old_bytes = old.read_bytes()
    replaced = install(old_root, "quality", runtime)
    assert_ok(replaced, "FGM install ok edition=quality")
    if old.read_bytes() == old_bytes:
        raise SystemExit("ReShade antigo não foi atualizado")

    protected = subprocess.run(
        [str(PWSH), "-NoProfile", "-Command",
         f". '{ROOT / 'tools' / 'fgm-install-lib.ps1'}'; try {{ Resolve-FgmPackageFile '{{fivem_plugins}}/CitizenFX.ini' '{plugins}' | Out-Null; exit 2 }} catch {{ exit 0 }}"],
        text=True, capture_output=True, check=False,
    )
    if protected.returncode != 0:
        raise SystemExit(protected.stdout + protected.stderr)

    setup = Path("/tmp/ReShade_Setup_6.8.0.exe")
    if setup.is_file():
        extracted = subprocess.run(
            [str(PWSH), "-NoProfile", "-Command",
             "$meta = Get-Content '" + str(ROOT / "tools" / "reshade-official.json") + "' -Raw | ConvertFrom-Json; "
             ". '" + str(ROOT / "tools" / "fgm-install-lib.ps1") + "'; "
             "$bytes = Expand-FgmReShade64 '" + str(setup) + "' $meta; "
             "if ($bytes.Length -ne 5255448) { exit 3 }"],
            text=True, capture_output=True, check=False,
        )
        if extracted.returncode != 0:
            raise SystemExit(extracted.stdout + extracted.stderr)
    else:
        raise SystemExit("instalador oficial de teste ausente em /tmp")
    if not INSTALLER.is_file():
        raise SystemExit("entrada do instalador ausente")
    print("instalação ok")


if __name__ == "__main__":
    main()
