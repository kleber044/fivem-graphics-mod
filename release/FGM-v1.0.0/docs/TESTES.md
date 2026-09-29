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

`validate_dist.py` confere manifesto, SHA-256, LUT PNG, shaders, ausência de bloom na Performance e ausência de `fxmanifest.lua`, `server.cfg`, `client/`, `server/`, DLL e EXE dentro de `dist/` e `release/`.

`install_test.py` e `uninstall_test.py` usam uma pasta falsa de FiveM. Cobrem instalação, segunda instalação, Quality para Performance e o inverso, reparo, `dxgi.dll` de outro programa, FiveM ausente, pasta sem marcador, hash adulterado, ReShade compatível reutilizado, `d3d11.dll` já existente, ReShade antigo substituído, arquivo protegido, extração do setup oficial e restauração byte a byte.

O teste dentro do FiveM, com o jogo aberto num servidor, fica no Windows de quem for validar o visual. Estes testes não substituem isso.

As prévias sintéticas saem em imagens `preview-quality-*` e `preview-performance-*`: dia, noite e chuva. À esquerda está o quadro original; à direita, a grade. Na chuva, à direita entram as gotas.
