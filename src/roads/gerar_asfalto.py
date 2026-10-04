"""Gera o asfalto do FGM. Não lê textura da Rockstar nem de outro mod.

A imagem é um detalhe em espaço de tela, com média perto de 0,5.
O shader multiplica só o pixel que já parece asfalto.
"""

from __future__ import annotations

import numpy as np


def _noise(size: int, cells: int, seed: int) -> np.ndarray:
    cells = max(2, min(cells, size))
    grid = np.random.default_rng(seed).random((cells, cells), dtype=np.float32)
    ys = np.linspace(0.0, cells, size, endpoint=False, dtype=np.float32)
    xs = np.linspace(0.0, cells, size, endpoint=False, dtype=np.float32)
    y0 = np.floor(ys).astype(np.int32)
    x0 = np.floor(xs).astype(np.int32)
    fy = ys - y0
    fx = xs - x0
    fy = fy * fy * (3.0 - 2.0 * fy)
    fx = fx * fx * (3.0 - 2.0 * fx)
    y1 = (y0 + 1) % cells
    x1 = (x0 + 1) % cells
    n00 = grid[np.ix_(y0, x0)]
    n10 = grid[np.ix_(y0, x1)]
    n01 = grid[np.ix_(y1, x0)]
    n11 = grid[np.ix_(y1, x1)]
    nx0 = n00 * (1.0 - fx)[None, :] + n10 * fx[None, :]
    nx1 = n01 * (1.0 - fx)[None, :] + n11 * fx[None, :]
    return nx0 * (1.0 - fy)[:, None] + nx1 * fy[:, None]


def _fbm(size: int, seed: int, octaves: int) -> np.ndarray:
    total = np.zeros((size, size), dtype=np.float32)
    weight = 0.0
    amp = 1.0
    cells = 4
    for octave in range(octaves):
        total += amp * _noise(size, cells, seed + octave * 17)
        weight += amp
        amp *= 0.5
        cells = min(size, cells * 2)
    return total / weight


def gerar(size: int, seed: int, cracks: float) -> bytes:
    """RGB 8 bits, lado `size`, costura nas bordas."""
    base = _fbm(size, seed, 5)
    grain = _noise(size, min(size, 96), seed + 90)
    fine = _noise(size, min(size, 192), seed + 140)
    ridge = 1.0 - np.abs(_fbm(size, seed + 30, 4) * 2.0 - 1.0)
    crack = np.clip((ridge - 0.78) / 0.18, 0.0, 1.0) * cracks
    dirt = _fbm(size, seed + 60, 3)
    detail = 0.50
    detail = detail + (base - 0.5) * 0.10
    detail = detail + (grain - 0.5) * 0.08
    detail = detail + (fine - 0.5) * 0.05
    detail = detail - crack * 0.22
    detail = detail + (dirt - 0.5) * 0.06
    detail = np.clip(detail, 0.18, 0.82)
    image = np.stack([detail, detail, detail], axis=-1)
    raw = (image * 255.0 + 0.5).astype(np.uint8).tobytes()
    return raw


def media(raw: bytes) -> float:
    return float(np.frombuffer(raw, dtype=np.uint8).mean() / 255.0)
