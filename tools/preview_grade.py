#!/usr/bin/env python3
"""Gera prévias da grade e das gotas sem abrir o GTA. A mesma matemática da LUT."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

from build_dist import grade, smoothstep

OUT = Path("/opt/cursor/artifacts")
SIZE = 32


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


def scene(width: int, height: int, night: bool) -> bytearray:
    rgb = bytearray(width * height * 3)
    for y in range(height):
        for x in range(width):
            u = x / (width - 1)
            v = y / (height - 1)
            if night:
                sky = (0.03 + 0.04 * (1.0 - v), 0.04 + 0.05 * (1.0 - v), 0.08 + 0.06 * (1.0 - v))
                street = (0.08, 0.08, 0.09)
                color = [sky[i] * (1.0 - v) + street[i] * v for i in range(3)]
                # poste e farol, já claros na imagem do jogo
                if abs(u - 0.22) < 0.012 and v > 0.35:
                    color = [1.0, 0.86, 0.55]
                if abs(u - 0.72) < 0.04 and abs(v - 0.62) < 0.015:
                    color = [0.95, 0.93, 0.8]
            else:
                sky = (0.45 + 0.15 * (1.0 - v), 0.62, 0.82)
                ground = (0.35, 0.36, 0.32)
                color = [sky[i] * (1.0 - v) + ground[i] * v for i in range(3)]
                if 0.55 < v < 0.72 and 0.40 < u < 0.70:
                    warm = (0.95, 0.55, 0.25)  # faixa de pôr do sol já presente no quadro
                    color = [color[i] * 0.35 + warm[i] * 0.65 for i in range(3)]
            index = (y * width + x) * 3
            rgb[index : index + 3] = bytes(int(min(255, max(0, channel * 255))) for channel in color)
    return rgb


def apply_grade(rgb: bytearray, width: int, height: int, edition: str) -> bytearray:
    out = bytearray(len(rgb))
    for i in range(0, len(rgb), 3):
        src = tuple(channel / 255.0 for channel in rgb[i : i + 3])
        graded = grade(src, edition)
        out[i : i + 3] = bytes(int(round(channel * 255)) for channel in graded)
    return out


def rain_mask(x: int, y: int, width: int, height: int, luma: float, saturation: float, layers: int) -> float:
    u = x / (width - 1)
    v = y / (height - 1)
    dark = max(0.0, min(1.0, (0.46 - luma) / 0.46))
    dull = max(0.0, min(1.0, (0.42 - saturation) / 0.42))
    weather = dark * (0.45 + 0.55 * dull)
    edge = smoothstep(0.15, 0.48, ((u - 0.5) ** 2 * 1.05 + (v - 0.46) ** 2) ** 0.5)
    # gota estável para a prévia (sem tempo)
    cell = int(u * 28) + int(v * 18) * 13
    bead = 1.0 if (cell % 11 == 0 and (int(u * 90) + int(v * 40)) % 7 == 0) else 0.0
    if layers > 1 and cell % 17 == 0:
        bead = max(bead, 0.7)
    return bead * weather * edge


def apply_rain(rgb: bytearray, width: int, height: int, strength: float, layers: int) -> tuple[bytearray, int]:
    out = bytearray(rgb)
    hits = 0
    for y in range(height):
        for x in range(width):
            index = (y * width + x) * 3
            color = [channel / 255.0 for channel in rgb[index : index + 3]]
            luma = 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]
            peak = max(color)
            floorc = min(color)
            saturation = (peak - floorc) / max(peak, 0.001)
            mask = rain_mask(x, y, width, height, luma, saturation, layers) * strength
            if mask > 0.08:
                hits += 1
                wet = (0.78, 0.84, 0.90)
                mixed = [color[i] * (1.0 - mask * 0.55) + wet[i] * (mask * 0.55) for i in range(3)]
                out[index : index + 3] = bytes(int(round(min(1.0, channel) * 255)) for channel in mixed)
    return out, hits


def panel(left: bytearray, right: bytearray, width: int, height: int) -> bytes:
    gap = 8
    out_w = width * 2 + gap
    rgb = bytearray(out_w * height * 3)
    for y in range(height):
        for x in range(width):
            src = (y * width + x) * 3
            dst = (y * out_w + x) * 3
            rgb[dst : dst + 3] = left[src : src + 3]
            dst = (y * out_w + width + gap + x) * 3
            rgb[dst : dst + 3] = right[src : src + 3]
    return bytes(rgb)


def region_hits(width: int, height: int, before: bytearray, after: bytearray, center: bool) -> int:
    hits = 0
    for y in range(height):
        for x in range(width):
            u = x / (width - 1)
            v = y / (height - 1)
            edge = ((u - 0.5) ** 2 + (v - 0.46) ** 2) ** 0.5
            inside = edge < 0.18 if center else edge > 0.34
            if not inside:
                continue
            index = (y * width + x) * 3
            if before[index : index + 3] != after[index : index + 3]:
                hits += 1
    return hits


def mean(buf: bytearray) -> float:
    return sum(buf) / len(buf)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    width, height = 480, 270
    night = scene(width, height, True)
    day = scene(width, height, False)
    frames = {}
    for edition, strength, layers in (("quality", 0.72, 2), ("performance", 0.30, 1)):
        day_grade = apply_grade(day, width, height, edition)
        night_grade = apply_grade(night, width, height, edition)
        rainy, _hits = apply_rain(night_grade, width, height, strength, layers)
        frames[edition] = (day_grade, night_grade, rainy)
        write_png(OUT / f"preview-{edition}-dia.png", width * 2 + 8, height, panel(day, day_grade, width, height))
        write_png(OUT / f"preview-{edition}-noite.png", width * 2 + 8, height, panel(night, night_grade, width, height))
        write_png(OUT / f"preview-{edition}-chuva.png", width * 2 + 8, height, panel(night_grade, rainy, width, height))
    night_q = frames["quality"][1]
    night_p = frames["performance"][1]
    if mean(night_q) >= mean(night):
        raise SystemExit("a grade Quality não escureceu a cena noturna")
    if mean(night_q) < mean(night) * 0.80:
        raise SystemExit("a grade Quality escureceu a noite além do leve")
    if mean(night_p) >= mean(night) or mean(night_p) < mean(night_q):
        raise SystemExit("a noite Performance deveria ficar entre o original e a Quality")
    rainy = frames["quality"][2]
    _day_rain, day_hits = apply_rain(frames["quality"][0], width, height, 0.72, 2)
    _night_rain, night_hits = apply_rain(night_q, width, height, 0.72, 2)
    if night_hits <= day_hits:
        raise SystemExit(f"chuva deveria marcar mais a noite ({night_hits}) do que o dia ({day_hits})")
    center = region_hits(width, height, night_q, rainy, True)
    border = region_hits(width, height, night_q, rainy, False)
    if border <= center:
        raise SystemExit(f"gotas deveriam preferir a borda ({border}) ao centro ({center})")
    print(f"previews ok noite_gotas={night_hits} dia_gotas={day_hits} borda={border} centro={center}")


if __name__ == "__main__":
    main()
