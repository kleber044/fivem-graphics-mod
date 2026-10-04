# Licenças

Auditoria do que a release 2.0.0 distribui e do que ela baixa na instalação.

## Arquivos deste produto

Shaders em `src/shaders`, LUTs geradas por `tools/build_dist.py`, asfalto gerado por `src/roads/gerar_asfalto.py`, presets, manifestos, instalador, `src/settings/graphics.json` e esta documentação foram escritos neste repositório. Não há cópia de NaturalVision, QuantV, VisualV, Razed, SweetFX, qUINT ou de arquivos da Rockstar e do FiveM.

O detentor do projeto pode vender e redistribuir esses arquivos. O aviso está em `licenses/FGM.txt`.

## ReShade 6.8.0

| Campo | Valor |
| --- | --- |
| Nome | ReShade |
| Versão | 6.8.0 |
| Autor | Patrick Mours (crosire) |
| URL oficial | https://reshade.me/ |
| Setup | https://reshade.me/downloads/ReShade_Setup_6.8.0.exe |
| Código | https://github.com/crosire/reshade |
| Licença | BSD-3-Clause. Texto em `licenses/ReShade-BSD-3-Clause.txt` |
| Uso comercial | Permitido pela licença |
| Redistribuição | A licença permite, desde que o copyright, as condições e o aviso acompanhem o binário. O site pede para não redistribuir o binário e apontar para https://reshade.me/ |
| Neste produto | O binário não vai na release. O instalador baixa o setup oficial, confere SHA-256 `207aea16205fbf952bc8fe1879966672454cf04002e7ad34237c7990a5b3c0b4`, extrai `ReShade64.dll` (SHA-256 `b2945c29e7095491a901746b400e58db9b1592ab092bacf2a888ce37f02d08da`, 5255448 bytes) e grava a licença ao lado quando ele mesmo instala a DLL |
| Endosso | O nome do autor não é usado como endosso do FGM |

Não usamos a build com add-ons. O pacote de shaders de `reshade-shaders` não é baixado. O cabeçalho `FGM.fxh` é deste projeto.

## NumPy

O gerador de asfalto usa NumPy só na máquina que monta o pacote. O NumPy não é instalado no PC do jogador e não vai na release.

| Campo | Valor |
| --- | --- |
| Nome | NumPy |
| Uso aqui | gerar o PNG na build |
| Licença | BSD-3-Clause |
| URL | https://numpy.org/ |
| No produto do jogador | não é redistribuído |

## O que não entra

- `update.rpf`, `visualsettings.dat`, timecycle e executáveis do GTA
- executáveis e `CitizenFX.ini` do FiveM
- DLL baixada de qualquer site que não seja reshade.me
- shader, LUT, textura ou preset de outro mod
