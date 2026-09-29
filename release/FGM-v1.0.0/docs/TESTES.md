# Testes

No repositório, com Python 3:

```text
python3 tools/build_dist.py
python3 tools/validate_dist.py
python3 tools/verify_hashes.py
python3 tools/preview_grade.py
python3 tools/install_test.py
python3 tools/uninstall_test.py
```

`validate_dist.py` confere manifesto, SHA-256, LUT PNG, shaders, ausência de bloom na Performance, `FGM_Lamps` ligado antes do bloom na Quality e com 4 amostras na Performance, `LampWhite` 0,880 nas duas, `effects.street_lamps` igual a `local-approximation`, `FGM_Rain` fora de `Techniques=` e presente só em `TechniqueSorting=`, ausência da heurística de cena escura, `effects.screen_rain` igual a `manual-toggle`, e ausência de `fxmanifest.lua`, `server.cfg`, `client/`, `server/`, DLL e EXE dentro de `dist/` e `release/`.

`install_test.py` e `uninstall_test.py` usam uma pasta falsa de FiveM. Cobrem instalação, segunda instalação, Quality para Performance e o inverso, reparo, `dxgi.dll` de outro programa, FiveM ausente, pasta sem marcador, hash adulterado, ReShade compatível reutilizado, `d3d11.dll` já existente, ReShade antigo substituído, arquivo protegido, extração do setup oficial e restauração byte a byte.

O teste dentro do FiveM, com o jogo aberto num servidor, fica no Windows de quem for validar o visual. Estes testes não substituem isso.

As prévias sintéticas saem em imagens `preview-quality-*` e `preview-performance-*`: dia, noite e chuva. À esquerda está o quadro original. No dia e na noite, à direita entram a grade e a correção de postes. A noite de teste tem um núcleo de sódio, o halo quente em volta, uma janela, um farol branco, neon, semáforo e luz azul. A checagem exige o núcleo mais neutro, a mesma luminância, o mesmo branco na Quality e na Performance, e essas outras luzes paradas. O pôr do sol do dia também fica parado. Força zero no slider não mexe no âmbar.

O arquivo de chuva compara a lente limpa, com `FGM_Rain` desligado, e a mesma cena depois que a técnica é marcada. Não é uma captura do GTA e não simula detecção de clima: dia e noite recebem a mesma máscara de gota, força zero não pinta pixel, e a força maior cobre mais pixels do que a menor.
