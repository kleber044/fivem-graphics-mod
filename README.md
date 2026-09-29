# FGM — mod gráfico local para FiveM

Pacote visual **client-side** para o PC do jogador. Ele entra junto com o ReShade na pasta `plugins` do FiveM e vale em qualquer servidor que não bloqueie mod gráfico local.

Não existe `fxmanifest.lua`, `server.cfg` nem script de servidor. O dono da cidade não instala nada e o jogador não precisa de permissão administrativa.

Há duas edições prontas para copiar:

| Pasta | Uso |
| --- | --- |
| `dist/quality` | Melhor imagem: LUT mais marcada, bloom curto, nitidez maior, chuva em duas camadas. |
| `dist/performance` | O mesmo estilo, sem bloom, com nitidez, vinheta e chuva reduzidas. |

O que o pacote realmente faz é pós-processamento da imagem já desenhada pelo jogo: cor, contraste, bloom só em pixels claros, nitidez, vinheta e gotas na tela. Céu, poças, faróis e sombras do mundo continuam os do servidor. O detalhe está em `docs/ARQUITETURA.md`.

## Instalação rápida

1. Instale o [ReShade oficial](https://reshade.me/) **sem add-ons** e mova `dxgi.dll` e `ReShade.ini` para a pasta `plugins` do FiveM.
2. Copie o conteúdo de **uma** edição (`dist/quality` ou `dist/performance`) por cima dessa pasta, seguindo `manifest.json`.
3. No jogo, abra o ReShade (tecla Home) e carregue `FGM-Quality.ini` ou `FGM-Performance.ini`.

O passo a passo, o backup e a remoção estão em `docs/`.

## Efeito de sangue

Não faz parte do pacote. Um shader local não enxerga a vida do personagem, e um leitor de memória deixaria de ser um mod gráfico. A limitação está em `docs/COMPATIBILIDADE.md`.
