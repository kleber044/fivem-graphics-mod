#!/usr/bin/env python3
"""Gera dist/quality e dist/performance a partir de src/ e valida o pacote."""

from __future__ import annotations

import hashlib
import json
import shutil
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "shaders"
DIST = ROOT / "dist"
LUT_SIZE = 32
PRODUCT_VERSION = "1.0.0"

EDITIONS = {
    "quality": {
        "preset": "FGM-Quality.ini",
        "lut": "fgm_quality_lut.png",
        "techniques": [
            "FGM_Lut@FGM_Lut.fx",
            "FGM_ClearView@FGM_ClearView.fx",
            "FGM_Bloom@FGM_Bloom.fx",
            "FGM_Lamps@FGM_Lamps.fx",
            "FGM_Sharp@FGM_Sharp.fx",
            "FGM_Vignette@FGM_Vignette.fx",
        ],
        "uniforms": {
            "FGM_Lut.fx": {"ColorVibrance": "0.360", "PlantExtra": "0.280"},
            "FGM_ClearView.fx": {"ClearLevel": "3"},
            "FGM_Lamps.fx": {"PreprocessorDefinitions": "LAMP_TAPS=8", "LampLevel": "3"},
            "FGM_Bloom.fx": {"BloomThreshold": "0.800", "BloomAmount": "0.180"},
            "FGM_Sharp.fx": {"SharpStrength": "0.340"},
            "FGM_Vignette.fx": {"VignetteAmount": "0.160"},
            "FGM_Rain.fx": {"RainStrength": "0.720", "RainLayers": "2", "RainDistort": "1.000"},
        },
        "shaders": [
            "FGM.fxh",
            "FGM_Lut.fx",
            "FGM_ClearView.fx",
            "FGM_Lamps.fx",
            "FGM_Bloom.fx",
            "FGM_Sharp.fx",
            "FGM_Vignette.fx",
            "FGM_Rain.fx",
        ],
    },
    "performance": {
        "preset": "FGM-Performance.ini",
        "lut": "fgm_performance_lut.png",
        "techniques": [
            "FGM_Lut@FGM_Lut.fx",
            "FGM_ClearView@FGM_ClearView.fx",
            "FGM_Lamps@FGM_Lamps.fx",
            "FGM_Sharp@FGM_Sharp.fx",
            "FGM_Vignette@FGM_Vignette.fx",
        ],
        "uniforms": {
            "FGM_Lut.fx": {"ColorVibrance": "0.220", "PlantExtra": "0.140"},
            "FGM_ClearView.fx": {"ClearLevel": "2"},
            "FGM_Lamps.fx": {"PreprocessorDefinitions": "LAMP_TAPS=4", "LampLevel": "2"},
            "FGM_Sharp.fx": {"SharpStrength": "0.140"},
            "FGM_Vignette.fx": {"VignetteAmount": "0.060"},
            "FGM_Rain.fx": {"RainStrength": "0.300", "RainLayers": "1", "RainDistort": "0.350"},
        },
        "shaders": [
            "FGM.fxh",
            "FGM_Lut.fx",
            "FGM_ClearView.fx",
            "FGM_Lamps.fx",
            "FGM_Sharp.fx",
            "FGM_Vignette.fx",
            "FGM_Rain.fx",
        ],
    },
}


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    span = edge1 - edge0
    if span == 0:
        return 0.0
    t = min(1.0, max(0.0, (x - edge0) / span))
    return t * t * (3.0 - 2.0 * t)


def grade(rgb: tuple[float, float, float], edition: str) -> tuple[float, float, float]:
    # Curva em sRGB. O contraste afrouxa no preto para a sombra não virar buraco.
    quality = edition == "quality"
    if quality:
        contrast = 1.11
        shadow_scale = 0.060
        shadow_tint = (-0.016, -0.002, 0.012)
        highlight_tint = (0.018, 0.006, -0.008)
        sky_push = 0.028
        sun_push = 0.032
    else:
        contrast = 1.055
        shadow_scale = 0.028
        shadow_tint = (-0.008, -0.001, 0.006)
        highlight_tint = (0.010, 0.003, -0.004)
        sky_push = 0.014
        sun_push = 0.016
    x = list(rgb)
    lum = 0.2126 * x[0] + 0.7152 * x[1] + 0.0722 * x[2]
    shadow = smoothstep(0.50, 0.05, lum)
    highlight = smoothstep(0.62, 0.92, lum)
    curved = []
    for channel in x:
        pulled = (channel - 0.50) * contrast + 0.50
        weight = smoothstep(0.0, 0.25, channel)
        curved.append(channel * (1.0 - weight) + pulled * weight)
    x = [channel * (1.0 - shadow_scale * shadow) for channel in curved]
    green_dom = max(0.0, x[1] - max(x[0], x[2]))
    plant = smoothstep(0.02, 0.14, green_dom)
    blue_dom = max(0.0, x[2] - max(x[0], x[1]))
    sky = smoothstep(0.02, 0.16, blue_dom) * smoothstep(0.35, 0.80, lum)
    warm_dom = max(0.0, x[0] - x[2]) * max(0.0, x[0] - x[1] * 0.85)
    sunset = smoothstep(0.03, 0.16, warm_dom) * smoothstep(0.20, 0.70, lum)
    tint_scale = 1.0 - 0.75 * plant
    x = [
        channel + shadow * shadow_tint[i] * tint_scale + highlight * highlight_tint[i]
        for i, channel in enumerate(x)
    ]
    x[0] += sun_push * sunset - sky_push * 0.35 * sky
    x[1] += sun_push * 0.25 * sunset
    x[2] += sky_push * sky - sun_push * 0.45 * sunset
    return tuple(min(1.0, max(0.0, channel)) for channel in x)


def vibrance(rgb: tuple[float, float, float], amount: float, plant_extra: float) -> tuple[float, float, float]:
    # A mesma conta de FGM_Vibrant em FGM_Lut.fx.
    red, green, blue = rgb
    tone = 0.2126 * red + 0.7152 * green + 0.0722 * blue
    peak = max(red, green, blue)
    floorc = min(red, green, blue)
    sat = (peak - floorc) / max(peak, 0.001)
    shadow = smoothstep(0.08, 0.22, tone)
    not_white = 1.0 - smoothstep(0.78, 0.94, tone)
    headroom = 1.0 - smoothstep(0.42, 0.70, sat)
    rg = red - green
    gb = green - blue
    skin = smoothstep(0.04, 0.12, rg) * (1.0 - smoothstep(0.18, 0.32, rg))
    skin *= smoothstep(0.03, 0.10, gb)
    skin *= smoothstep(0.20, 0.40, tone) * (1.0 - smoothstep(0.62, 0.82, tone))
    skin *= smoothstep(0.10, 0.22, sat) * (1.0 - smoothstep(0.45, 0.65, sat))
    protect = 1.0 - 0.80 * min(1.0, max(0.0, skin))
    plant = smoothstep(0.03, 0.14, green - max(red, blue))
    plant *= 1.0 - smoothstep(0.55, 0.80, sat)
    gain = amount * shadow * not_white * headroom * protect * (1.0 + plant_extra * plant)
    out = [tone + (channel - tone) * (1.0 + gain) for channel in rgb]
    out_peak = max(out)
    if out_peak > 1.0:
        head = max(out_peak - tone, 0.001)
        room = max(1.0 - tone, 0.0)
        out = [tone + (channel - tone) * (room / head) for channel in out]
    return tuple(min(1.0, max(0.0, channel)) for channel in out)


def clear_pixel(rgb: tuple[float, float, float], level: int) -> tuple[float, float, float]:
    # A mesma conta de FGM_ClearView.fx. Sem amostra extra.
    strength = (0.0, 0.12, 0.22, 0.34)[max(0, min(3, int(level)))]
    if strength <= 0.0:
        return rgb
    red, green, blue = rgb
    tone = 0.2126 * red + 0.7152 * green + 0.0722 * blue
    peak = max(red, green, blue)
    floorc = min(red, green, blue)
    sat = (peak - floorc) / max(peak, 0.001)
    gray = 1.0 - smoothstep(0.06, 0.22, sat)
    band = smoothstep(0.40, 0.55, tone) * (1.0 - smoothstep(0.76, 0.88, tone))
    veil = gray * band * strength
    if veil <= 0.001:
        return rgb
    scale = 1.0 / max(1.0 - veil, 0.001)
    return tuple(min(1.0, max(0.0, (channel - veil) * scale)) for channel in rgb)


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
    height = size
    rgb = bytearray(width * height * 3)
    for blue in range(size):
        for green in range(size):
            for red in range(size):
                color = grade((red / (size - 1), green / (size - 1), blue / (size - 1)), edition)
                x = blue * size + red
                y = green
                index = (y * width + x) * 3
                rgb[index : index + 3] = bytes(int(round(channel * 255)) for channel in color)
    write_png(path, width, height, bytes(rgb))


def preset_text(edition: str, spec: dict) -> str:
    # Techniques= é o que roda. FGM_Rain fica fora dessa lista.
    # TechniqueSorting= só o oferece no overlay, desmarcado, para o jogador ligar.
    enabled = ",".join(spec["techniques"])
    sorting = enabled + ",FGM_Rain@FGM_Rain.fx"
    lines = [
        f"Techniques={enabled}",
        f"TechniqueSorting={sorting}",
        "",
    ]
    for shader, values in spec["uniforms"].items():
        lines.append(f"[{shader}]")
        for key, value in values.items():
            lines.append(f"{key}={value}")
        lines.append("")
    return "\n".join(lines)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def manifest(edition: str, spec: dict, folder: Path, files: list[tuple[str, str]]) -> dict:
    entries = []
    for source, destination in files:
        destination_dir = destination.rsplit("/", 1)[0]
        file_path = folder / source
        entries.append(
            {
                "source": source,
                "destination_dir": destination_dir,
                "destination": destination,
                "sha256": sha256_file(file_path),
                "bytes": file_path.stat().st_size,
                "backup_if_exists": True,
                "install_action": "backup_then_replace",
                "restore_on_uninstall": "restore_backup_or_delete",
            }
        )
    return {
        "schema": 2,
        "package": f"fgm-{edition}",
        "version": PRODUCT_VERSION,
        "edition": edition,
        "kind": "client-local",
        "preset": spec["preset"],
        "min_reshade": "5.0.0",
        "preferred_reshade": "6.8.0",
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
    spec = EDITIONS[edition]
    folder = DIST / edition
    shader_dir = folder / "reshade-shaders" / "Shaders" / "FGM"
    texture_dir = folder / "reshade-shaders" / "Textures" / "FGM"
    if folder.exists():
        shutil.rmtree(folder)
    shader_dir.mkdir(parents=True)
    texture_dir.mkdir(parents=True)

    for name in spec["shaders"]:
        text = (SRC / name).read_text(encoding="utf-8")
        if name == "FGM_Lut.fx":
            text = text.replace("fgm_quality_lut.png", spec["lut"])
        (shader_dir / name).write_text(text, encoding="utf-8")

    build_lut(texture_dir / spec["lut"], edition)
    (folder / spec["preset"]).write_text(preset_text(edition, spec), encoding="utf-8")

    packaged = []
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            source = path.relative_to(folder).as_posix()
            destination = "{fivem_plugins}/" + source
            packaged.append((source, destination))
    (folder / "manifest.json").write_text(
        json.dumps(manifest(edition, spec, folder, packaged), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    readme = folder / "LEIA-ME.txt"
    readme.write_text(
        "\n".join(
            [
                f"FGM {edition} {PRODUCT_VERSION} — mod gráfico local.",
                "Não copie esta pasta para resources e não edite server.cfg.",
                "No Windows, use o Instalar-FGM.ps1 da pasta release/FGM-v1.0.0.",
                "Este manifesto lista origem, destino, backup e hash de cada arquivo.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def assemble_release() -> None:
    release = ROOT / "release" / f"FGM-v{PRODUCT_VERSION}"
    if release.exists():
        shutil.rmtree(release)
    mapping = {"quality": "Quality", "performance": "Performance"}
    manifests = release / "installer-manifests"
    manifests.mkdir(parents=True)
    for edition, title in mapping.items():
        shutil.copytree(DIST / edition, release / title)
        shutil.copy2(DIST / edition / "manifest.json", manifests / f"{edition}.json")
    for name in ("docs", "licenses"):
        shutil.copytree(ROOT / name, release / name)
    runtime = release / "runtime"
    runtime.mkdir()
    shutil.copy2(ROOT / "tools" / "reshade-official.json", runtime / "reshade-official.json")
    shutil.copy2(ROOT / "tools" / "reshade-official.json", release / "reshade-official.json")
    shutil.copy2(ROOT / "tools" / "Instalar-FGM.ps1", release / "Instalar-FGM.ps1")
    shutil.copy2(ROOT / "tools" / "fgm-install-lib.ps1", release / "fgm-install-lib.ps1")
    commands = {
        "product": "FGM",
        "version": PRODUCT_VERSION,
        "entrypoint": "Instalar-FGM.ps1",
        "fivem_root": "%LOCALAPPDATA%\\FiveM\\FiveM.app",
        "plugins": "%LOCALAPPDATA%\\FiveM\\FiveM.app\\plugins",
        "state": "%LOCALAPPDATA%\\FiveM\\FiveM.app\\FGM-state.json",
        "backup": "%LOCALAPPDATA%\\FiveM\\FiveM.app\\FGM-Backup\\<data-hora>\\",
        "commands": {
            "install_quality": ["-Command", "install", "-Edition", "quality"],
            "install_performance": ["-Command", "install", "-Edition", "performance"],
            "switch_quality": ["-Command", "switch", "-Edition", "quality"],
            "switch_performance": ["-Command", "switch", "-Edition", "performance"],
            "repair": ["-Command", "repair"],
            "uninstall": ["-Command", "uninstall"],
        },
    }
    (manifests / "commands.json").write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
    launchers = {
        "Instalar-Quality.cmd": 'install -Edition quality',
        "Instalar-Performance.cmd": 'install -Edition performance',
        "Desinstalar.cmd": "uninstall",
        "Reparar.cmd": "repair",
    }
    for filename, args in launchers.items():
        (release / filename).write_text(
            "\r\n".join(
                [
                    "@echo off",
                    "powershell -NoProfile -ExecutionPolicy Bypass -File \"%~dp0Instalar-FGM.ps1\" -Command " + args,
                    "if errorlevel 1 pause",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    (release / "COMO-TESTAR.txt").write_text(
        "\n".join(
            [
                "FGM 1.0.0 — teste no Windows",
                "",
                "1. Feche o FiveM.",
                "2. Dê dois cliques em Instalar-Quality.cmd ou Instalar-Performance.cmd.",
                "3. Abra o FiveM e entre num servidor que permita ReShade.",
                "4. O preset da edição escolhida já fica selecionado.",
                "5. Para trocar, feche o jogo e execute a outra instalação.",
                "6. Desinstalar.cmd restaura o backup e remove só o que o FGM criou.",
                "7. FGM_Rain começa desligado. Não há gotas no menu nem em clima limpo.",
                "8. Quando chover no jogo, abra o ReShade com Home e marque FGM_Rain.",
                "9. Força das gotas sobe a intensidade. Desmarque a técnica quando a chuva acabar.",
                "10. Quality abre em White LED, horizonte forte e vivacidade 0,36.",
                "11. Performance abre em Neutral, horizonte médio e vivacidade 0,22.",
                "12. FGM_Rain continua desmarcado até você ligar na chuva.",
                "",
                "O ReShade 6.8.0 é baixado de https://reshade.me/ durante a instalação.",
                "O binário não vem neste pacote.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"release/FGM-v{PRODUCT_VERSION} pronto")


def main() -> None:
    for edition in EDITIONS:
        build_edition(edition)
        print(f"dist/{edition} pronto")
    assemble_release()


if __name__ == "__main__":
    main()
