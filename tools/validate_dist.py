#!/usr/bin/env python3
"""Confere o pacote 2.0.0: manifesto, shaders, chuva desligada e ausência de resource."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RELEASE = ROOT / "release" / "FGM-v2.0.0"
REQUIRED_DOCS = [
    "INSTALACAO.md",
    "DESINSTALACAO.md",
    "BACKUP.md",
    "COMPATIBILIDADE.md",
    "LICENCAS.md",
    "ARQUITETURA.md",
    "INTEGRACAO_INSTALADOR.md",
    "TROUBLESHOOTING.md",
    "TESTES.md",
    "PERFIS.md",
    "PERFORMANCE.md",
    "ROAD_MOD.md",
]
FORBIDDEN_NAMES = {"fxmanifest.lua", "server.cfg", "__resource.lua"}
THIRD_PARTY_MARKERS = ("LumaSharpen", "qUINT", "BloomAndLensFlares", "SweetFX", "Technicolor")
EDITIONS = ("ultra", "high", "medium", "low")
ORDER = (
    "FGM_ClearView@FGM_ClearView.fx",
    "FGM_Bloom@FGM_Bloom.fx",
    "FGM_Lamps@FGM_Lamps.fx",
)


def fail(message: str) -> None:
    raise SystemExit(message)


def enabled_of(preset_text: str) -> list[str]:
    return preset_text.split("Techniques=", 1)[1].splitlines()[0].split(",")


def main() -> None:
    for name in REQUIRED_DOCS:
        if not (ROOT / "docs" / name).is_file():
            fail(f"documento ausente: docs/{name}")
    sizes = {}
    for edition in EDITIONS:
        folder = DIST / edition
        manifest_path = folder / "manifest.json"
        if not manifest_path.is_file():
            fail(f"manifesto ausente: {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("schema") != 3 or manifest.get("version") != "2.0.0":
            fail(f"{edition}: schema ou versão inesperados")
        if manifest.get("kind") != "client-local" or manifest.get("edition") != edition:
            fail(f"{edition}: manifesto não é o pacote local esperado")
        effects = manifest.get("effects", {})
        expected = {
            "damage_blood": "unavailable",
            "screen_rain": "manual-toggle",
            "street_lamps": "local-approximation",
            "clear_view": "local-approximation",
            "vibrance": "selective",
            "world_texture_replacement": "unavailable",
            "road_detail": "screen-space-original-texture",
            "film_grain": "optional-off",
            "chromatic_aberration": "optional-off",
        }
        for key, value in expected.items():
            if effects.get(key) != value:
                fail(f"{edition}: effects.{key} deveria ser {value}")
        for entry in manifest["files"]:
            source = folder / entry["source"]
            if not source.is_file():
                fail(f"origem inexistente: {source}")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            if entry.get("sha256") != digest:
                fail(f"sha256 divergente: {source}")
            if entry.get("restore_on_uninstall") != "restore_backup_or_delete":
                fail(f"restauração inesperada: {entry['source']}")
            if not entry["destination"].startswith("{fivem_plugins}/"):
                fail(f"destino fora de plugins: {entry['destination']}")
            if source.suffix == ".fx":
                text = source.read_text(encoding="utf-8")
                for marker in THIRD_PARTY_MARKERS:
                    if marker in text:
                        fail(f"shader de terceiros em {source}")
                if '#include "ReShade.fxh"' in text:
                    fail(f"depende de ReShade.fxh: {source}")
                if '#include "FGM.fxh"' not in text:
                    fail(f"shader sem cabeçalho local: {source}")
            if source.name in FORBIDDEN_NAMES:
                fail(f"arquivo de servidor: {source}")
        preset = folder / manifest["preset"]
        preset_text = preset.read_text(encoding="utf-8")
        enabled = enabled_of(preset_text)
        sorting = preset_text.split("TechniqueSorting=", 1)[1].splitlines()[0].split(",")
        for technique in enabled + sorting:
            filename = technique.split("@", 1)[1]
            if not (folder / "reshade-shaders" / "Shaders" / "FGM" / filename).is_file():
                fail(f"técnica sem shader: {technique}")
        if any(item.startswith("FGM_Rain@") for item in enabled):
            fail(f"{edition}: chuva não pode começar ligada")
        if "FGM_Rain@FGM_Rain.fx" not in sorting:
            fail(f"{edition}: chuva precisa existir desligada no overlay")
        if any(item.startswith("FGM_FilmGrain@") or item.startswith("FGM_ChromaticAberration@") for item in enabled):
            fail(f"{edition}: grão ou aberração não podem começar ligados")
        rain = (folder / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Rain.fx").read_text(encoding="utf-8")
        if "float weather" in rain or "cena escura" in rain:
            fail(f"{edition}: chuva ainda tenta adivinhar o clima")
        for required in ("FGM_Lamps@FGM_Lamps.fx", "FGM_ClearView@FGM_ClearView.fx", "FGM_Lut@FGM_Lut.fx", "FGM_ColorProtection@FGM_ColorProtection.fx", "FGM_Roads@FGM_Roads.fx"):
            if required not in enabled:
                fail(f"{edition}: falta {required}")
        if enabled.index("FGM_ClearView@FGM_ClearView.fx") > enabled.index("FGM_Lamps@FGM_Lamps.fx"):
            fail(f"{edition}: ClearView precisa entrar antes dos postes")
        bloom_file = folder / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Bloom.fx"
        if edition == "low":
            if bloom_file.exists() or "FGM_Bloom@" in preset_text:
                fail("low não pode carregar bloom")
            if "LAMP_TAPS=4" not in preset_text or "LampLevel=2" not in preset_text:
                fail("low precisa de Neutral com 4 amostras")
            if "RainStrength=0.000" not in preset_text:
                fail("low guarda a chuva em zero")
        else:
            if "FGM_Bloom@FGM_Bloom.fx" not in enabled:
                fail(f"{edition}: bloom precisa estar ligado")
            if enabled.index("FGM_Lamps@FGM_Lamps.fx") < enabled.index("FGM_Bloom@FGM_Bloom.fx"):
                fail(f"{edition}: postes precisam entrar depois do bloom")
        if edition in {"ultra", "high"} and "LAMP_TAPS=8" not in preset_text:
            fail(f"{edition}: precisa de 8 amostras nos postes")
        if edition == "ultra" and ("LampLevel=3" not in preset_text or "ColorVibrance=0.120" not in preset_text):
            fail("ultra precisa de White LED e vivacidade 0.120")
        if edition == "ultra" and ("BloomThreshold=0.940" not in preset_text or "BloomAmount=0.040" not in preset_text):
            fail("ultra precisa segurar o bloom")
        road = folder / "reshade-shaders" / "Textures" / "FGM" / "fgm_road.png"
        if road.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            fail(f"asfalto inválido: {road}")
        sizes[edition] = road.stat().st_size
        packaged = [entry["destination"] for entry in manifest["files"]]
        if "roads/" in "".join(packaged):
            fail(f"{edition}: a pasta roads/ não deve ser copiada para plugins")
        if manifest.get("backup_files") != packaged:
            fail(f"{edition}: backup divergente")
    if not (sizes["ultra"] > sizes["high"] >= sizes["medium"] > sizes["low"]):
        fail(f"VRAM do asfalto não cai com o perfil: {sizes}")
    if not RELEASE.is_dir():
        fail("release 2.0.0 ausente")
    for name in ("Instalar-Ultra.cmd", "Instalar-High.cmd", "Instalar-Medium.cmd", "Instalar-Low.cmd", "Instalar-Quality.cmd", "Instalar-Performance.cmd", "Desinstalar.cmd", "Reparar.cmd", "graphics.json"):
        if not (RELEASE / name).is_file():
            fail(f"release sem {name}")
    for title in ("Ultra", "High", "Medium", "Low"):
        if not (RELEASE / title / "manifest.json").is_file():
            fail(f"release sem {title}")
    quality = (RELEASE / "Instalar-Quality.cmd").read_text(encoding="utf-8")
    if "-Edition quality" not in quality:
        fail("Quality precisa continuar como atalho")
    for path in list(RELEASE.rglob("*")) + list(DIST.rglob("*")):
        if path.name in FORBIDDEN_NAMES or path.name.lower() in {"dxgi.dll", "d3d11.dll", "reshade64.dll"}:
            fail(f"arquivo proibido: {path}")
        if path.suffix.lower() == ".exe":
            fail(f"executável no pacote: {path}")
    print("pacote local ok")


if __name__ == "__main__":
    sys.exit(main())
