# Licenças

O que vai em `dist/` foi escrito neste repositório: shaders `.fx`, cabeçalho `FGM.fxh`, LUTs PNG, presets `.ini`, manifesto e esta documentação. Esse material pode ser vendido e redistribuído pelo dono do projeto. Não há shader, textura ou preset de outro mod gráfico dentro do pacote.

Nada em `dist/` foi copiado de NaturalVision, QuantV, VisualV, Razed, ou de pacotes SweetFX / qUINT / ReShade-shaders.

## Dependência externa

| Campo | Valor |
| --- | --- |
| Nome | ReShade |
| Origem | [https://reshade.me/](https://reshade.me/) e código em [https://github.com/crosire/reshade](https://github.com/crosire/reshade) |
| Licença | BSD-3-Clause. O texto acompanha o repositório oficial: [LICENSE.md](https://github.com/crosire/reshade/blob/main/LICENSE.md). |
| Uso comercial | Permitido pela BSD-3-Clause. |
| Redistribuição | Permitida, desde que se mantenham o aviso de copyright e o texto da licença, e que o nome do autor não seja usado para endossar o produto. |
| Neste pacote | **Não está incluído.** O jogador baixa o instalador oficial, sem add-ons. `dxgi.dll` e `ReShade.ini` não são arquivos nossos e o manifesto os lista em `do_not_touch`. |

Os shaders deste projeto não incluem `ReShade.fxh` do repositório [crosire/reshade-shaders](https://github.com/crosire/reshade-shaders). Aquele cabeçalho é CC0, mas o restante daquele repositório tem licenças variadas e não é necessário aqui. O arquivo `FGM.fxh` declara apenas o sampler da imagem, o `timer` e o vertex shader de tela cheia usados pelos nossos efeitos.

## O que o instalador não deve baixar nem embutir

- DLL do ReShade, para evitar redistribuir binário sem o texto da licença ao lado.
- Qualquer shader de `reshade-shaders` além do que está em `src/shaders`.
- `visualsettings.dat`, `timecycle` ou `update.rpf` da Rockstar. Esses arquivos não têm licença de redistribuição.
