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


# Centros usados pela prévia e pelas checagens. O anel do shader tem 18 px.
MARK = {
    "sodium": (70, 130),
    "window": (195, 95),
    "window_edge": (160, 95),
    "head": (360, 180),
    "neon": (30, 80),
    "red": (300, 60),
    "green": (340, 60),
    "amber": (400, 60),
    "blue": (450, 110),
    "street": (200, 240),
    "sunset": (260, 170),
}


def paint(color: list[float], x: int, y: int, cx: int, cy: int, radius: int, ink: tuple[float, float, float]) -> list[float]:
    if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= radius * radius:
        return list(ink)
    return color


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
                if 160 <= x <= 230 and 70 <= y <= 120:
                    color = [0.86, 0.63, 0.34]
                color = paint(color, x, y, 70, 130, 14, (0.42, 0.30, 0.12))
                color = paint(color, x, y, 70, 130, 7, (1.0, 0.70, 0.28))
                color = paint(color, x, y, 360, 180, 4, (0.96, 0.94, 0.82))
                color = paint(color, x, y, 30, 80, 5, (0.92, 0.12, 0.62))
                color = paint(color, x, y, 300, 60, 3, (0.93, 0.07, 0.05))
                color = paint(color, x, y, 340, 60, 3, (0.08, 0.78, 0.12))
                color = paint(color, x, y, 400, 60, 3, (0.95, 0.48, 0.05))
                color = paint(color, x, y, 450, 110, 4, (0.15, 0.28, 0.96))
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


def luma(color: tuple[float, float, float]) -> float:
    return 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]


def lamp_chroma(color: tuple[float, float, float]) -> float:
    # A mesma conta de FGM_Lamps.fx. Núcleo âmbar, sem farol branco nem neon.
    red, green, blue = color
    peak = max(red, green, blue)
    floorc = min(red, green, blue)
    sat = (peak - floorc) / max(peak, 0.001)
    bright = smoothstep(0.55, 0.75, luma(color))
    ratio = green / max(red, 0.001)
    sodium = smoothstep(0.55, 0.64, ratio) * (1.0 - smoothstep(0.84, 0.93, ratio))
    blue_def = smoothstep(0.16, 0.30, min(red, green) - blue)
    sat_ok = smoothstep(0.18, 0.32, sat) * (1.0 - smoothstep(0.70, 0.88, sat))
    return bright * sodium * blue_def * sat_ok


def apply_lamps(rgb: bytearray, width: int, height: int, taps: int, strength: float) -> bytearray:
    # Anel de 18 px. Quality usa 8 amostras; Performance usa as 4 cardeais.
    out = bytearray(rgb)
    if strength <= 0.001:
        return out
    offsets = [(1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)]
    if taps > 4:
        diagonal = 0.7071
        offsets += [(diagonal, diagonal), (-diagonal, diagonal), (diagonal, -diagonal), (-diagonal, -diagonal)]
    radius = 18.0
    for y in range(height):
        for x in range(width):
            index = (y * width + x) * 3
            color = tuple(channel / 255.0 for channel in rgb[index : index + 3])
            chroma = lamp_chroma(color)
            if chroma <= 0.001:
                continue
            around = 0.0
            for ox, oy in offsets:
                sx = min(width - 1, max(0, int(round(x + ox * radius))))
                sy = min(height - 1, max(0, int(round(y + oy * radius))))
                sample_index = (sy * width + sx) * 3
                sample = tuple(channel / 255.0 for channel in rgb[sample_index : sample_index + 3])
                around = max(around, luma(sample))
            isolated = smoothstep(0.22, 0.42, luma(color) - around)
            amount = chroma * isolated * strength
            if amount <= 0.0:
                continue
            tone = luma(color)
            mixed = [channel * (1.0 - amount) + tone * amount for channel in color]
            out[index : index + 3] = bytes(int(round(min(1.0, max(0.0, channel)) * 255)) for channel in mixed)
    return out


def apply_grade(rgb: bytearray, width: int, height: int, edition: str) -> bytearray:
    out = bytearray(len(rgb))
    for i in range(0, len(rgb), 3):
        src = tuple(channel / 255.0 for channel in rgb[i : i + 3])
        graded = grade(src, edition)
        out[i : i + 3] = bytes(int(round(channel * 255)) for channel in graded)
    return out


def rain_mask(x: int, y: int, width: int, height: int, layers: int) -> float:
    # A prévia mostra o efeito depois que o jogador liga FGM_Rain.
    # O brilho da cena não entra: não há detecção de clima.
    u = x / (width - 1)
    v = y / (height - 1)
    edge = smoothstep(0.15, 0.48, ((u - 0.5) ** 2 * 1.05 + (v - 0.46) ** 2) ** 0.5)
    cell = int(u * 28) + int(v * 18) * 13
    bead = 1.0 if (cell % 11 == 0 and (int(u * 90) + int(v * 40)) % 7 == 0) else 0.0
    if layers > 1 and cell % 17 == 0:
        bead = max(bead, 0.7)
    return bead * edge


def apply_rain(rgb: bytearray, width: int, height: int, strength: float, layers: int) -> tuple[bytearray, int]:
    out = bytearray(rgb)
    hits = 0
    for y in range(height):
        for x in range(width):
            index = (y * width + x) * 3
            color = [channel / 255.0 for channel in rgb[index : index + 3]]
            mask = rain_mask(x, y, width, height, layers) * strength
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


def pixel(buf: bytearray, width: int, x: int, y: int) -> tuple[float, float, float]:
    index = (y * width + x) * 3
    return tuple(channel / 255.0 for channel in buf[index : index + 3])


def yellow_gap(color: tuple[float, float, float]) -> float:
    return (color[0] + color[1]) * 0.5 - color[2]


def max_delta(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return max(abs(a[i] - b[i]) for i in range(3))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    width, height = 480, 270
    night = scene(width, height, True)
    day = scene(width, height, False)
    frames = {}
    lamps = {}
    for edition, strength, layers, taps in (
        ("quality", 0.72, 2, 8),
        ("performance", 0.30, 1, 4),
    ):
        day_grade = apply_grade(day, width, height, edition)
        night_grade = apply_grade(night, width, height, edition)
        day_lamps = apply_lamps(day_grade, width, height, taps, 0.88)
        night_lamps = apply_lamps(night_grade, width, height, taps, 0.88)
        rainy, _hits = apply_rain(night_grade, width, height, strength, layers)
        frames[edition] = (day_grade, night_grade, rainy)
        lamps[edition] = night_lamps
        write_png(OUT / f"preview-{edition}-dia.png", width * 2 + 8, height, panel(day, day_lamps, width, height))
        write_png(OUT / f"preview-{edition}-noite.png", width * 2 + 8, height, panel(night, night_lamps, width, height))
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
    _off, off_hits = apply_rain(night_q, width, height, 0.0, 2)
    _day_rain, day_hits = apply_rain(frames["quality"][0], width, height, 0.72, 2)
    _night_rain, night_hits = apply_rain(night_q, width, height, 0.72, 2)
    _light, light_hits = apply_rain(night_q, width, height, 0.30, 1)
    if off_hits != 0:
        raise SystemExit(f"força zero deveria deixar a tela limpa ({off_hits})")
    if day_hits == 0 or night_hits == 0:
        raise SystemExit(f"com a técnica ligada as gotas precisam aparecer de dia ({day_hits}) e de noite ({night_hits})")
    if day_hits != night_hits:
        raise SystemExit(f"a gota não pode depender do brilho da cena (noite {night_hits}, dia {day_hits})")
    if night_hits <= light_hits:
        raise SystemExit(f"chuva mais forte deveria marcar mais pixels ({night_hits}) do que a fraca ({light_hits})")
    center = region_hits(width, height, night_q, rainy, True)
    border = region_hits(width, height, night_q, rainy, False)
    if border <= center:
        raise SystemExit(f"gotas deveriam preferir a borda ({border}) ao centro ({center})")
    sx, sy = MARK["sodium"]
    before = pixel(night_q, width, sx, sy)
    after_q = pixel(lamps["quality"], width, sx, sy)
    after_p = pixel(lamps["performance"], width, sx, sy)
    if yellow_gap(after_q) >= yellow_gap(before) * 0.45:
        raise SystemExit(f"o poste Quality continuou amarelo ({yellow_gap(before):.3f} -> {yellow_gap(after_q):.3f})")
    if abs(luma(after_q) - luma(before)) > 0.02:
        raise SystemExit("o branco do poste mudou a luminância e alimentaria o bloom")
    if after_q[2] > luma(after_q) + 0.02 or after_q[2] > after_q[0] + 0.02:
        raise SystemExit(f"o poste ficou azulado {tuple(round(c, 3) for c in after_q)}")
    if max_delta(after_q, after_p) > 0.03:
        raise SystemExit("Quality e Performance precisam do mesmo branco no núcleo do poste")
    off = apply_lamps(night_q, width, height, 8, 0.0)
    if pixel(off, width, sx, sy) != before:
        raise SystemExit("Branco dos postes em zero deveria preservar o âmbar")
    protected = ("window", "window_edge", "head", "neon", "red", "green", "amber", "blue", "street")
    for name in protected:
        x, y = MARK[name]
        delta = max_delta(pixel(night_q, width, x, y), pixel(lamps["quality"], width, x, y))
        if delta > 0.03:
            raise SystemExit(f"{name} não deveria ser neutralizado ({delta:.3f})")
    sunset = MARK["sunset"]
    day_q = frames["quality"][0]
    day_lamps = apply_lamps(day_q, width, height, 8, 0.88)
    sunset_delta = max_delta(pixel(day_q, width, *sunset), pixel(day_lamps, width, *sunset))
    if sunset_delta > 0.03:
        raise SystemExit(f"o pôr do sol mudou de tom ({sunset_delta:.3f})")
    print(
        f"previews ok desligado={off_hits} noite_gotas={night_hits} dia_gotas={day_hits} "
        f"fraca={light_hits} borda={border} centro={center} "
        f"poste={tuple(round(c, 3) for c in after_q)}"
    )


if __name__ == "__main__":
    main()
