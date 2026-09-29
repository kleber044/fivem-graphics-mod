#!/usr/bin/env python3
"""Confere o pacote local: manifesto, shaders originais e ausência de resource de servidor."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
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
]
FORBIDDEN_NAMES = {
    "fxmanifest.lua",
    "server.cfg",
    "__resource.lua",
}
THIRD_PARTY_MARKERS = (
    "LumaSharpen",
    "qUINT",
    "BloomAndLensFlares",
    "SweetFX",
    "Technicolor",
)


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    for name in REQUIRED_DOCS:
        if not (ROOT / "docs" / name).is_file():
            fail(f"documento ausente: docs/{name}")

    for edition in ("quality", "performance"):
        folder = DIST / edition
        manifest_path = folder / "manifest.json"
        if not manifest_path.is_file():
            fail(f"manifesto ausente: {manifest_path}")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("schema") != 2:
            fail(f"{edition}: schema precisa ser 2")
        if manifest.get("effects", {}).get("damage_blood") != "unavailable":
            fail(f"{edition}: sangue por dano não pode ser anunciado como disponível")
        if manifest.get("effects", {}).get("screen_rain") != "manual-toggle":
            fail(f"{edition}: chuva não pode ser anunciada como detecção automática")
        if manifest.get("effects", {}).get("street_lamps") != "local-approximation":
            fail(f"{edition}: postes não podem ser anunciados como detecção exata")
        if manifest.get("effects", {}).get("clear_view") != "local-approximation":
            fail(f"{edition}: horizonte não pode ser anunciado como leitura de profundidade")
        if manifest.get("effects", {}).get("vibrance") != "selective":
            fail(f"{edition}: vivacidade precisa ser seletiva")
        if manifest.get("kind") != "client-local":
            fail(f"{edition}: kind precisa ser client-local")
        if manifest.get("edition") != edition:
            fail(f"{edition}: edition do manifesto não confere")
        sources = []
        for entry in manifest["files"]:
            source = folder / entry["source"]
            if not source.is_file():
                fail(f"origem inexistente: {source}")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            if entry.get("sha256") != digest:
                fail(f"sha256 divergente: {source}")
            if "backup_if_exists" not in entry or "restore_on_uninstall" not in entry:
                fail(f"entrada sem backup/restauração: {entry['source']}")
            if not entry["destination"].startswith("{fivem_plugins}/"):
                fail(f"destino fora da pasta local do FiveM: {entry['destination']}")
            if entry["destination_dir"] != entry["destination"].rsplit("/", 1)[0]:
                fail(f"pasta de destino não confere: {entry['source']}")
            if entry["restore_on_uninstall"] != "restore_backup_or_delete":
                fail(f"política de restauração inesperada: {entry['source']}")
            sources.append(source)
            text = source.read_text(encoding="utf-8", errors="replace") if source.suffix in {".fx", ".ini", ".json", ".md"} else ""
            for marker in THIRD_PARTY_MARKERS:
                if marker in text:
                    fail(f"referência de shader de terceiros em {source}: {marker}")
            if source.suffix == ".fx" and '#include "ReShade.fxh"' in text:
                fail(f"shader depende do pacote de terceiros ReShade.fxh: {source}")
            if source.suffix == ".fx" and '#include "FGM.fxh"' not in text:
                fail(f"shader sem cabeçalho local: {source}")
        preset = folder / manifest["preset"]
        if not preset.is_file():
            fail(f"preset ausente: {preset}")
        preset_text = preset.read_text(encoding="utf-8")
        enabled = preset_text.split("Techniques=", 1)[1].splitlines()[0].split(",")
        sorting = preset_text.split("TechniqueSorting=", 1)[1].splitlines()[0].split(",")
        for technique in enabled + sorting:
            filename = technique.split("@", 1)[1]
            if not (folder / "reshade-shaders" / "Shaders" / "FGM" / filename).is_file():
                fail(f"técnica aponta para shader ausente: {technique}")
        if any(item.startswith("FGM_Rain@") for item in enabled):
            fail(f"{edition}: FGM_Rain está ativo no preset e apareceria sem chuva e no menu")
        if "FGM_Rain@FGM_Rain.fx" not in sorting:
            fail(f"{edition}: FGM_Rain precisa ficar disponível, desligado, no overlay")
        rain_shader = (folder / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Rain.fx").read_text(encoding="utf-8")
        if "float weather" in rain_shader or "cena escura" in rain_shader:
            fail(f"{edition}: FGM_Rain ainda usa heurística de cena escura")
        if "FGM_Lamps@FGM_Lamps.fx" not in enabled:
            fail(f"{edition}: FGM_Lamps precisa vir ligado")
        if "FGM_ClearView@FGM_ClearView.fx" not in enabled:
            fail(f"{edition}: FGM_ClearView precisa vir ligado")
        if edition == "quality":
            if "LAMP_TAPS=8" not in preset_text or "LampLevel=3" not in preset_text:
                fail("quality precisa de White LED com 8 amostras")
            if "ClearLevel=3" not in preset_text or "ColorVibrance=0.360" not in preset_text:
                fail("quality precisa de horizonte forte e vivacidade 0.360")
            if enabled.index("FGM_Lamps@FGM_Lamps.fx") < enabled.index("FGM_Bloom@FGM_Bloom.fx"):
                fail("os postes precisam entrar depois do bloom para o núcleo não voltar amarelo")
            if enabled.index("FGM_ClearView@FGM_ClearView.fx") > enabled.index("FGM_Bloom@FGM_Bloom.fx"):
                fail("a limpeza do horizonte precisa entrar antes do bloom")
        if edition == "performance":
            if "LAMP_TAPS=4" not in preset_text or "LampLevel=2" not in preset_text:
                fail("performance precisa de Neutral com 4 amostras")
            if "ClearLevel=2" not in preset_text or "ColorVibrance=0.220" not in preset_text:
                fail("performance precisa de horizonte médio e vivacidade 0.220")
            if "FGM_Bloom" in preset_text:
                fail("performance não pode ativar o bloom pesado")
        if edition == "quality" and "FGM_Bloom@FGM_Bloom.fx" not in preset_text:
            fail("quality precisa incluir bloom")
        header = folder / "reshade-shaders" / "Shaders" / "FGM" / "FGM.fxh"
        if not header.is_file():
            fail(f"{edition}: cabeçalho local ausente")
        if edition == "performance" and (folder / "reshade-shaders" / "Shaders" / "FGM" / "FGM_Bloom.fx").exists():
            fail("performance não deve carregar o shader de bloom")
        destinations = [entry["destination"] for entry in manifest["files"]]
        if manifest.get("backup_files") != destinations or manifest.get("restore_on_uninstall") != destinations:
            fail(f"{edition}: listas de backup e restauração divergem dos arquivos")
        lut = next(folder.glob("reshade-shaders/Textures/FGM/*.png"))
        signature = lut.read_bytes()[:8]
        if signature != b"\x89PNG\r\n\x1a\n":
            fail(f"LUT inválida: {lut}")
        for path in folder.rglob("*"):
            if path.name in FORBIDDEN_NAMES:
                fail(f"arquivo de servidor dentro do pacote: {path}")

    banned = [ROOT / "fxmanifest.lua", ROOT / "server.cfg", ROOT / "client", ROOT / "server"]
    for path in banned:
        if path.exists():
            fail(f"resto de resource de servidor: {path}")
    release = ROOT / "release" / "FGM-v1.0.0"
    if not release.is_dir():
        fail("release/FGM-v1.0.0 ausente")
    for name in ("Instalar-FGM.ps1", "fgm-install-lib.ps1", "reshade-official.json", "COMO-TESTAR.txt"):
        if not (release / name).is_file():
            fail(f"release sem {name}")
    for edition in ("Quality", "Performance"):
        if not (release / edition / "manifest.json").is_file():
            fail(f"release sem {edition}")
    for path in list(release.rglob("*")) + list(DIST.rglob("*")):
        if path.name in FORBIDDEN_NAMES or path.name.lower() in {"dxgi.dll", "d3d11.dll", "reshade64.dll"}:
            fail(f"arquivo proibido no pacote: {path}")
        if path.suffix.lower() == ".exe":
            fail(f"executável dentro do pacote: {path}")
    print("pacote local ok")


if __name__ == "__main__":
    sys.exit(main())
