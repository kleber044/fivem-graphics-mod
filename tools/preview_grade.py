#!/usr/bin/env python3
"""Prévias e regressões visuais sem abrir o FiveM.

A mesma matemática de tools/fgm_color.py. Não é uma captura do GTA.
"""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

from fgm_color import (
    LOOK,
    PROFILES,
    apply_color,
    asphalt_mask,
    bloom_cap,
    bloom_weight,
    clear_pixel,
    foliage_mask,
    lamp_amount,
    lamp_chroma,
    lamp_strength,
    luma,
    ring_stats,
    road_blend,
    saturation,
    sharp_gain,
    smoothstep,
)

OUT = Path("/opt/cursor/artifacts")

MARK = {
    "sodium": (58, 210),
    "halo": (58, 196),
    "asphalt": (78, 248),
    "distant": (420, 70),
    "streak": (340, 88),
    "tail": (130, 28),
    "wall": (430, 210),
    "facade": (450, 40),
    "road": (200, 250),
    "milk": (55, 36),
    "window": (230, 120),
    "head": (400, 200),
    "neon": (24, 36),
    "red": (330, 48),
    "green": (370, 48),
    "amber": (410, 48),
    "blue": (450, 90),
    "street": (120, 250),
    "sunset": (300, 168),
    "plant": (48, 175),
    "car": (340, 200),
    "sign": (150, 188),
    "haze": (200, 78),
    "haze_sky": (200, 24),
    "sky": (40, 22),
    "cloud": (110, 24),
    "shirt": (430, 155),
    "walk": (250, 230),
    "shadow": (20, 250),
    "skin": (430, 250),
    "jeans": (30, 240),
    "jacket": (100, 230),
}


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
                if y < 70:
                    veil = 0.55
                    color = [channel * 0.45 + veil * 0.55 for channel in color]
                if 40 <= x <= 70 and 24 <= y <= 48:
                    color = [0.30, 0.305, 0.31]
                if 390 <= x <= 479 and 0 <= y <= 110:
                    color = [0.28, 0.24, 0.18]
                if 160 <= x <= 310 and 55 <= y <= 185:
                    color = [0.86, 0.63, 0.34]
                if 300 <= x <= 479 and 145 <= y <= 269:
                    color = [0.42, 0.32, 0.20]
                if 16 <= x <= 90 and 160 <= y <= 205:
                    color = [0.18, 0.34, 0.14]
                if 48 <= x <= 118 and 232 <= y <= 262:
                    color = [0.30, 0.21, 0.08]
                if 140 <= x <= 280 and 236 <= y <= 265:
                    color = [0.18, 0.14, 0.09]
                if 250 <= x <= 430 and 86 <= y <= 90:
                    color = [0.72, 0.52, 0.18]
                if 70 <= x <= 190 and 24 <= y <= 32:
                    color = [0.62, 0.44, 0.16]
                color = paint(color, x, y, 420, 70, 3, (0.90, 0.70, 0.30))
                color = paint(color, x, y, 58, 210, 20, (0.55, 0.38, 0.16))
                color = paint(color, x, y, 58, 210, 11, (1.0, 0.68, 0.26))
                color = paint(color, x, y, 400, 200, 4, (0.96, 0.94, 0.82))
                color = paint(color, x, y, 24, 36, 5, (0.92, 0.12, 0.62))
                color = paint(color, x, y, 330, 48, 3, (0.93, 0.07, 0.05))
                color = paint(color, x, y, 370, 48, 3, (0.08, 0.78, 0.12))
                color = paint(color, x, y, 410, 48, 3, (0.95, 0.48, 0.05))
                color = paint(color, x, y, 450, 90, 4, (0.15, 0.28, 0.96))
            else:
                sky = (0.45 + 0.15 * (1.0 - v), 0.62, 0.82)
                ground = (0.35, 0.36, 0.32)
                color = [sky[i] * (1.0 - v) + ground[i] * v for i in range(3)]
                if y < 100:
                    haze = 0.78 + 0.08 * (1.0 - y / 100.0)
                    color = [channel * 0.25 + haze * 0.75 for channel in color]
                if 120 <= x <= 280 and 55 <= y <= 100:
                    color = [0.55, 0.56, 0.58]
                if 20 <= x <= 80 and 150 <= y <= 205:
                    color = [0.34, 0.42, 0.28]
                if 310 <= x <= 375 and 180 <= y <= 225:
                    color = [0.62, 0.14, 0.12]
                if 130 <= x <= 175 and 165 <= y <= 210:
                    color = [0.78, 0.62, 0.12]
                if 8 <= x <= 72 and 8 <= y <= 40:
                    color = [0.40, 0.58, 0.80]
                if 90 <= x <= 140 and 12 <= y <= 40:
                    color = [0.95, 0.96, 0.97]
                if 400 <= x <= 455 and 140 <= y <= 175:
                    color = [0.96, 0.95, 0.94]
                if 220 <= x <= 280 and 215 <= y <= 245:
                    color = [0.88, 0.86, 0.82]
                if 0.55 < v < 0.72 and 0.55 < u < 0.78:
                    warm = (0.95, 0.55, 0.25)
                    color = [color[i] * 0.35 + warm[i] * 0.65 for i in range(3)]
                color = paint(color, x, y, 430, 250, 70, (0.72, 0.50, 0.40))
                color = paint(color, x, y, 30, 240, 8, (0.18, 0.28, 0.55))
                color = paint(color, x, y, 100, 230, 8, (0.62, 0.16, 0.14))
            index = (y * width + x) * 3
            rgb[index : index + 3] = bytes(int(min(255, max(0, round(channel * 255)))) for channel in color)
    return rgb


def pixel(buf: bytearray, width: int, x: int, y: int) -> tuple[float, float, float]:
    index = (y * width + x) * 3
    return tuple(channel / 255.0 for channel in buf[index : index + 3])


def put(buf: bytearray, width: int, x: int, y: int, color: tuple[float, float, float]) -> None:
    index = (y * width + x) * 3
    buf[index : index + 3] = bytes(int(round(min(1.0, max(0.0, channel)) * 255)) for channel in color)


def scene_day(raw: bytearray, width: int, height: int, x: int, y: int) -> float:
    total = 0.0
    for ox, oy in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)):
        sx = min(width - 1, max(0, int(round(x + ox * 160.0))))
        sy = min(height - 1, max(0, int(round(y + oy * 160.0))))
        total += luma(pixel(raw, width, sx, sy))
    return smoothstep(0.26, 0.46, total * 0.25)


def yellow_gap(color: tuple[float, float, float]) -> float:
    return (color[0] + color[1]) * 0.5 - color[2]


def max_delta(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return max(abs(a[i] - b[i]) for i in range(3))


def mean(buf: bytearray) -> float:
    return sum(buf) / len(buf)


def sample_luma(buf: bytearray, width: int, height: int, x: int, y: int, ox: float, oy: float) -> float:
    sx = min(width - 1, max(0, int(round(x + ox))))
    sy = min(height - 1, max(0, int(round(y + oy))))
    return luma(pixel(buf, width, sx, sy))


def ring(buf: bytearray, width: int, height: int, x: int, y: int, radius: float, taps: int) -> tuple[float, float, float, float]:
    offsets = [(1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)]
    if taps > 4:
        diagonal = 0.7071
        offsets += [(diagonal, diagonal), (-diagonal, diagonal), (diagonal, -diagonal), (-diagonal, -diagonal)]
    samples = [sample_luma(buf, width, height, x, y, ox * radius, oy * radius) for ox, oy in offsets]
    return ring_stats(samples)


def streak_amount(buf: bytearray, width: int, height: int, x: int, y: int, tone: float) -> float:
    left = sample_luma(buf, width, height, x, y, -18.0, 0.0)
    right = sample_luma(buf, width, height, x, y, 18.0, 0.0)
    up = sample_luma(buf, width, height, x, y, 0.0, -18.0)
    down = sample_luma(buf, width, height, x, y, 0.0, 18.0)
    horizontal = (left + right) * 0.5
    vertical = (up + down) * 0.5
    elongated = smoothstep(0.06, 0.14, abs(horizontal - vertical))
    darker = min(horizontal, vertical)
    brighter = max(horizontal, vertical)
    aligned = smoothstep(0.04, 0.10, tone - darker)
    along = 1.0 - smoothstep(0.02, 0.08, abs(tone - brighter))
    return elongated * aligned * along


def apply_lamps(rgb: bytearray, width: int, height: int, taps: int, level: int) -> bytearray:
    strength = lamp_strength(level)
    out = bytearray(rgb)
    for y in range(height):
        for x in range(width):
            color = pixel(rgb, width, x, y)
            if lamp_chroma(color) <= 0.001:
                continue
            near = ring(rgb, width, height, x, y, 56.0, taps)
            far = ring(rgb, width, height, x, y, 140.0, taps)
            streak = streak_amount(rgb, width, height, x, y, luma(color))
            amount = lamp_amount(color, near, far, strength, streak)
            if amount <= 0.0:
                continue
            tone = luma(color)
            put(out, width, x, y, tuple(channel * (1.0 - amount) + tone * amount for channel in color))
    return out


def apply_bloom(rgb: bytearray, width: int, height: int, threshold: float, amount: float, taps: int) -> bytearray:
    if amount <= 0.0 or taps <= 0:
        return bytearray(rgb)
    offsets = [(0.0, 0.0, 1.4)]
    near = 2.5
    for ox, oy in ((near, 0.0), (-near, 0.0), (0.0, near), (0.0, -near)):
        offsets.append((ox, oy, 1.0))
    if taps > 5:
        for ox, oy in ((near, near), (-near, -near), (near, -near), (-near, near)):
            offsets.append((ox, oy, 1.0))
    if taps > 9:
        far = 6.0
        for ox, oy in ((far, 0.0), (-far, 0.0), (0.0, far), (0.0, -far)):
            offsets.append((ox, oy, 0.45))
    out = bytearray(len(rgb))
    for y in range(height):
        for x in range(width):
            base = pixel(rgb, width, x, y)
            glow = [0.0, 0.0, 0.0]
            weight = 0.0
            for ox, oy, scale in offsets:
                sample = pixel(rgb, width, min(width - 1, max(0, int(round(x + ox)))), min(height - 1, max(0, int(round(y + oy)))))
                gain = bloom_weight(sample, threshold) * scale
                for i in range(3):
                    glow[i] += sample[i] * gain
                weight += scale
            glow = tuple(channel / max(weight, 0.001) for channel in glow)
            put(out, width, x, y, bloom_cap(base, glow, amount, threshold))
    return out


def apply_grade_pass(raw: bytearray, width: int, height: int, edition: str) -> bytearray:
    spec = LOOK[edition]
    out = bytearray(len(raw))
    for y in range(height):
        for x in range(width):
            src = pixel(raw, width, x, y)
            day = scene_day(raw, width, height, x, y)
            color = apply_color(src, edition, day)
            color = clear_pixel(color, spec["clear_day"], spec["clear_night"])
            put(out, width, x, y, color)
    return out


def finish(raw: bytearray, graded: bytearray, width: int, height: int, edition: str) -> bytearray:
    spec = LOOK[edition]
    image = apply_bloom(graded, width, height, spec["bloom_threshold"], spec["bloom_amount"], spec["bloom_taps"])
    image = apply_lamps(image, width, height, spec["lamp_taps"], spec["lamp_level"])
    out = bytearray(len(image))
    for y in range(height):
        for x in range(width):
            color = pixel(image, width, x, y)
            detail = 0.5 + 0.12 * math.sin(x * 0.37) * math.cos(y * 0.21)
            color = road_blend(color, detail, spec["road"])
            put(out, width, x, y, color)
    return out


def rain_mask(x: int, y: int, width: int, height: int, layers: int) -> float:
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
            color = list(pixel(rgb, width, x, y))
            mask = rain_mask(x, y, width, height, layers) * strength
            if mask > 0.08:
                hits += 1
                wet = (0.78, 0.84, 0.90)
                mixed = tuple(color[i] * (1.0 - mask * 0.55) + wet[i] * (mask * 0.55) for i in range(3))
                put(out, width, x, y, mixed)
    return out, hits


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


def strip(frames: list[bytearray], width: int, height: int) -> tuple[bytes, int]:
    gap = 4
    count = len(frames)
    out_w = width * count + gap * (count - 1)
    rgb = bytearray(out_w * height * 3)
    for i, frame in enumerate(frames):
        origin = i * (width + gap)
        for y in range(height):
            src = y * width * 3
            dst = (y * out_w + origin) * 3
            rgb[dst : dst + width * 3] = frame[src : src + width * 3]
    return bytes(rgb), out_w


def fail(message: str) -> None:
    raise SystemExit(message)


def check(night: bytearray, day: bytearray, graded: dict, day_done: dict, night_done: dict, lamps_only: dict, width: int, height: int) -> str:
    ultra_grade = graded["ultra"][1]
    low_grade = graded["low"][1]
    if mean(ultra_grade) >= mean(night):
        fail("a LUT Ultra não escureceu a noite")
    if mean(ultra_grade) < mean(night) * 0.75:
        fail("a LUT Ultra escureceu a noite demais")
    if mean(low_grade) >= mean(night) or mean(low_grade) < mean(ultra_grade):
        fail("a noite Low deveria ficar entre o original e a Ultra")
    rainy, _hits = apply_rain(ultra_grade, width, height, LOOK["ultra"]["rain"], 2)
    _off, off_hits = apply_rain(ultra_grade, width, height, 0.0, 2)
    _day_rain, day_hits = apply_rain(graded["ultra"][0], width, height, 0.70, 2)
    _night_rain, night_hits = apply_rain(ultra_grade, width, height, 0.70, 2)
    _light, light_hits = apply_rain(ultra_grade, width, height, 0.30, 1)
    if off_hits != 0:
        fail(f"força zero deveria deixar a tela limpa ({off_hits})")
    if day_hits == 0 or night_hits == 0 or day_hits != night_hits:
        fail(f"a gota não pode depender do brilho ({day_hits}, {night_hits})")
    if night_hits <= light_hits:
        fail("chuva mais forte deveria marcar mais pixels")
    if LOOK["low"]["rain"] != 0.0:
        fail("Low guarda chuva em zero")
    center = region_hits(width, height, ultra_grade, rainy, True)
    border = region_hits(width, height, ultra_grade, rainy, False)
    if border <= center:
        fail(f"gotas deveriam preferir a borda ({border}) ao centro ({center})")

    before = pixel(ultra_grade, width, *MARK["sodium"])
    after = pixel(night_done["ultra"], width, *MARK["sodium"])
    after_low = pixel(night_done["low"], width, *MARK["sodium"])
    if yellow_gap(after) > 0.05:
        fail(f"poste Ultra continuou amarelo ({yellow_gap(after):.3f})")
    if yellow_gap(after_low) > 0.06:
        fail(f"poste Low continuou amarelo ({yellow_gap(after_low):.3f})")
    if abs(luma(after) - luma(before)) > 0.06:
        fail("o branco do poste mudou demais a luminância")
    if after[2] > after[0] + 0.08 or after[1] > after[2] + 0.04:
        fail(f"poste saiu do branco neutro {tuple(round(c, 3) for c in after)}")
    for name, limit in (("halo", 0.06), ("asphalt", 0.08), ("distant", 0.08), ("streak", 0.08), ("tail", 0.08)):
        src = pixel(ultra_grade, width, *MARK[name])
        out = pixel(night_done["ultra"], width, *MARK[name])
        if yellow_gap(out) > max(limit, yellow_gap(src) * 0.45):
            fail(f"{name} continuou amarelo ({yellow_gap(src):.3f} -> {yellow_gap(out):.3f})")
    protected = ("window", "head", "neon", "red", "green", "amber", "blue", "street", "wall", "facade", "road")
    for name in protected:
        delta = max_delta(pixel(ultra_grade, width, *MARK[name]), pixel(lamps_only["ultra"], width, *MARK[name]))
        if delta > 0.03:
            fail(f"{name} foi neutralizado ({delta:.3f})")
    sunset_delta = max_delta(
        pixel(graded["ultra"][0], width, *MARK["sunset"]),
        pixel(apply_lamps(graded["ultra"][0], width, height, 8, 3), width, *MARK["sunset"]),
    )
    if sunset_delta > 0.03:
        fail("o pôr do sol foi tratado como poste")

    haze_src = pixel(day, width, *MARK["haze"])
    haze_out = pixel(day_done["ultra"], width, *MARK["haze"])
    haze_before = luma(haze_src)
    haze_after = luma(haze_out)
    if abs(haze_before - haze_after) > 0.06:
        fail(f"montanha/névoa foi esmagada ({haze_before:.3f} -> {haze_after:.3f})")
    if saturation(haze_out) + 0.02 < saturation(haze_src):
        fail(f"névoa perdeu cor ({saturation(haze_src):.3f} -> {saturation(haze_out):.3f})")
    if (haze_src[2] - haze_src[0]) - (haze_out[2] - haze_out[0]) > 0.015:
        fail("o tom da montanha foi comido")
    milk_before = luma(pixel(night, width, *MARK["milk"]))
    milk_u = luma(pixel(night_done["ultra"], width, *MARK["milk"]))
    milk_l = luma(pixel(night_done["low"], width, *MARK["milk"]))
    if milk_before - milk_u < 0.03 or milk_u < 0.06:
        fail(f"leite da noite Ultra fora da faixa ({milk_before:.3f} -> {milk_u:.3f})")
    if milk_u > milk_l + 0.02:
        fail("Ultra deveria limpar o leite da noite pelo menos tanto quanto Low")
    for name in ("wall", "facade", "road"):
        src = pixel(ultra_grade, width, *MARK[name])
        out = pixel(night_done["ultra"], width, *MARK[name])
        if saturation(out) + 0.05 < saturation(src):
            fail(f"{name} perdeu cor")

    plant_before = saturation(pixel(day, width, *MARK["plant"]))
    plant_after = saturation(pixel(day_done["ultra"], width, *MARK["plant"]))
    plant_low = saturation(pixel(day_done["low"], width, *MARK["plant"]))
    if plant_before - plant_after > 0.08:
        fail(f"vegetação foi lavada ({plant_before:.3f} -> {plant_after:.3f})")
    if plant_after < 0.25 or plant_after > plant_before + 0.05:
        fail(f"vegetação fora do natural ({plant_before:.3f} -> {plant_after:.3f})")
    if plant_after + 0.04 < plant_low:
        fail("Ultra ficou mais cinza que Low na vegetação")
    if foliage_mask(pixel(day_done["ultra"], width, *MARK["plant"])) < 0.2:
        fail("a planta deixou de ser verde")

    for name in ("skin", "jeans", "jacket"):
        raw_color = pixel(day, width, *MARK[name])
        out_color = pixel(day_done["ultra"], width, *MARK[name])
        if max_delta(raw_color, out_color) > 0.035:
            fail(f"{name} saiu da cor do jogo {tuple(round(c, 3) for c in raw_color)} -> {tuple(round(c, 3) for c in out_color)}")
    shirt = pixel(day_done["ultra"], width, *MARK["shirt"])
    cloud = pixel(day_done["ultra"], width, *MARK["cloud"])
    if max(shirt) > 0.955 or min(shirt) < 0.78:
        fail(f"camisa branca fora da faixa {tuple(round(c, 3) for c in shirt)}")
    if max(cloud) > 0.955 or min(cloud) < 0.78:
        fail(f"nuvem fora da faixa {tuple(round(c, 3) for c in cloud)}")
    car = pixel(day_done["ultra"], width, *MARK["car"])
    if max(car) > 0.94:
        fail(f"carro estourou {tuple(round(c, 3) for c in car)}")
    sky_src = pixel(day, width, *MARK["sky"])
    sky_out = pixel(day_done["ultra"], width, *MARK["sky"])
    sky_gap_src = sky_src[2] - sky_src[0]
    sky_gap_out = sky_out[2] - sky_out[0]
    if sky_gap_out < sky_gap_src * 0.82:
        fail(f"céu perdeu azul demais ({sky_gap_src:.3f} -> {sky_gap_out:.3f})")
    if sky_gap_out > sky_gap_src * 1.08:
        fail(f"céu ficou saturado demais ({sky_gap_src:.3f} -> {sky_gap_out:.3f})")
    if saturation(sky_out) < 0.28:
        fail(f"céu acinzentado ({saturation(sky_out):.3f})")

    road = pixel(night_done["ultra"], width, *MARK["road"])
    if asphalt_mask(pixel(night, width, *MARK["road"])) < 0.2 and asphalt_mask(road) < 0.05:
        pass
    skin_sharp = sharp_gain((0.72, 0.50, 0.40), 0.20, 0.26)
    leaf_sharp = sharp_gain((0.22, 0.55, 0.16), 0.20, 0.26)
    flat_sharp = sharp_gain((0.45, 0.45, 0.45), 0.01, 0.26)
    if not (skin_sharp < leaf_sharp < flat_sharp):
        fail(f"nitidez não protege pele e folha ({skin_sharp:.3f}, {leaf_sharp:.3f}, {flat_sharp:.3f})")
    return (
        f"previews ok poste={tuple(round(c, 3) for c in after)} "
        f"haze={haze_before:.3f}->{haze_after:.3f} planta={plant_before:.3f}->{plant_after:.3f} "
        f"gotas={night_hits} borda={border}"
    )


def render(out_dir: Path) -> str:
    width, height = 480, 270
    night = scene(width, height, True)
    day = scene(width, height, False)
    graded = {}
    done = {}
    lamps_only = {}
    for edition in PROFILES:
        day_grade = apply_grade_pass(day, width, height, edition)
        night_grade = apply_grade_pass(night, width, height, edition)
        graded[edition] = (day_grade, night_grade)
        done[edition] = {
            "day": finish(day, day_grade, width, height, edition),
            "night": finish(night, night_grade, width, height, edition),
        }
        spec = LOOK[edition]
        lamps_only[edition] = apply_lamps(night_grade, width, height, spec["lamp_taps"], spec["lamp_level"])
    report = check(
        night,
        day,
        graded,
        {k: v["day"] for k, v in done.items()},
        {k: v["night"] for k, v in done.items()},
        lamps_only,
        width,
        height,
    )
    rainy, _hits = apply_rain(graded["ultra"][1], width, height, LOOK["ultra"]["rain"], 2)
    panels = {
        "dia": [day] + [done[name]["day"] for name in PROFILES],
        "noite": [night] + [done[name]["night"] for name in PROFILES],
        "chuva": [graded["ultra"][1], rainy],
        "poste": [night, lamps_only["low"], lamps_only["ultra"]],
    }
    for name, frames in panels.items():
        raw, out_w = strip(frames, width, height)
        write_png(out_dir / f"comparacao-{name}.png", out_w, height, raw)
    for edition in ("ultra", "low"):
        raw, out_w = strip([day, done[edition]["day"]], width, height)
        write_png(out_dir / f"preview-{edition}-dia.png", out_w, height, raw)
        raw, out_w = strip([night, done[edition]["night"]], width, height)
        write_png(out_dir / f"preview-{edition}-noite.png", out_w, height, raw)
    raw, out_w = strip([graded["ultra"][1], rainy], width, height)
    write_png(out_dir / "preview-ultra-chuva.png", out_w, height, raw)
    return report


def main() -> None:
    print(render(OUT))


if __name__ == "__main__":
    main()
