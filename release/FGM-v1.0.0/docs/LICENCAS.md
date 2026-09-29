# Licenças

Auditoria do que a release distribui e do que ela baixa na instalação.

## Arquivos deste produto

Shaders em `src/shaders`, LUTs geradas por `tools/build_dist.py`, presets, manifestos, instalador e esta documentação foram escritos neste repositório. Não há cópia de NaturalVision, QuantV, VisualV, Razed, SweetFX, qUINT ou de arquivos da Rockstar e do FiveM.

O detentor do projeto pode vender e redistribuir esses arquivos. O aviso está em `licenses/FGM.txt`.

## ReShade 6.8.0

| Campo | Valor |
| --- | --- |
| Nome | ReShade |
| Autor | Patrick Mours (crosire) |
| Fonte oficial | https://reshade.me/downloads/ReShade_Setup_6.8.0.exe |
| Código | https://github.com/crosire/reshade |
| Versão pinada | 6.8.0, publicada em 2 de agosto de 2026 |
| Licença | BSD-3-Clause. Texto em `licenses/ReShade-BSD-3-Clause.txt` e em https://github.com/crosire/reshade/blob/main/LICENSE.md |
| Uso comercial | Permitido pela BSD-3-Clause |
| Redistribuição | A licença permite redistribuir o binário se o copyright, as condições e o aviso forem incluídos. O site oficial pede para não redistribuir binários e apontar para https://reshade.me/ |
| Neste produto | O binário não vai na release. O instalador baixa o setup oficial, confere SHA-256 `207aea16205fbf952bc8fe1879966672454cf04002e7ad34237c7990a5b3c0b4`, extrai `ReShade64.dll` (SHA-256 `b2945c29e7095491a901746b400e58db9b1592ab092bacf2a888ce37f02d08da`) e grava a licença ao lado quando ele mesmo instala a DLL |
| Endosso | O nome do autor não é usado como endosso do FGM |

Não usamos a build com add-ons. O pacote de shaders de `reshade-shaders` não é baixado. O cabeçalho `FGM.fxh` é deste projeto.

## O que não entra

- `update.rpf`, `visualsettings.dat`, timecycle e executáveis do GTA
- executáveis e `CitizenFX.ini` do FiveM
- DLL baixada de qualquer site que não seja reshade.me
