"""Matemática visual do FGM 2.0. Os shaders em src/shaders repetem estas contas.

Não há leitura de profundidade, clima, menu ou memória do processo.
"""

from __future__ import annotations

PRODUCT_VERSION = "2.0.0"

# Quality instala Ultra. Performance instala Low.
ALIASES = {"quality": "ultra", "performance": "low"}

PROFILES = ("ultra", "high", "medium", "low")


def canonical_edition(name: str) -> str:
    key = name.strip().lower()
    key = ALIASES.get(key, key)
    if key not in PROFILES:
        raise ValueError(f"edição desconhecida: {name}")
    return key


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    span = edge1 - edge0
    if span == 0:
        return 0.0
    t = min(1.0, max(0.0, (x - edge0) / span))
    return t * t * (3.0 - 2.0 * t)


def clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def clamp3(color: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(clamp01(channel) for channel in color)


def luma(color: tuple[float, float, float]) -> float:
    return 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]


def saturation(color: tuple[float, float, float]) -> float:
    peak = max(color)
    floorc = min(color)
    return (peak - floorc) / max(peak, 0.001)


def mix(a: tuple[float, float, float], b: tuple[float, float, float], t: float) -> tuple[float, float, float]:
    return tuple(a[i] * (1.0 - t) + b[i] * t for i in range(3))


# Contraste da LUT, abertura de sombra, céu e pôr do sol. A tinta de sombra ficou no AmbientTone.
GRADE = {
    "ultra": {"contrast": 1.050, "shadow_scale": 0.035, "sky_push": 0.008, "sun_push": 0.010},
    "high": {"contrast": 1.040, "shadow_scale": 0.030, "sky_push": 0.007, "sun_push": 0.008},
    "medium": {"contrast": 1.030, "shadow_scale": 0.022, "sky_push": 0.005, "sun_push": 0.006},
    "low": {"contrast": 1.025, "shadow_scale": 0.016, "sky_push": 0.004, "sun_push": 0.004},
}

# Força de cada técnica. Zero significa que o preset não liga o passo.
LOOK = {
    "ultra": {
        "exposure": 0.012,
        "shadows": 0.045,
        "vibrance": 0.120,
        "plant": 0.030,
        "day_calm": 0.240,
        "night": 0.080,
        "ambient": 0.035,
        "contrast": 0.040,
        "tonemap": 0.400,
        "highlight": 0.450,
        "clear_day": 0.500,
        "clear_night": 0.120,
        "bloom_threshold": 0.940,
        "bloom_amount": 0.040,
        "bloom_taps": 13,
        "lamp_level": 3,
        "lamp_taps": 8,
        "road": 0.120,
        "road_size": 1024,
        "reflect": 0.200,
        "reflect_taps": 8,
        "sharp": 0.260,
        "vignette": 0.140,
        "rain": 0.700,
        "rain_layers": 2,
        "rain_distort": 0.850,
        "grain": 0.000,
        "aberration": 0.000,
    },
    "high": {
        "exposure": 0.008,
        "shadows": 0.035,
        "vibrance": 0.100,
        "plant": 0.020,
        "day_calm": 0.210,
        "night": 0.065,
        "ambient": 0.028,
        "contrast": 0.030,
        "tonemap": 0.340,
        "highlight": 0.380,
        "clear_day": 0.440,
        "clear_night": 0.105,
        "bloom_threshold": 0.950,
        "bloom_amount": 0.028,
        "bloom_taps": 9,
        "lamp_level": 3,
        "lamp_taps": 8,
        "road": 0.100,
        "road_size": 512,
        "reflect": 0.140,
        "reflect_taps": 4,
        "sharp": 0.200,
        "vignette": 0.110,
        "rain": 0.550,
        "rain_layers": 2,
        "rain_distort": 0.650,
        "grain": 0.000,
        "aberration": 0.000,
    },
    "medium": {
        "exposure": 0.000,
        "shadows": 0.028,
        "vibrance": 0.070,
        "plant": 0.010,
        "day_calm": 0.170,
        "night": 0.050,
        "ambient": 0.020,
        "contrast": 0.018,
        "tonemap": 0.260,
        "highlight": 0.300,
        "clear_day": 0.340,
        "clear_night": 0.085,
        "bloom_threshold": 0.970,
        "bloom_amount": 0.015,
        "bloom_taps": 5,
        "lamp_level": 2,
        "lamp_taps": 4,
        "road": 0.070,
        "road_size": 512,
        "reflect": 0.080,
        "reflect_taps": 4,
        "sharp": 0.140,
        "vignette": 0.080,
        "rain": 0.350,
        "rain_layers": 1,
        "rain_distort": 0.400,
        "grain": 0.000,
        "aberration": 0.000,
    },
    "low": {
        "exposure": 0.000,
        "shadows": 0.020,
        "vibrance": 0.050,
        "plant": 0.000,
        "day_calm": 0.130,
        "night": 0.035,
        "ambient": 0.012,
        "contrast": 0.000,
        "tonemap": 0.200,
        "highlight": 0.250,
        "clear_day": 0.260,
        "clear_night": 0.070,
        "bloom_threshold": 1.000,
        "bloom_amount": 0.000,
        "bloom_taps": 0,
        "lamp_level": 2,
        "lamp_taps": 4,
        "road": 0.040,
        "road_size": 256,
        "reflect": 0.000,
        "reflect_taps": 0,
        "sharp": 0.090,
        "vignette": 0.050,
        "rain": 0.000,
        "rain_layers": 1,
        "rain_distort": 0.200,
        "grain": 0.000,
        "aberration": 0.000,
    },
}


def shoulder(channel: float) -> float:
    # Joelha alta. Branco continua branco, mas 0,96 não gruda em 1,00.
    knee = 0.78
    if channel <= knee:
        return clamp01(channel)
    span = 1.0 - knee
    t = (channel - knee) / span
    curved = t / (1.0 + 0.35 * t)
    full = 1.0 / 1.35
    rolled = knee + 0.16 * (curved / full)
    return clamp01(rolled)


def grade(rgb: tuple[float, float, float], edition: str) -> tuple[float, float, float]:
    spec = GRADE[canonical_edition(edition)]
    x = list(rgb)
    tone = luma(rgb)
    shadow = smoothstep(0.50, 0.05, tone)
    highlight = smoothstep(0.62, 0.92, tone)
    curved = []
    for channel in x:
        pulled = (channel - 0.50) * spec["contrast"] + 0.50
        weight = smoothstep(0.0, 0.25, channel)
        curved.append(channel * (1.0 - weight) + pulled * weight)
    x = [channel * (1.0 - spec["shadow_scale"] * shadow) for channel in curved]
    green_dom = max(0.0, x[1] - max(x[0], x[2]))
    plant = smoothstep(0.02, 0.14, green_dom)
    blue_dom = max(0.0, x[2] - max(x[0], x[1]))
    sky = smoothstep(0.02, 0.16, blue_dom) * smoothstep(0.35, 0.80, tone)
    warm_dom = max(0.0, x[0] - x[2]) * max(0.0, x[0] - x[1] * 0.85)
    sunset = smoothstep(0.03, 0.16, warm_dom) * smoothstep(0.20, 0.70, tone)
    # O céu e o pôr do sol mexem pouco. A vegetação não recebe tinta fria extra.
    tint = 1.0 - 0.75 * plant
    _ = highlight, tint
    x[0] += spec["sun_push"] * sunset - spec["sky_push"] * 0.35 * sky
    x[1] += spec["sun_push"] * 0.25 * sunset
    x[2] += spec["sky_push"] * sky - spec["sun_push"] * 0.45 * sunset
    return tuple(shoulder(channel) for channel in x)


def skin_mask(rgb: tuple[float, float, float], tone: float, sat: float) -> float:
    red, green, blue = rgb
    rg = red - green
    gb = green - blue
    skin = smoothstep(0.04, 0.12, rg) * (1.0 - smoothstep(0.18, 0.32, rg))
    skin *= smoothstep(0.03, 0.10, gb)
    skin *= smoothstep(0.20, 0.40, tone) * (1.0 - smoothstep(0.62, 0.82, tone))
    skin *= smoothstep(0.10, 0.22, sat) * (1.0 - smoothstep(0.45, 0.65, sat))
    return clamp01(skin)


def foliage_mask(rgb: tuple[float, float, float]) -> float:
    return smoothstep(0.02, 0.08, rgb[1] - max(rgb[0], rgb[2]))


def keep_person(original: tuple[float, float, float], graded: tuple[float, float, float]) -> tuple[float, float, float]:
    # Pele e roupa com cor voltam ao quadro. Grama e céu continuam na grade.
    red, green, blue = original
    tone = luma(original)
    sat = saturation(original)
    foliage = foliage_mask(original)
    skyish = smoothstep(0.04, 0.12, blue - max(red, green))
    skyish *= smoothstep(0.35, 0.52, tone)
    skyish *= 1.0 - smoothstep(0.58, 0.78, sat)
    rg = red - green
    gb = green - blue
    skin = skin_mask(original, tone, sat)
    broad = smoothstep(0.015, 0.06, rg) * (1.0 - smoothstep(0.28, 0.48, rg))
    broad *= smoothstep(0.008, 0.045, gb)
    broad *= smoothstep(0.08, 0.20, tone) * (1.0 - smoothstep(0.86, 0.97, tone))
    broad *= smoothstep(0.05, 0.14, sat) * (1.0 - smoothstep(0.62, 0.82, sat))
    broad *= 1.0 - foliage
    skin = max(skin, broad)
    garment = smoothstep(0.10, 0.20, sat) * (1.0 - foliage) * (1.0 - skyish)
    keep = clamp01(max(skin, garment * 0.92))
    return tuple(graded[i] * (1.0 - keep) + original[i] * keep for i in range(3))


def guard(before: tuple[float, float, float], after: tuple[float, float, float]) -> tuple[float, float, float]:
    # Cada passo devolve pele e roupa. Branco alto não fica mais claro do que entrou.
    kept = keep_person(before, after)
    tone = luma(before)
    sat = saturation(before)
    hot = smoothstep(0.82, 0.94, tone) * (1.0 - smoothstep(0.02, 0.12, sat))
    if hot <= 0.001:
        return kept
    cap = luma(kept)
    limit = luma(before)
    if cap <= limit:
        return kept
    scale = limit / max(cap, 0.001)
    capped = tuple(kept[i] * scale for i in range(3))
    return mix(kept, capped, hot)


def exposure(rgb: tuple[float, float, float], bias: float) -> tuple[float, float, float]:
    if abs(bias) <= 0.0001:
        return rgb
    tone = luma(rgb)
    # O ganho cai no topo para camisa, nuvem e parede não estourarem.
    gain = bias * (1.0 - smoothstep(0.72, 0.94, tone))
    lifted = tuple(channel * (1.0 + gain) for channel in rgb)
    return guard(rgb, clamp3(lifted))


def shadows(rgb: tuple[float, float, float], amount: float) -> tuple[float, float, float]:
    # Abre só o preto esmagado. Meio-tom não sobe.
    if amount <= 0.0001:
        return rgb
    tone = luma(rgb)
    crushed = smoothstep(0.16, 0.02, tone)
    lift = amount * crushed * 0.55
    opened = tuple(channel + lift * (0.08 - channel) for channel in rgb)
    return guard(rgb, clamp3(opened))


def vibrance(
    rgb: tuple[float, float, float],
    amount: float,
    plant_extra: float,
    day: float = 0.0,
    calm: float = 0.0,
) -> tuple[float, float, float]:
    # Vivacidade seletiva. O parâmetro calm existe para o teste antigo chamar o dia junto.
    day = clamp01(day)
    amount *= 1.0 - 0.75 * day
    plant_extra *= 1.0 - day
    red, green, blue = rgb
    tone = luma(rgb)
    sat = saturation(rgb)
    shadow = smoothstep(0.08, 0.22, tone)
    not_white = 1.0 - smoothstep(0.72, 0.90, tone)
    headroom = 1.0 - smoothstep(0.28, 0.50, sat)
    protect = 1.0 - 0.80 * skin_mask(rgb, tone, sat)
    plant = smoothstep(0.03, 0.14, green - max(red, blue))
    plant *= 1.0 - smoothstep(0.55, 0.80, sat)
    green_dom = min(1.0, max(0.0, (green - max(red, blue)) / 0.12))
    blue_dom = min(1.0, max(0.0, (blue - max(red, green)) / 0.10))
    warm_dom = min(1.0, max(0.0, (red - max(green, blue) - 0.05) / 0.14))
    hue_bias = (1.0 - 0.65 * green_dom) * (1.0 - 0.55 * blue_dom) * (1.0 - 0.40 * warm_dom)
    gain = amount * shadow * not_white * headroom * protect * hue_bias * (1.0 + plant_extra * plant)
    out = [tone + (channel - tone) * (1.0 + gain) for channel in rgb]
    out_peak = max(out)
    if out_peak > 1.0:
        head = max(out_peak - tone, 0.001)
        room = max(1.0 - tone, 0.0)
        out = [tone + (channel - tone) * (room / head) for channel in out]
    colored = clamp3(tuple(out))
    if calm > 0.001:
        colored = day_calm(colored, day, calm)
    return colored


def color_vibrance(rgb: tuple[float, float, float], amount: float, plant_extra: float, day: float) -> tuple[float, float, float]:
    return guard(rgb, vibrance(rgb, amount, plant_extra, day, 0.0))


def day_calm(rgb: tuple[float, float, float], day: float, calm: float) -> tuple[float, float, float]:
    if day <= 0.001 or calm <= 0.001:
        return rgb
    red, green, blue = rgb
    tone = luma(rgb)
    sat = saturation(rgb)
    open_mid = smoothstep(0.16, 0.34, tone) * (1.0 - smoothstep(0.90, 0.98, tone))
    green_w = min(1.0, max(0.0, (green - max(red, blue)) / 0.08))
    warm = min(1.0, max(0.0, (min(red, green) - blue - 0.02) / 0.10))
    sky = min(1.0, max(0.0, (blue - max(red, green)) / 0.06))
    pull = calm * day * open_mid * (0.70 + green_w + 0.55 * warm + 0.35 * sky)
    pull *= 1.0 - 0.65 * skin_mask(rgb, tone, sat)
    pull = min(0.32, max(0.0, pull))
    calmed = [channel * (1.0 - pull) + tone * pull for channel in rgb]
    hot = smoothstep(0.86, 0.98, tone) * day
    calmed = [channel * (1.0 - hot) + (channel * 0.97 + 0.01) * hot for channel in calmed]
    return clamp3(tuple(calmed))


def apply_day(rgb: tuple[float, float, float], day: float, calm: float) -> tuple[float, float, float]:
    return guard(rgb, day_calm(rgb, day, calm))


def apply_night(rgb: tuple[float, float, float], day: float, amount: float) -> tuple[float, float, float]:
    # Só o véu azul do céu noturno. Poste, neon e planta não entram.
    if amount <= 0.0001:
        return rgb
    night = 1.0 - clamp01(day)
    if night <= 0.001:
        return rgb
    red, green, blue = rgb
    tone = luma(rgb)
    blue_dom = min(1.0, max(0.0, (blue - max(red, green)) / 0.08))
    band = smoothstep(0.05, 0.14, tone) * (1.0 - smoothstep(0.30, 0.46, tone))
    sat = saturation(rgb)
    gray = 1.0 - smoothstep(0.04, 0.18, sat)
    pull = amount * night * blue_dom * band * gray
    neutral = (tone, tone * 0.98, tone * 0.96)
    return guard(rgb, mix(rgb, neutral, clamp01(pull)))


def ambient_tone(rgb: tuple[float, float, float], amount: float) -> tuple[float, float, float]:
    # Sombra fica um fio mais neutra. Não pinta o meio-tom nem a vegetação.
    if amount <= 0.0001:
        return rgb
    tone = luma(rgb)
    shadow = smoothstep(0.42, 0.06, tone)
    sat = saturation(rgb)
    foliage = foliage_mask(rgb)
    weight = amount * shadow * (1.0 - smoothstep(0.20, 0.45, sat)) * (1.0 - foliage)
    weight *= 1.0 - skin_mask(rgb, tone, sat)
    cooled = (rgb[0] - 0.012, rgb[1] - 0.002, rgb[2] + 0.008)
    return guard(rgb, mix(rgb, clamp3(cooled), clamp01(weight)))


def contrast_mid(rgb: tuple[float, float, float], amount: float) -> tuple[float, float, float]:
    # Curva só no meio. Sombra e branco ficam quietos.
    if amount <= 0.0001:
        return rgb
    tone = luma(rgb)
    weight = smoothstep(0.12, 0.28, tone) * (1.0 - smoothstep(0.72, 0.90, tone))
    curved = tuple((channel - 0.50) * (1.0 + amount) + 0.50 for channel in rgb)
    return guard(rgb, mix(rgb, clamp3(curved), weight))


def tonemap(rgb: tuple[float, float, float], amount: float) -> tuple[float, float, float]:
    if amount <= 0.0001:
        return rgb
    mapped = tuple(channel + (shoulder(channel) - channel) * amount for channel in rgb)
    return guard(rgb, clamp3(mapped))


def highlight_recovery(rgb: tuple[float, float, float], amount: float) -> tuple[float, float, float]:
    # Canal estourado desce em direção aos outros. Branco neutro só encosta na joelha.
    if amount <= 0.0001:
        return rgb
    peak = max(rgb)
    floorc = min(rgb)
    if peak < 0.86:
        return rgb
    hot = smoothstep(0.86, 0.98, peak)
    sat = (peak - floorc) / max(peak, 0.001)
    colored = smoothstep(0.04, 0.18, sat)
    pulled = tuple(channel + (min(channel, peak * 0.92 + floorc * 0.08) - channel) * hot * colored * amount for channel in rgb)
    white = smoothstep(0.90, 0.98, peak) * (1.0 - smoothstep(0.02, 0.08, sat))
    knee = tuple(min(channel, 0.945) for channel in pulled)
    return guard(rgb, mix(clamp3(pulled), knee, white))


def color_protect(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    # Rede final: pele não vai para laranja nem cinza, e o branco não gruda em 1.
    red, green, blue = rgb
    tone = luma(rgb)
    sat = saturation(rgb)
    skin = skin_mask(rgb, tone, sat)
    orange = smoothstep(0.16, 0.28, red - green) * skin
    cooled = (red - 0.06 * orange, green, blue)
    gray = smoothstep(0.10, 0.02, sat) * skin * smoothstep(0.25, 0.45, tone)
    # Sem o quadro original não inventamos saturação. Só impedimos o laranja.
    _ = gray
    out = mix(rgb, clamp3(cooled), clamp01(orange))
    peak = max(out)
    if peak > 0.96 and sat < 0.08:
        out = tuple(channel * (0.955 / peak) for channel in out)
    foliage = foliage_mask(rgb)
    if foliage > 0.4 and sat > 0.62:
        pull = smoothstep(0.62, 0.80, sat) * foliage
        out = mix(out, tuple(tone + (channel - tone) * 0.72 for channel in out), pull)
    return clamp3(out)


def clear_pixel(rgb: tuple[float, float, float], day_strength: float, night_strength: float) -> tuple[float, float, float]:
    if day_strength <= 0.0 and night_strength <= 0.0:
        return rgb
    red, green, blue = rgb
    tone = luma(rgb)
    sat = saturation(rgb)
    day_gray = 1.0 - smoothstep(0.03, 0.16, sat)
    night_gray = 1.0 - smoothstep(0.02, 0.10, sat)
    day_band = smoothstep(0.30, 0.44, tone) * (1.0 - smoothstep(0.78, 0.90, tone))
    night_band = smoothstep(0.12, 0.20, tone) * (1.0 - smoothstep(0.32, 0.46, tone))
    veil_day = min(day_gray * day_band * day_strength, tone * 0.52)
    veil_night = night_gray * night_band * night_strength
    veil = max(veil_day, veil_night)
    if veil <= 0.001:
        return rgb
    scale = 1.0 / max(1.0 - veil, 0.001)
    return clamp3(tuple((channel - veil) * scale for channel in rgb))


def apply_color(rgb: tuple[float, float, float], edition: str, day: float) -> tuple[float, float, float]:
    spec = LOOK[canonical_edition(edition)]
    x = rgb
    if spec["exposure"] > 0:
        x = exposure(x, spec["exposure"])
    if spec["shadows"] > 0:
        x = shadows(x, spec["shadows"])
    graded = grade(x, edition)
    x = guard(x, graded)
    x = color_vibrance(x, spec["vibrance"], spec["plant"], day)
    x = ambient_tone(x, spec["ambient"])
    x = apply_day(x, day, spec["day_calm"])
    x = apply_night(x, day, spec["night"])
    x = contrast_mid(x, spec["contrast"])
    x = tonemap(x, spec["tonemap"])
    x = highlight_recovery(x, spec["highlight"])
    return color_protect(x)


def lamp_strength(level: int) -> float:
    if level <= 1:
        return 0.78
    if level == 2:
        return 0.98
    return 1.0


def lamp_chroma(color: tuple[float, float, float]) -> float:
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


def ring_stats(samples: list[float]) -> tuple[float, float, float, float]:
    lo = min(samples)
    hi = max(samples)
    cut = (lo + hi) * 0.5
    bright = [value for value in samples if value >= cut]
    dark = [value for value in samples if value < cut]
    bright_support = sum(bright) / len(bright)
    dark_support = sum(dark) / len(dark) if dark else bright_support
    dark_fraction = len(dark) / len(samples)
    return hi - lo, bright_support, dark_support, dark_fraction


def lamp_amount(
    color: tuple[float, float, float],
    near: tuple[float, float, float, float],
    far: tuple[float, float, float, float],
    strength: float,
    streak: float = 0.0,
) -> float:
    sodium = lamp_chroma(color)
    if sodium <= 0.001:
        return 0.0
    tone = luma(color)
    near_spread, near_bright, near_dark, near_fraction = near
    _far_spread, _far_bright, far_dark, far_fraction = far
    peak = smoothstep(0.012, 0.045, tone - near_bright)
    thin = smoothstep(0.34, 0.52, near_fraction) * smoothstep(0.05, 0.12, tone - near_dark)
    spill = smoothstep(0.05, 0.12, tone - near_dark) * smoothstep(0.08, 0.18, near_bright - tone)
    gradient = smoothstep(0.025, 0.07, near_spread) * (1.0 - smoothstep(0.16, 0.30, near_spread))
    wide = smoothstep(0.40, 0.65, far_fraction) * smoothstep(0.08, 0.16, tone - far_dark) * gradient
    on_surface = (1.0 - smoothstep(0.02, 0.28, near_fraction)) * (1.0 - smoothstep(0.03, 0.09, abs(tone - near_bright)))
    day_block = smoothstep(0.30, 0.40, far_dark)
    motion = clamp01(streak) * (1.0 - on_surface) * (1.0 - day_block)
    light = sodium * max(peak, thin, spill, wide, motion) * (1.0 - on_surface) * (1.0 - day_block)
    shade = 1.0 - smoothstep(0.10, 0.18, tone)
    light *= 1.0 - shade * (1.0 - min(1.0, peak + thin + spill + motion))
    return clamp01(light) * strength


def asphalt_mask(color: tuple[float, float, float]) -> float:
    tone = luma(color)
    sat = saturation(color)
    gray = 1.0 - smoothstep(0.05, 0.16, sat)
    band = smoothstep(0.05, 0.12, tone) * (1.0 - smoothstep(0.42, 0.62, tone))
    not_skin = 1.0 - skin_mask(color, tone, sat)
    not_plant = 1.0 - foliage_mask(color)
    not_lamp = 1.0 - lamp_chroma(color)
    blue = smoothstep(0.04, 0.12, color[2] - max(color[0], color[1]))
    return clamp01(gray * band * not_skin * not_plant * not_lamp * (1.0 - blue))


def road_blend(color: tuple[float, float, float], detail: float, strength: float) -> tuple[float, float, float]:
    mask = asphalt_mask(color) * strength
    if mask <= 0.001:
        return color
    # detail em torno de 0,5 é neutro. Abaixo escurece fissura, acima marca o agregado.
    gain = 1.0 + (detail - 0.5) * 0.55
    textured = tuple(clamp01(channel * gain) for channel in color)
    return mix(color, textured, mask)


def reflect_amount(color: tuple[float, float, float], dark_support: float, spread: float) -> float:
    mask = asphalt_mask(color)
    if mask <= 0.001:
        return 0.0
    tone = luma(color)
    glint = smoothstep(0.03, 0.10, tone - dark_support) * (1.0 - smoothstep(0.22, 0.40, spread))
    return mask * glint


def sharp_gain(color: tuple[float, float, float], detail_luma: float, strength: float) -> float:
    # Borda forte e folha perdem nitidez para não criar halo.
    edge = smoothstep(0.05, 0.16, abs(detail_luma))
    foliage = foliage_mask(color)
    tone = luma(color)
    sat = saturation(color)
    skin = skin_mask(color, tone, sat)
    return strength * (1.0 - 0.70 * edge) * (1.0 - 0.50 * foliage) * (1.0 - 0.85 * skin)


def bloom_weight(color: tuple[float, float, float], threshold: float) -> float:
    tone = luma(color)
    return clamp01((tone - threshold) / max(1.0 - threshold, 0.001))


def bloom_cap(base: tuple[float, float, float], glow: tuple[float, float, float], amount: float, threshold: float) -> tuple[float, float, float]:
    added = tuple(base[i] + glow[i] * amount for i in range(3))
    result = clamp3(added)
    tone = luma(base)
    sat = saturation(base)
    surface = 1.0 - smoothstep(0.04, 0.18, sat)
    cap_luma = min(0.948, max(tone, threshold) + 0.008)
    out_luma = luma(result)
    if surface > 0.001 and out_luma > cap_luma:
        scale = cap_luma / max(out_luma, 0.001)
        capped = tuple(result[i] * scale for i in range(3))
        result = mix(result, capped, surface)
    return clamp3(result)


def vignette(color: tuple[float, float, float], uv_x: float, uv_y: float, amount: float) -> tuple[float, float, float]:
    if amount <= 0.0001:
        return color
    edge = smoothstep(0.35, 0.92, ((uv_x - 0.5) ** 2 * 1.3225 + (uv_y - 0.48) ** 2) ** 0.5)
    return clamp3(tuple(channel * (1.0 - edge * amount) for channel in color))


# Custo aproximado em amostras de textura por pixel, a 1080p, com a técnica ligada.
# Número medido pela contagem do shader, não por GPU.
COST = {
    "FGM_Exposure": {"taps": 1, "tier": "baixo", "note": "1 amostra, sai cedo se o viés é zero"},
    "FGM_Shadows": {"taps": 1, "tier": "baixo", "note": "1 amostra, só no preto"},
    "FGM_Lut": {"taps": 3, "tier": "baixo", "note": "2 amostras da LUT 1024x32 e 1 do quadro"},
    "FGM_Color": {"taps": 5, "tier": "baixo", "note": "1 do quadro e 4 da cena para saber se é dia"},
    "FGM_AmbientTone": {"taps": 1, "tier": "baixo", "note": "1 amostra"},
    "FGM_Day": {"taps": 5, "tier": "baixo", "note": "sai cedo à noite"},
    "FGM_Night": {"taps": 5, "tier": "baixo", "note": "sai cedo de dia"},
    "FGM_Contrast": {"taps": 1, "tier": "baixo", "note": "1 amostra, fora do Low"},
    "FGM_Tonemap": {"taps": 1, "tier": "baixo", "note": "joelha no topo"},
    "FGM_HighlightRecovery": {"taps": 1, "tier": "baixo", "note": "sai cedo abaixo de 0,86"},
    "FGM_ColorProtection": {"taps": 1, "tier": "baixo", "note": "trava pele, branco e verde neon"},
    "FGM_ClearView": {"taps": 1, "tier": "baixo", "note": "sem kernel"},
    "FGM_Bloom": {"taps": 13, "tier": "médio", "note": "Ultra 13, High 9, Medium 5, Low desligado"},
    "FGM_Lamps": {"taps": 17, "tier": "médio", "note": "sai cedo sem amarelo; Ultra/High 8+8+4, Medium/Low 4+4+4"},
    "FGM_Roads": {"taps": 2, "tier": "baixo", "note": "1 do quadro e 1 da textura; sai cedo fora do asfalto"},
    "FGM_ReflectionsEnhance": {"taps": 9, "tier": "médio", "note": "Ultra 8, High/Medium 4, Low desligado"},
    "FGM_Sharp": {"taps": 5, "tier": "baixo", "note": "cruz de 4, folha e borda perdem força"},
    "FGM_Vignette": {"taps": 1, "tier": "baixo", "note": "1 amostra"},
    "FGM_FilmGrain": {"taps": 1, "tier": "baixo", "note": "desligado no preset"},
    "FGM_ChromaticAberration": {"taps": 3, "tier": "baixo", "note": "desligado no preset"},
    "FGM_Rain": {"taps": 20, "tier": "médio", "note": "desligado no preset; Ultra duas camadas"},
}
