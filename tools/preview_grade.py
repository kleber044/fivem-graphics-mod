#!/usr/bin/env python3
"""Gera prévias da grade e das gotas sem abrir o GTA. A mesma matemática da LUT."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

from build_dist import clear_pixel, grade, keep_person, smoothstep, vibrance

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


# Centros usados pela prévia e pelas checagens. Anéis de 56 px e 140 px.
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
            rgb[index : index + 3] = bytes(int(min(255, max(0, channel * 255))) for channel in color)
    return rgb


def luma(color: tuple[float, float, float]) -> float:
    return 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]


def lamp_chroma(color: tuple[float, float, float]) -> float:
    # A mesma conta de FGM_Lamps.fx. Amarelo de luz, não neon nem farol branco.
    red, green, blue = color
    peak = max(red, green, blue)
    floorc = min(red, green, blue)
    sat = (peak - floorc) / max(peak, 0.001)
    excess = min(red, green) - blue
    yellow = smoothstep(0.035, 0.10, excess)
    ratio = green / max(red, 0.001)
    not_red = smoothstep(0.40, 0.55, ratio)
    not_green = 1.0 - smoothstep(0.0, 0.08, green - red)
    not_neon = 1.0 - smoothstep(0.86, 0.96, sat)
    has_cast = smoothstep(0.15, 0.28, sat)
    return yellow * not_red * not_green * not_neon * has_cast


def lamp_strength(level: int) -> float:
    if level <= 1:
        return 0.78
    if level == 2:
        return 0.98
    return 1.0


def ring(rgb: bytearray, width: int, height: int, x: int, y: int, radius: float, offsets: list[tuple[float, float]]) -> tuple[float, float, float, float]:
    samples = []
    for ox, oy in offsets:
        sx = min(width - 1, max(0, int(round(x + ox * radius))))
        sy = min(height - 1, max(0, int(round(y + oy * radius))))
        sample_index = (sy * width + sx) * 3
        sample = tuple(channel / 255.0 for channel in rgb[sample_index : sample_index + 3])
        samples.append(luma(sample))
    lo = min(samples)
    hi = max(samples)
    cut = (lo + hi) * 0.5
    bright = [value for value in samples if value >= cut]
    dark = [value for value in samples if value < cut]
    bright_support = sum(bright) / len(bright)
    dark_support = sum(dark) / len(dark) if dark else bright_support
    dark_fraction = len(dark) / len(samples)
    return hi - lo, bright_support, dark_support, dark_fraction


def lamp_amount(color: tuple[float, float, float], near: tuple[float, float, float, float], far: tuple[float, float, float, float], strength: float) -> float:
    # A mesma conta de FGM_Lamps.fx.
    sodium = lamp_chroma(color)
    if sodium <= 0.001:
        return 0.0
    tone = luma(color)
    near_spread, near_bright, near_dark, near_fraction = near
    _far_spread, far_bright, far_dark, far_fraction = far
    peak = smoothstep(0.012, 0.045, tone - near_bright)
    thin = smoothstep(0.34, 0.52, near_fraction) * smoothstep(0.05, 0.12, tone - near_dark)
    spill = smoothstep(0.05, 0.12, tone - near_dark) * smoothstep(0.08, 0.18, near_bright - tone)
    gradient = smoothstep(0.025, 0.07, near_spread) * (1.0 - smoothstep(0.16, 0.30, near_spread))
    wide = smoothstep(0.40, 0.65, far_fraction) * smoothstep(0.08, 0.16, tone - far_dark) * gradient
    # Superfície contínua: a cor ao redor é a mesma. Não é fio, halo nem reflexo.
    on_surface = (1.0 - smoothstep(0.02, 0.28, near_fraction)) * (1.0 - smoothstep(0.03, 0.09, abs(tone - near_bright)))
    day_block = smoothstep(0.30, 0.40, far_dark)
    light = sodium * max(peak, thin, spill, wide) * (1.0 - on_surface) * (1.0 - day_block)
    shade = 1.0 - smoothstep(0.10, 0.18, tone)
    light *= 1.0 - shade * (1.0 - min(1.0, peak + thin + spill))
    return min(1.0, max(0.0, light)) * strength


def apply_lamps(rgb: bytearray, width: int, height: int, taps: int, level: int) -> bytearray:
    # Anel de 56 px separa fio de luz e superfície. O de 140 px pega o halo largo.
    # Quality usa 8 amostras; Performance usa as 4 cardeais.
    strength = lamp_strength(level)
    out = bytearray(rgb)
    offsets = [(1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)]
    if taps > 4:
        diagonal = 0.7071
        offsets += [(diagonal, diagonal), (-diagonal, diagonal), (diagonal, -diagonal), (-diagonal, -diagonal)]
    for y in range(height):
        for x in range(width):
            index = (y * width + x) * 3
            color = tuple(channel / 255.0 for channel in rgb[index : index + 3])
            if lamp_chroma(color) <= 0.001:
                continue
            near = ring(rgb, width, height, x, y, 56.0, offsets)
            far = ring(rgb, width, height, x, y, 140.0, offsets)
            amount = lamp_amount(color, near, far, strength)
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


def saturation(color: tuple[float, float, float]) -> float:
    peak = max(color)
    floorc = min(color)
    return (peak - floorc) / max(peak, 0.001)


def scene_day(raw: bytearray, width: int, height: int, x: int, y: int) -> float:
    # A mesma sonda de FGM_SceneLuma: quatro amostras a 160 px no quadro original.
    total = 0.0
    for ox, oy in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)):
        sx = min(width - 1, max(0, int(round(x + ox * 160.0))))
        sy = min(height - 1, max(0, int(round(y + oy * 160.0))))
        total += luma(pixel(raw, width, sx, sy))
    return smoothstep(0.26, 0.46, total * 0.25)


def polish(
    graded: bytearray,
    raw: bytearray,
    width: int,
    height: int,
    amount: float,
    plant: float,
    clear: int,
    taps: int,
    level: int,
    calm: float,
) -> bytearray:
    vivid = bytearray(len(graded))
    for y in range(height):
        for x in range(width):
            index = (y * width + x) * 3
            src = tuple(channel / 255.0 for channel in graded[index : index + 3])
            original = tuple(channel / 255.0 for channel in raw[index : index + 3])
            day = scene_day(raw, width, height, x, y)
            color = keep_person(original, vibrance(src, amount, plant, day, calm))
            color = clear_pixel(color, clear)
            vivid[index : index + 3] = bytes(int(round(min(1.0, max(0.0, channel)) * 255)) for channel in color)
    return apply_lamps(vivid, width, height, taps, level)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    width, height = 480, 270
    night = scene(width, height, True)
    day = scene(width, height, False)
    look = {
        "quality": {"rain": 0.72, "layers": 2, "taps": 8, "level": 3, "clear": 3, "vibrance": 0.14, "plant": 0.04, "calm": 0.22},
        "performance": {"rain": 0.30, "layers": 1, "taps": 4, "level": 2, "clear": 2, "vibrance": 0.08, "plant": 0.00, "calm": 0.14},
    }
    frames = {}
    finished = {}
    lamps_only = {}
    for edition, spec in look.items():
        day_grade = apply_grade(day, width, height, edition)
        night_grade = apply_grade(night, width, height, edition)
        day_done = polish(day_grade, day, width, height, spec["vibrance"], spec["plant"], spec["clear"], spec["taps"], spec["level"], spec["calm"])
        night_done = polish(night_grade, night, width, height, spec["vibrance"], spec["plant"], spec["clear"], spec["taps"], spec["level"], spec["calm"])
        rainy, _hits = apply_rain(night_grade, width, height, spec["rain"], spec["layers"])
        frames[edition] = (day_grade, night_grade, rainy, day_done)
        finished[edition] = night_done
        lamps_only[edition] = apply_lamps(night_grade, width, height, spec["taps"], spec["level"])
        write_png(OUT / f"preview-{edition}-dia.png", width * 2 + 8, height, panel(day, day_done, width, height))
        write_png(OUT / f"preview-{edition}-noite.png", width * 2 + 8, height, panel(night, night_done, width, height))
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
    after_q = pixel(finished["quality"], width, sx, sy)
    after_p = pixel(finished["performance"], width, sx, sy)
    soft = pixel(apply_lamps(night_q, width, height, 8, 1), width, sx, sy)
    if yellow_gap(after_q) > 0.05:
        raise SystemExit(f"White LED continuou amarelo ({yellow_gap(before):.3f} -> {yellow_gap(after_q):.3f})")
    if yellow_gap(after_p) > 0.06:
        raise SystemExit(f"Neutral continuou amarelo ({yellow_gap(after_p):.3f})")
    if yellow_gap(soft) <= yellow_gap(after_p) + 0.02:
        raise SystemExit("Soft precisa ser mais quente que Neutral")
    if abs(luma(after_q) - luma(before)) > 0.04:
        raise SystemExit("o branco do poste mudou a luminância e alimentaria o bloom")
    if after_q[2] > after_q[0] + 0.08:
        raise SystemExit(f"o poste ficou azulado {tuple(round(c, 3) for c in after_q)}")
    if after_q[1] > after_q[2] + 0.04:
        raise SystemExit(f"o poste ficou esverdeado {tuple(round(c, 3) for c in after_q)}")
    halo_before = pixel(night_q, width, *MARK["halo"])
    halo = pixel(finished["quality"], width, *MARK["halo"])
    halo_p = pixel(finished["performance"], width, *MARK["halo"])
    if yellow_gap(halo) > 0.06:
        raise SystemExit(f"o halo do poste continuou amarelo ({tuple(round(c, 3) for c in halo)})")
    if yellow_gap(halo_p) > yellow_gap(halo_before) * 0.35:
        raise SystemExit(f"o halo Performance continuou amarelo ({yellow_gap(halo_p):.3f})")
    if halo[2] > halo[0] + 0.08:
        raise SystemExit(f"o halo ficou azul {tuple(round(c, 3) for c in halo)}")
    asphalt_before = pixel(night_q, width, *MARK["asphalt"])
    asphalt = pixel(finished["quality"], width, *MARK["asphalt"])
    if yellow_gap(asphalt) > yellow_gap(asphalt_before) * 0.40:
        raise SystemExit(f"o asfalto do poste continuou amarelo ({tuple(round(c, 3) for c in asphalt)})")
    distant_before = pixel(night_q, width, *MARK["distant"])
    distant = pixel(finished["quality"], width, *MARK["distant"])
    if yellow_gap(distant) > yellow_gap(distant_before) * 0.35:
        raise SystemExit(f"a luz urbana distante continuou amarela ({tuple(round(c, 3) for c in distant)})")
    distant_p = pixel(finished["performance"], width, *MARK["distant"])
    if yellow_gap(distant_p) > yellow_gap(distant_before) * 0.40:
        raise SystemExit(f"a luz distante Performance continuou amarela ({yellow_gap(distant_p):.3f})")
    for name in ("streak", "tail"):
        src = pixel(night_q, width, *MARK[name])
        out = pixel(finished["quality"], width, *MARK[name])
        out_p = pixel(finished["performance"], width, *MARK[name])
        if yellow_gap(out) > yellow_gap(src) * 0.35:
            raise SystemExit(f"{name} continuou amarelo ({tuple(round(c, 3) for c in out)})")
        if yellow_gap(out_p) > yellow_gap(src) * 0.40:
            raise SystemExit(f"{name} Performance continuou amarelo ({yellow_gap(out_p):.3f})")
    protected = ("window", "head", "neon", "red", "green", "amber", "blue", "street", "wall", "facade", "road")
    for name in protected:
        x, y = MARK[name]
        delta = max_delta(pixel(night_q, width, x, y), pixel(lamps_only["quality"], width, x, y))
        if delta > 0.03:
            raise SystemExit(f"{name} não deveria ser neutralizado ({delta:.3f})")
    day_q = frames["quality"][0]
    day_done = frames["quality"][3]
    sunset_delta = max_delta(pixel(day_q, width, *MARK["sunset"]), pixel(apply_lamps(day_q, width, height, 8, 3), width, *MARK["sunset"]))
    if sunset_delta > 0.03:
        raise SystemExit(f"o pôr do sol foi tratado como poste ({sunset_delta:.3f})")
    haze_before = luma(pixel(day_q, width, *MARK["haze"]))
    haze_after = luma(pixel(day_done, width, *MARK["haze"]))
    sky_before = luma(pixel(day_q, width, *MARK["haze_sky"]))
    sky_after = luma(pixel(day_done, width, *MARK["haze_sky"]))
    haze_drop = haze_before - haze_after
    if haze_drop < 0.10:
        raise SystemExit(f"a névoa do prédio distante não recuou ({haze_before:.3f} -> {haze_after:.3f})")
    if haze_drop > 0.32 or haze_after < 0.22:
        raise SystemExit(f"a limpeza do horizonte ficou dura ({haze_before:.3f} -> {haze_after:.3f})")
    if (sky_before - haze_before) >= (sky_after - haze_after):
        raise SystemExit("o horizonte não ganhou separação")
    shadow_before = luma(pixel(night_q, width, *MARK["shadow"]))
    shadow_after = luma(pixel(finished["quality"], width, *MARK["shadow"]))
    if shadow_after < shadow_before - 0.03:
        raise SystemExit("a limpeza do horizonte escureceu a sombra")
    milk_before = luma(pixel(night_q, width, *MARK["milk"]))
    milk_q = luma(pixel(finished["quality"], width, *MARK["milk"]))
    milk_p = luma(pixel(finished["performance"], width, *MARK["milk"]))
    if milk_before - milk_q < 0.04:
        raise SystemExit(f"o leite da noite não recuou ({milk_before:.3f} -> {milk_q:.3f})")
    if milk_q < 0.08:
        raise SystemExit(f"o leite da noite foi esmagado ({milk_q:.3f})")
    if milk_before - milk_p < 0.025:
        raise SystemExit(f"o leite Performance quase não mudou ({milk_before:.3f} -> {milk_p:.3f})")
    if milk_q >= milk_p:
        raise SystemExit("Quality deveria limpar mais o leite da noite que Performance")
    for name in ("wall", "facade", "road"):
        src = pixel(night_q, width, *MARK[name])
        out = pixel(finished["quality"], width, *MARK[name])
        if saturation(out) + 0.04 < saturation(src):
            raise SystemExit(f"{name} perdeu cor ({saturation(src):.3f} -> {saturation(out):.3f})")
    plant_before = saturation(pixel(day_q, width, *MARK["plant"]))
    plant_after = saturation(pixel(day_done, width, *MARK["plant"]))
    plant_perf = saturation(pixel(frames["performance"][3], width, *MARK["plant"]))
    if plant_before - plant_after < 0.03:
        raise SystemExit(f"o dia não acalmou a vegetação ({plant_before:.3f} -> {plant_after:.3f})")
    if plant_after < 0.22:
        raise SystemExit(f"vegetação ficou lavada ({plant_before:.3f} -> {plant_after:.3f})")
    if plant_perf > plant_before - 0.015:
        raise SystemExit(f"Performance não acalmou a vegetação ({plant_before:.3f} -> {plant_perf:.3f})")
    if plant_after > plant_perf + 0.005:
        raise SystemExit("Quality deveria acalmar o dia pelo menos tanto quanto Performance")
    if plant_after > 0.48:
        raise SystemExit(f"vegetação ainda forte ({plant_after:.3f})")
    graded_green = grade((0.22, 0.55, 0.16), "quality")
    night_green = vibrance(graded_green, 0.14, 0.04)
    day_green = vibrance(graded_green, 0.14, 0.04, 1.0, 0.22)
    if saturation(night_green) > saturation(graded_green) + 0.04:
        raise SystemExit(f"verde já vivo ainda subiu à noite ({saturation(night_green):.3f})")
    if saturation(graded_green) - saturation(day_green) < 0.04:
        raise SystemExit(f"o verde do dia quase não cedeu ({saturation(graded_green):.3f} -> {saturation(day_green):.3f})")
    if saturation(day_green) < 0.28:
        raise SystemExit(f"o verde do dia ficou cinza ({saturation(day_green):.3f})")
    skin_src = grade((0.76, 0.56, 0.46), "quality")
    skin = vibrance(skin_src, 0.14, 0.04)
    if skin[0] > skin_src[0] + 0.03:
        raise SystemExit(f"pele ficou laranja ({tuple(round(c, 3) for c in skin)})")
    for sample in ((0.76, 0.56, 0.46), (0.45, 0.30, 0.22), (0.62, 0.16, 0.14), (0.18, 0.28, 0.55)):
        kept = keep_person(sample, vibrance(grade(sample, "quality"), 0.14, 0.04, 1.0, 0.22))
        if max_delta(kept, sample) > 0.030:
            raise SystemExit(f"personagem saiu da cor do jogo {tuple(round(c, 3) for c in sample)} -> {tuple(round(c, 3) for c in kept)}")
    for name in ("skin", "jeans", "jacket"):
        raw_color = pixel(day, width, *MARK[name])
        out_color = pixel(day_done, width, *MARK[name])
        if max_delta(raw_color, out_color) > 0.030:
            raise SystemExit(f"{name} saiu da cor do jogo {tuple(round(c, 3) for c in raw_color)} -> {tuple(round(c, 3) for c in out_color)}")
    sky_src = pixel(day_q, width, *MARK["sky"])
    sky_out = pixel(day_done, width, *MARK["sky"])
    if (sky_src[2] - sky_src[0]) - (sky_out[2] - sky_out[0]) < 0.03:
        raise SystemExit("o céu do dia não perdeu o azul exagerado")
    shirt = pixel(day_done, width, *MARK["shirt"])
    if max(shirt) > 0.955:
        raise SystemExit(f"camisa branca estourou {tuple(round(c, 3) for c in shirt)}")
    if min(shirt) < 0.82:
        raise SystemExit(f"camisa branca ficou cinza {tuple(round(c, 3) for c in shirt)}")
    cloud = pixel(day_done, width, *MARK["cloud"])
    if max(cloud) > 0.955 or min(cloud) < 0.82:
        raise SystemExit(f"nuvem fora da faixa {tuple(round(c, 3) for c in cloud)}")
    car = pixel(day_done, width, *MARK["car"])
    if max(car) > 0.92:
        raise SystemExit(f"carro estourou vermelho {tuple(round(c, 3) for c in car)}")
    print(
        f"previews ok desligado={off_hits} noite_gotas={night_hits} dia_gotas={day_hits} "
        f"fraca={light_hits} borda={border} centro={center} "
        f"poste={tuple(round(c, 3) for c in after_q)} "
        f"haze={haze_before:.3f}->{haze_after:.3f} planta={plant_before:.3f}->{plant_after:.3f}"
    )


if __name__ == "__main__":
    main()
