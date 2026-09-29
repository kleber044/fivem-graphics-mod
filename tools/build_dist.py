#!/usr/bin/env python3
"""Gera dist/quality e dist/performance a partir de src/ e valida o pacote."""

from __future__ import annotations

import json
import shutil
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "shaders"
DIST = ROOT / "dist"
LUT_SIZE = 32

EDITIONS = {
    "quality": {
        "preset": "FGM-Quality.ini",
        "lut": "fgm_quality_lut.png",
        "techniques": [
            "FGM_Lut@FGM_Lut.fx",
            "FGM_Bloom@FGM_Bloom.fx",
            "FGM_Sharp@FGM_Sharp.fx",
            "FGM_Vignette@FGM_Vignette.fx",
            "FGM_Rain@FGM_Rain.fx",
        ],
        "uniforms": {
            "FGM_Bloom.fx": {"BloomThreshold": "0.780", "BloomAmount": "0.160"},
            "FGM_Sharp.fx": {"SharpStrength": "0.380"},
            "FGM_Vignette.fx": {"VignetteAmount": "0.200"},
            "FGM_Rain.fx": {"RainStrength": "0.800", "RainLayers": "2"},
        },
        "shaders": [
            "FGM.fxh",
            "FGM_Lut.fx",
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
            "FGM_Sharp@FGM_Sharp.fx",
            "FGM_Vignette@FGM_Vignette.fx",
            "FGM_Rain@FGM_Rain.fx",
        ],
        "uniforms": {
            "FGM_Sharp.fx": {"SharpStrength": "0.160"},
            "FGM_Vignette.fx": {"VignetteAmount": "0.080"},
            "FGM_Rain.fx": {"RainStrength": "0.400", "RainLayers": "1"},
        },
        "shaders": [
            "FGM.fxh",
            "FGM_Lut.fx",
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
    # Curva em sRGB, o mesmo espaço em que o shader lê o quadro.
    # O contraste não chega no preto: abaixo de 0,25 a curva volta para a cor original.
    if edition == "quality":
        contrast = 1.08
        shadow_scale = 0.06
        shadow_tint = (-0.016, -0.004, 0.014)
        highlight_tint = (0.028, 0.010, -0.016)
        saturation = 0.93
    else:
        contrast = 1.04
        shadow_scale = 0.03
        shadow_tint = (-0.008, -0.002, 0.007)
        highlight_tint = (0.014, 0.005, -0.008)
        saturation = 0.96
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
    x = [channel + shadow * shadow_tint[i] + highlight * highlight_tint[i] for i, channel in enumerate(x)]
    luma = 0.2126 * x[0] + 0.7152 * x[1] + 0.0722 * x[2]
    x = [luma + (channel - luma) * saturation for channel in x]
    return tuple(min(1.0, max(0.0, channel)) for channel in x)


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
    techniques = ",".join(spec["techniques"])
    lines = [
        f"Techniques={techniques}",
        f"TechniqueSorting={techniques}",
        "",
    ]
    for shader, values in spec["uniforms"].items():
        lines.append(f"[{shader}]")
        for key, value in values.items():
            lines.append(f"{key}={value}")
        lines.append("")
    return "\n".join(lines)


def manifest(edition: str, spec: dict, files: list[tuple[str, str]]) -> dict:
    entries = []
    for source, destination in files:
        destination_dir = destination.rsplit("/", 1)[0]
        entries.append(
            {
                "source": source,
                "destination_dir": destination_dir,
                "destination": destination,
                "backup_if_exists": True,
                "restore_on_uninstall": "restore_backup_or_delete",
            }
        )
    return {
        "schema": 1,
        "package": f"fgm-{edition}",
        "version": "1.0.0",
        "edition": edition,
        "kind": "client-local",
        "preset": spec["preset"],
        "tokens": {
            "fivem_plugins": "%LOCALAPPDATA%\\FiveM\\FiveM.app\\plugins",
            "fivem_plugins_explorer_name": "FiveM Application Data\\plugins",
        },
        "external_dependencies": [
            {
                "name": "ReShade",
                "bundled": False,
                "required_files_not_shipped": ["dxgi.dll", "ReShade.ini"],
            }
        ],
        "files": entries,
        "backup_files": [entry["destination"] for entry in entries],
        "restore_on_uninstall": [entry["destination"] for entry in entries],
        "do_not_touch": [
            "{fivem_plugins}\\ReShade.ini",
            "{fivem_plugins}\\dxgi.dll",
            "{fivem_plugins}\\d3d11.dll",
            "%LOCALAPPDATA%\\FiveM\\FiveM.app\\CitizenFX.ini",
            "{gta_root}\\update\\update.rpf",
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
        json.dumps(manifest(edition, spec, packaged), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    readme = folder / "LEIA-ME.txt"
    readme.write_text(
        "\n".join(
            [
                f"FGM {edition} — mod gráfico local para o PC do jogador.",
                "Não é resource de servidor. Não copie esta pasta para resources.",
                "Instale o ReShade oficial na pasta plugins do FiveM e depois copie",
                "os arquivos listados em manifest.json para os destinos indicados.",
                "Leia docs/INSTALACAO.md no repositório antes de usar.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    for edition in EDITIONS:
        build_edition(edition)
        print(f"dist/{edition} pronto")


if __name__ == "__main__":
    main()
