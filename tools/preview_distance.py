#!/usr/bin/env python3
"""Prévia do Ultra na distância: montanha, mata, horizonte, carro, céu e entardecer.

A mesma matemática de tools/fgm_color.py. Não é uma captura do GTA.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

from fgm_color import LOOK, apply_color, clear_pixel, luma, saturation

OUT = Path("/opt/cursor/artifacts")
WIDTH = 220
HEIGHT = 120


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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def blank() -> bytearray:
    return bytearray(WIDTH * HEIGHT * 3)


def put(buf: bytearray, x: int, y: int, color: tuple[float, float, float]) -> None:
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return
    index = (y * WIDTH + x) * 3
    buf[index : index + 3] = bytes(int(round(min(1.0, max(0.0, channel)) * 255)) for channel in color)


def fill(buf: bytearray, x0: int, y0: int, x1: int, y1: int, color: tuple[float, float, float]) -> None:
    for y in range(y0, y1):
        for x in range(x0, x1):
            put(buf, x, y, color)


def pixel(buf: bytearray, x: int, y: int) -> tuple[float, float, float]:
    index = (y * WIDTH + x) * 3
    return tuple(channel / 255.0 for channel in buf[index : index + 3])


def grade_frame(src: bytearray) -> bytearray:
    spec = LOOK["ultra"]
    out = bytearray(len(src))
    for index in range(0, len(src), 3):
        color = tuple(channel / 255.0 for channel in src[index : index + 3])
        graded = apply_color(color, "ultra", 1.0)
        graded = clear_pixel(graded, spec["clear_day"], spec["clear_night"])
        out[index : index + 3] = bytes(int(round(min(1.0, max(0.0, channel)) * 255)) for channel in graded)
    return out


def mountain() -> bytearray:
    buf = blank()
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        sky = (0.46 + 0.08 * (1.0 - t), 0.62, 0.78 - 0.06 * t)
        for x in range(WIDTH):
            put(buf, x, y, sky)
    fill(buf, 18, 48, 200, 78, (0.50, 0.54, 0.62))
    fill(buf, 40, 62, 170, 92, (0.36, 0.40, 0.48))
    fill(buf, 70, 78, 145, 112, (0.28, 0.32, 0.38))
    return buf


def vegetation() -> bytearray:
    buf = blank()
    fill(buf, 0, 0, WIDTH, 70, (0.55, 0.62, 0.70))
    fill(buf, 0, 70, WIDTH, HEIGHT, (0.42, 0.46, 0.40))
    fill(buf, 30, 46, 190, 108, (0.34, 0.40, 0.30))
    fill(buf, 48, 58, 92, 100, (0.30, 0.38, 0.26))
    fill(buf, 120, 52, 168, 104, (0.28, 0.36, 0.24))
    return buf


def horizon() -> bytearray:
    buf = blank()
    fill(buf, 0, 0, WIDTH, 36, (0.48, 0.64, 0.84))
    fill(buf, 0, 36, WIDTH, 72, (0.78, 0.80, 0.84))
    fill(buf, 0, 72, WIDTH, 92, (0.82, 0.82, 0.82))
    fill(buf, 0, 92, WIDTH, HEIGHT, (0.40, 0.42, 0.36))
    return buf


def car() -> bytearray:
    buf = blank()
    fill(buf, 0, 0, WIDTH, 48, (0.50, 0.66, 0.86))
    fill(buf, 0, 48, WIDTH, HEIGHT, (0.32, 0.33, 0.31))
    fill(buf, 70, 58, 160, 100, (0.70, 0.12, 0.10))
    fill(buf, 78, 66, 148, 88, (0.16, 0.20, 0.24))
    return buf


def sky() -> bytearray:
    buf = blank()
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        color = (0.36 + 0.10 * t, 0.56 + 0.06 * t, 0.90 - 0.08 * t)
        for x in range(WIDTH):
            put(buf, x, y, color)
    fill(buf, 40, 28, 110, 58, (0.93, 0.94, 0.96))
    fill(buf, 130, 18, 190, 46, (0.88, 0.90, 0.93))
    return buf


def sunset() -> bytearray:
    buf = blank()
    for y in range(70):
        t = y / 69.0
        color = (0.92 - 0.20 * t, 0.46 + 0.10 * t, 0.22 + 0.08 * t)
        for x in range(WIDTH):
            put(buf, x, y, color)
    fill(buf, 0, 70, WIDTH, HEIGHT, (0.34, 0.26, 0.18))
    fill(buf, 24, 78, 196, 112, (0.55, 0.32, 0.16))
    fill(buf, 90, 40, 108, 112, (0.22, 0.16, 0.14))
    return buf


def fail(message: str) -> None:
    raise SystemExit(message)


def check(name: str, src: bytearray, out: bytearray, rules: list[tuple]) -> str:
    bits = []
    for rule in rules:
        kind = rule[0]
        x, y = rule[1], rule[2]
        before = pixel(src, x, y)
        after = pixel(out, x, y)
        if kind == "keep":
            limit = rule[3]
            delta = max(abs(before[i] - after[i]) for i in range(3))
            if delta > limit:
                fail(f"{name} moveu demais ({delta:.3f} > {limit:.3f}) {before} -> {after}")
            bits.append(f"{kind}@{x},{y} d={delta:.3f}")
        elif kind == "chroma":
            # gap = channel A - channel B must stay
            a, b, floor = rule[3], rule[4], rule[5]
            gap_before = before[a] - before[b]
            gap_after = after[a] - after[b]
            if gap_before > 0.02 and gap_after < gap_before * floor:
                fail(f"{name} perdeu cor ({gap_before:.3f} -> {gap_after:.3f})")
            bits.append(f"gap {gap_before:.3f}->{gap_after:.3f}")
        elif kind == "sat":
            low, high = rule[3], rule[4]
            sat = saturation(after)
            if sat < low or sat > high:
                fail(f"{name} saturação {sat:.3f} fora de {low:.2f}..{high:.2f}")
            bits.append(f"sat={sat:.3f}")
        elif kind == "contrast":
            x2, y2, floor = rule[3], rule[4], rule[5]
            before_gap = abs(luma(before) - luma(pixel(src, x2, y2)))
            after_gap = abs(luma(after) - luma(pixel(out, x2, y2)))
            if before_gap > 0.04 and after_gap < before_gap * floor:
                fail(f"{name} perdeu contraste ({before_gap:.3f} -> {after_gap:.3f})")
            bits.append(f"contraste {before_gap:.3f}->{after_gap:.3f}")
        elif kind == "cap":
            if max(after) > rule[3]:
                fail(f"{name} estourou {after}")
            bits.append(f"pico={max(after):.3f}")
        elif kind == "green":
            if after[1] <= after[0] or after[1] <= after[2]:
                fail(f"{name} deixou de ser verde {after}")
            bits.append("verde")
        else:
            fail(f"regra desconhecida {kind}")
    return f"{name}: " + ", ".join(bits)


def strip(frames: list[bytearray]) -> tuple[bytes, int]:
    gap = 4
    out_w = WIDTH * len(frames) + gap * (len(frames) - 1)
    raw = bytearray(out_w * HEIGHT * 3)
    for y in range(HEIGHT):
        cursor = 0
        for frame_index, frame in enumerate(frames):
            if frame_index:
                cursor += gap
            src = y * WIDTH * 3
            dst = (y * out_w + cursor) * 3
            raw[dst : dst + WIDTH * 3] = frame[src : src + WIDTH * 3]
            cursor += WIDTH
    return bytes(raw), out_w


def main() -> None:
    scenes = {
        "montanha": mountain(),
        "vegetacao": vegetation(),
        "horizonte": horizon(),
        "carro": car(),
        "ceu": sky(),
        "entardecer": sunset(),
    }
    graded = {name: grade_frame(frame) for name, frame in scenes.items()}
    reports = [
        check(
            "montanha",
            scenes["montanha"],
            graded["montanha"],
            [
                ("chroma", 80, 60, 2, 0, 0.75),
                ("contrast", 80, 60, 90, 88, 0.82),
                ("keep", 80, 60, 0.06),
                ("sat", 80, 60, 0.08, 0.40),
            ],
        ),
        check(
            "vegetacao",
            scenes["vegetacao"],
            graded["vegetacao"],
            [
                ("green", 70, 78, 0),
                ("chroma", 70, 78, 1, 0, 0.80),
                ("keep", 70, 78, 0.06),
                ("sat", 70, 78, 0.12, 0.45),
            ],
        ),
        check(
            "horizonte",
            scenes["horizonte"],
            graded["horizonte"],
            [
                ("chroma", 40, 16, 2, 0, 0.85),
                ("keep", 40, 80, 0.05),
                ("keep", 40, 100, 0.06),
                ("sat", 40, 16, 0.20, 0.55),
            ],
        ),
        check(
            "carro",
            scenes["carro"],
            graded["carro"],
            [
                ("chroma", 72, 92, 0, 2, 0.90),
                ("keep", 72, 92, 0.06),
                ("cap", 72, 92, 0.94),
                ("sat", 72, 92, 0.60, 0.95),
            ],
        ),
        check(
            "ceu",
            scenes["ceu"],
            graded["ceu"],
            [
                ("chroma", 20, 20, 2, 0, 0.85),
                ("keep", 20, 20, 0.05),
                ("cap", 70, 40, 0.955),
                ("sat", 20, 20, 0.30, 0.70),
            ],
        ),
        check(
            "entardecer",
            scenes["entardecer"],
            graded["entardecer"],
            [
                ("chroma", 40, 30, 0, 2, 0.85),
                ("keep", 40, 30, 0.06),
                ("sat", 40, 30, 0.45, 0.90),
                ("keep", 140, 96, 0.06),
            ],
        ),
    ]
    rows = []
    for name, frame in scenes.items():
        raw, out_w = strip([frame, graded[name]])
        write_png(OUT / f"ultra-{name}.png", out_w, HEIGHT, raw)
        rows.append(raw)
    sheet_h = HEIGHT * len(rows) + 4 * (len(rows) - 1)
    sheet = bytearray(out_w * sheet_h * 3)
    for row_index, raw in enumerate(rows):
        y0 = row_index * (HEIGHT + 4)
        for y in range(HEIGHT):
            src = y * out_w * 3
            dst = ((y0 + y) * out_w) * 3
            sheet[dst : dst + out_w * 3] = raw[src : src + out_w * 3]
    write_png(OUT / "ultra-distancia.png", out_w, sheet_h, bytes(sheet))
    print(" | ".join(reports))


if __name__ == "__main__":
    main()
