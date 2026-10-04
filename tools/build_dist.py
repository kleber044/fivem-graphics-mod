#!/usr/bin/env python3
"""Gera dist/ultra, dist/high, dist/medium e dist/low e a release 2.0.0."""

from __future__ import annotations

import hashlib
import json
import shutil
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "shaders"
DIST = ROOT / "dist"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src" / "roads"))

from fgm_color import LOOK, PRODUCT_VERSION, grade  # noqa: E402
from gerar_asfalto import gerar, media  # noqa: E402

LUT_SIZE = 32

OPTIONAL_OFF = (
    "FGM_FilmGrain@FGM_FilmGrain.fx",
    "FGM_ChromaticAberration@FGM_ChromaticAberration.fx",
    "FGM_Rain@FGM_Rain.fx",
)

ALWAYS_SHADERS = [
    "FGM.fxh",
    "FGM_Shadows.fx",
    "FGM_Lut.fx",
    "FGM_Color.fx",
    "FGM_AmbientTone.fx",
    "FGM_Day.fx",
    "FGM_Night.fx",
    "FGM_Tonemap.fx",
    "FGM_HighlightRecovery.fx",
    "FGM_ColorProtection.fx",
    "FGM_ClearView.fx",
    "FGM_Lamps.fx",
    "FGM_Roads.fx",
    "FGM_Sharp.fx",
    "FGM_Vignette.fx",
    "FGM_FilmGrain.fx",
    "FGM_ChromaticAberration.fx",
    "FGM_Rain.fx",
]


def shader_list(spec: dict) -> list[str]:
    names = list(ALWAYS_SHADERS)
    if spec["ambient"] <= 0:
        names.remove("FGM_AmbientTone.fx")
    if spec["exposure"] > 0:
        names.insert(1, "FGM_Exposure.fx")
    if spec["contrast"] > 0:
        names.insert(names.index("FGM_Tonemap.fx"), "FGM_Contrast.fx")
    if spec["bloom_amount"] > 0:
        names.insert(names.index("FGM_Lamps.fx"), "FGM_Bloom.fx")
    if spec["reflect"] > 0:
        names.insert(names.index("FGM_Sharp.fx"), "FGM_ReflectionsEnhance.fx")
    return names


def technique_list(spec: dict) -> list[str]:
    items = []
    if spec["exposure"] > 0:
        items.append("FGM_Exposure@FGM_Exposure.fx")
    if spec["shadows"] > 0:
        items.append("FGM_Shadows@FGM_Shadows.fx")
    items.extend(["FGM_Lut@FGM_Lut.fx", "FGM_Color@FGM_Color.fx"])
    if spec["ambient"] > 0:
        items.append("FGM_AmbientTone@FGM_AmbientTone.fx")
    items.extend(["FGM_Day@FGM_Day.fx", "FGM_Night@FGM_Night.fx"])
    if spec["contrast"] > 0:
        items.append("FGM_Contrast@FGM_Contrast.fx")
    items.extend(
        [
            "FGM_Tonemap@FGM_Tonemap.fx",
            "FGM_HighlightRecovery@FGM_HighlightRecovery.fx",
            "FGM_ColorProtection@FGM_ColorProtection.fx",
            "FGM_ClearView@FGM_ClearView.fx",
        ]
    )
    if spec["bloom_amount"] > 0:
        items.append("FGM_Bloom@FGM_Bloom.fx")
    items.append("FGM_Lamps@FGM_Lamps.fx")
    if spec["road"] > 0:
        items.append("FGM_Roads@FGM_Roads.fx")
    if spec["reflect"] > 0:
        items.append("FGM_ReflectionsEnhance@FGM_ReflectionsEnhance.fx")
    items.extend(["FGM_Sharp@FGM_Sharp.fx", "FGM_Vignette@FGM_Vignette.fx"])
    return items


def uniforms(edition: str, spec: dict) -> dict[str, dict[str, str]]:
    values: dict[str, dict[str, str]] = {
        "FGM_Shadows.fx": {"ShadowOpen": f"{spec['shadows']:.3f}"},
        "FGM_Color.fx": {
            "ColorVibrance": f"{spec['vibrance']:.3f}",
            "PlantExtra": f"{spec['plant']:.3f}",
        },
        "FGM_Day.fx": {"DayCalm": f"{spec['day_calm']:.3f}"},
        "FGM_Night.fx": {"NightAmount": f"{spec['night']:.3f}"},
        "FGM_Tonemap.fx": {"TonemapAmount": f"{spec['tonemap']:.3f}"},
        "FGM_HighlightRecovery.fx": {"HighlightAmount": f"{spec['highlight']:.3f}"},
        "FGM_ClearView.fx": {
            "ClearDay": f"{spec['clear_day']:.3f}",
            "ClearNight": f"{spec['clear_night']:.3f}",
        },
        "FGM_Lamps.fx": {
            "PreprocessorDefinitions": f"LAMP_TAPS={spec['lamp_taps']}",
            "LampLevel": str(spec["lamp_level"]),
        },
        "FGM_Roads.fx": {
            "RoadStrength": f"{spec['road']:.3f}",
            "RoadScale": {"ultra": "8.000", "high": "7.000", "medium": "6.000", "low": "4.000"}[edition],
        },
        "FGM_Sharp.fx": {"SharpStrength": f"{spec['sharp']:.3f}"},
        "FGM_Vignette.fx": {"VignetteAmount": f"{spec['vignette']:.3f}"},
        "FGM_FilmGrain.fx": {"GrainAmount": "0.000"},
        "FGM_ChromaticAberration.fx": {"AberrationAmount": "0.000"},
        "FGM_Rain.fx": {
            "RainStrength": f"{spec['rain']:.3f}",
            "RainLayers": str(spec["rain_layers"]),
            "RainDistort": f"{spec['rain_distort']:.3f}",
        },
    }
    if spec["ambient"] > 0:
        values["FGM_AmbientTone.fx"] = {"AmbientAmount": f"{spec['ambient']:.3f}"}
    if spec["exposure"] > 0:
        values["FGM_Exposure.fx"] = {"ExposureBias": f"{spec['exposure']:.3f}"}
    if spec["contrast"] > 0:
        values["FGM_Contrast.fx"] = {"ContrastAmount": f"{spec['contrast']:.3f}"}
    if spec["bloom_amount"] > 0:
        values["FGM_Bloom.fx"] = {
            "PreprocessorDefinitions": f"BLOOM_TAPS={spec['bloom_taps']}",
            "BloomThreshold": f"{spec['bloom_threshold']:.3f}",
            "BloomAmount": f"{spec['bloom_amount']:.3f}",
        }
    if spec["reflect"] > 0:
        values["FGM_ReflectionsEnhance.fx"] = {
            "PreprocessorDefinitions": f"REFLECT_TAPS={spec['reflect_taps']}",
            "ReflectAmount": f"{spec['reflect']:.3f}",
        }
    return values


def write_png(path: Path, width: int, height: int, rgb: bytes) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(rgb[y * stride : (y + 1) * stride])
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def build_lut(path: Path, edition: str) -> None:
    size = LUT_SIZE
    width = size * size
    rgb = bytearray(width * size * 3)
    for blue in range(size):
        for green in range(size):
            for red in range(size):
                color = grade((red / (size - 1), green / (size - 1), blue / (size - 1)), edition)
                x = blue * size + red
                index = (green * width + x) * 3
                rgb[index : index + 3] = bytes(int(round(channel * 255)) for channel in color)
    write_png(path, width, size, bytes(rgb))


def preset_text(techniques: list[str], values: dict[str, dict[str, str]]) -> str:
    enabled = ",".join(techniques)
    sorting = enabled + "," + ",".join(OPTIONAL_OFF)
    lines = [f"Techniques={enabled}", f"TechniqueSorting={sorting}", ""]
    for shader, pairs in values.items():
        lines.append(f"[{shader}]")
        for key, value in pairs.items():
            lines.append(f"{key}={value}")
        lines.append("")
    return "\n".join(lines)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def manifest(edition: str, preset: str, folder: Path, files: list[tuple[str, str]]) -> dict:
    entries = []
    for source, destination in files:
        file_path = folder / source
        entries.append(
            {
                "source": source,
                "destination_dir": destination.rsplit("/", 1)[0],
                "destination": destination,
                "sha256": sha256_file(file_path),
                "bytes": file_path.stat().st_size,
                "backup_if_exists": True,
                "install_action": "backup_then_replace",
                "restore_on_uninstall": "restore_backup_or_delete",
            }
        )
    spec = LOOK[edition]
    return {
        "schema": 3,
        "package": f"fgm-{edition}",
        "version": PRODUCT_VERSION,
        "edition": edition,
        "aliases": {"ultra": ["quality"], "low": ["performance"]}.get(edition, []),
        "kind": "client-local",
        "preset": preset,
        "min_reshade": "5.0.0",
        "preferred_reshade": "6.8.0",
        "road_texture_px": spec["road_size"],
        "tokens": {
            "fivem_plugins": "%LOCALAPPDATA%\\FiveM\\FiveM.app\\plugins",
            "fivem_root": "%LOCALAPPDATA%\\FiveM\\FiveM.app",
            "fivem_plugins_explorer_name": "FiveM Application Data\\plugins",
        },
        "effects": {
            "screen_rain": "manual-toggle",
            "street_lamps": "local-approximation",
            "clear_view": "local-approximation",
            "vibrance": "selective",
            "damage_blood": "unavailable",
            "road_detail": "screen-space-original-texture",
            "world_texture_replacement": "unavailable",
            "film_grain": "optional-off",
            "chromatic_aberration": "optional-off",
            "graphics_settings": "backup-then-replace-existing-keys",
        },
        "install_policy": {
            "default": "backup_if_exists_then_replace",
            "created_when": "destination absent",
            "replaced_when": "destination exists",
            "recorded_in": "{fivem_root}/FGM-state.json",
            "backup_dir": "{fivem_root}/FGM-Backup/<data-hora>/",
        },
        "dependencies": [
            {
                "name": "ReShade",
                "author": "Patrick Mours (crosire)",
                "version": "6.8.0",
                "source": "https://reshade.me/downloads/ReShade_Setup_6.8.0.exe",
                "license": "BSD-3-Clause",
                "commercial_use": True,
                "redistribution": "license-allows-but-author-asks-not-to-bundle",
                "bundled": False,
                "acquire": "official-download-on-install",
                "min_version": "5.0.0",
            }
        ],
        "files": entries,
        "backup_files": [entry["destination"] for entry in entries],
        "restore_on_uninstall": [entry["destination"] for entry in entries],
        "runtime_managed": [
            "{fivem_plugins}/dxgi.dll",
            "{fivem_plugins}/d3d11.dll",
            "{fivem_plugins}/ReShade.ini",
        ],
        "do_not_touch": [
            "%LOCALAPPDATA%\\FiveM\\FiveM.app\\CitizenFX.ini",
            "{gta_root}\\update\\update.rpf",
            "{gta_root}\\GTA5.exe",
            "{fivem_root}\\FiveM.exe",
        ],
    }


def build_edition(edition: str) -> None:
    spec = LOOK[edition]
    folder = DIST / edition
    shader_dir = folder / "reshade-shaders" / "Shaders" / "FGM"
    texture_dir = folder / "reshade-shaders" / "Textures" / "FGM"
    road_dir = folder / "roads"
    if folder.exists():
        shutil.rmtree(folder)
    shader_dir.mkdir(parents=True)
    texture_dir.mkdir(parents=True)
    road_dir.mkdir(parents=True)
    lut_name = f"fgm_{edition}_lut.png"
    preset_name = f"FGM-{edition.capitalize()}.ini"
    for name in shader_list(spec):
        text = (SRC / name).read_text(encoding="utf-8")
        if name == "FGM_Lut.fx":
            text = text.replace("fgm_ultra_lut.png", lut_name)
        (shader_dir / name).write_text(text, encoding="utf-8")
    build_lut(texture_dir / lut_name, edition)
    road = gerar(spec["road_size"], seed={"ultra": 11, "high": 12, "medium": 13, "low": 14}[edition], cracks={"ultra": 1.0, "high": 0.85, "medium": 0.55, "low": 0.35}[edition])
    if not 0.42 <= media(road) <= 0.58:
        raise SystemExit(f"asfalto {edition} saiu da média neutra ({media(road):.3f})")
    write_png(texture_dir / "fgm_road.png", spec["road_size"], spec["road_size"], road)
    write_png(road_dir / "fgm_road.png", spec["road_size"], spec["road_size"], road)
    (road_dir / "LEIA-ME.txt").write_text(
        "\n".join(
            [
                f"Asfalto FGM {edition}, {spec['road_size']} px.",
                "Textura original gerada por src/roads/gerar_asfalto.py.",
                "Não é arquivo da Rockstar e não entra em update.rpf.",
                "O shader FGM_Roads usa a cópia em reshade-shaders/Textures/FGM/fgm_road.png.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    techniques = technique_list(spec)
    (folder / preset_name).write_text(preset_text(techniques, uniforms(edition, spec)), encoding="utf-8")
    packaged = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.name in {"manifest.json", "LEIA-ME.txt"}:
            continue
        if path.parent.name == "roads":
            continue
        source = path.relative_to(folder).as_posix()
        packaged.append((source, "{fivem_plugins}/" + source))
    (folder / "manifest.json").write_text(
        json.dumps(manifest(edition, preset_name, folder, packaged), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (folder / "LEIA-ME.txt").write_text(
        "\n".join(
            [
                f"FGM {edition} {PRODUCT_VERSION} — mod gráfico local.",
                "Não copie esta pasta para resources e não edite server.cfg.",
                "No Windows, use Instalar-Ultra.cmd, Instalar-High.cmd, Instalar-Medium.cmd ou Instalar-Low.cmd.",
                "Quality instala Ultra. Performance instala Low.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def launcher(args: str, script: str = "%~dp0Instalar-FGM.ps1") -> str:
    return "\r\n".join(
        [
            "@echo off",
            "powershell -NoProfile -ExecutionPolicy Bypass -File \"" + script + "\" -Command " + args,
            "if errorlevel 1 pause",
            "",
        ]
    )


def assemble_release() -> None:
    release = ROOT / "release" / f"FGM-v{PRODUCT_VERSION}"
    if release.exists():
        shutil.rmtree(release)
    old = ROOT / "release" / "FGM-v1.0.0"
    if old.exists():
        shutil.rmtree(old)
    titles = {"ultra": "Ultra", "high": "High", "medium": "Medium", "low": "Low"}
    manifests = release / "installer-manifests"
    manifests.mkdir(parents=True)
    for edition, title in titles.items():
        shutil.copytree(DIST / edition, release / title)
        shutil.copy2(DIST / edition / "manifest.json", manifests / f"{edition}.json")
    shutil.copytree(ROOT / "docs", release / "Docs")
    shutil.copytree(ROOT / "licenses", release / "Licenses")
    shutil.copytree(ROOT / "licenses", release / "licenses")
    installer = release / "Installer"
    installer.mkdir()
    for name in ("Instalar-FGM.ps1", "fgm-install-lib.ps1"):
        shutil.copy2(ROOT / "tools" / name, release / name)
        shutil.copy2(ROOT / "tools" / name, installer / name)
    shutil.copy2(ROOT / "src" / "settings" / "graphics.json", release / "graphics.json")
    shutil.copy2(ROOT / "src" / "settings" / "graphics.json", DIST / "graphics.json")
    runtime = release / "runtime"
    runtime.mkdir()
    shutil.copy2(ROOT / "tools" / "reshade-official.json", runtime / "reshade-official.json")
    shutil.copy2(ROOT / "tools" / "reshade-official.json", release / "reshade-official.json")
    commands = {
        "product": "FGM",
        "version": PRODUCT_VERSION,
        "entrypoint": "Instalar-FGM.ps1",
        "fivem_root": "%LOCALAPPDATA%\\FiveM\\FiveM.app",
        "plugins": "%LOCALAPPDATA%\\FiveM\\FiveM.app\\plugins",
        "state": "%LOCALAPPDATA%\\FiveM\\FiveM.app\\FGM-state.json",
        "backup": "%LOCALAPPDATA%\\FiveM\\FiveM.app\\FGM-Backup\\<data-hora>\\",
        "graphics": "%USERPROFILE%\\Documents\\Rockstar Games\\GTA V\\settings.xml",
        "commands": {
            "install_ultra": ["-Command", "install", "-Edition", "ultra"],
            "install_high": ["-Command", "install", "-Edition", "high"],
            "install_medium": ["-Command", "install", "-Edition", "medium"],
            "install_low": ["-Command", "install", "-Edition", "low"],
            "install_quality_alias": ["-Command", "install", "-Edition", "quality"],
            "install_performance_alias": ["-Command", "install", "-Edition", "performance"],
            "repair": ["-Command", "repair"],
            "uninstall": ["-Command", "uninstall"],
        },
    }
    (manifests / "commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
    launchers = {
        "Instalar-Ultra.cmd": "install -Edition ultra",
        "Instalar-High.cmd": "install -Edition high",
        "Instalar-Medium.cmd": "install -Edition medium",
        "Instalar-Low.cmd": "install -Edition low",
        "Instalar-Quality.cmd": "install -Edition quality",
        "Instalar-Performance.cmd": "install -Edition performance",
        "Desinstalar.cmd": "uninstall",
        "Reparar.cmd": "repair",
    }
    for filename, args in launchers.items():
        (release / filename).write_text(launcher(args), encoding="utf-8")
        (installer / filename).write_text(launcher(args, "%~dp0..\\Instalar-FGM.ps1"), encoding="utf-8")
    (release / "COMO-TESTAR.txt").write_text(
        "\n".join(
            [
                "FGM 2.0.0 — uma rodada no FiveM",
                "",
                "Feche o FiveM antes de instalar. A lista curta de teste está em Docs/TESTES.md.",
                "Ultra é o visual principal. Quality instala Ultra. Performance instala Low.",
                "FGM_Rain, grão e aberração cromática começam desligados.",
                "O ReShade 6.8.0 é baixado de https://reshade.me/ se ainda não houver um compatível.",
                "O binário não vem neste pacote.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"release/FGM-v{PRODUCT_VERSION} pronto")


def main() -> None:
    for stale in ("quality", "performance"):
        folder = DIST / stale
        if folder.exists():
            shutil.rmtree(folder)
    for edition in LOOK:
        build_edition(edition)
        print(f"dist/{edition} pronto ({LOOK[edition]['road_size']} px de asfalto)")
    assemble_release()


if __name__ == "__main__":
    main()
