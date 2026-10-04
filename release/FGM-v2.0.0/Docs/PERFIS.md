# Perfis

Quatro presets. Os números abaixo são os do arquivo `.ini` gerado por `tools/build_dist.py`.

| | Ultra | High | Medium | Low |
| --- | --- | --- | --- | --- |
| Atalho antigo | Quality | — | — | Performance |
| Preset | `FGM-Ultra.ini` | `FGM-High.ini` | `FGM-Medium.ini` | `FGM-Low.ini` |
| Vivacidade | 0,12 | 0,10 | 0,07 | 0,05 |
| Verde extra | 0,03 | 0,02 | 0,01 | 0 |
| Calma do dia | 0,10 | 0,09 | 0,08 | 0,06 |
| Véu do dia | 0,18 | 0,14 | 0,10 | 0,08 |
| Exposição | desligada | desligada | desligada | desligada |
| Tom de ambiente | desligado | 0,012 | 0,010 | 0,006 |
| Joelha | 0,12 | 0,10 | 0,08 | 0,06 |
| Recuperação de luz | 0,22 | 0,18 | 0,14 | 0,10 |
| Véu da noite | 0,12 | 0,105 | 0,085 | 0,07 |
| Bloom | 0,04 acima de 0,94, 13 amostras | 0,028 acima de 0,95, 9 | 0,015 acima de 0,97, 5 | desligado |
| Postes | White LED, 8 | White LED, 8 | Neutral, 4 | Neutral, 4 |
| Asfalto | 1024 px, força 0,12 | 512 px, 0,10 | 512 px, 0,07 | 256 px, 0,04 |
| Reflexo de asfalto | 0,20, 8 amostras | 0,14, 4 | 0,08, 4 | desligado |
| Nitidez | 0,26 | 0,20 | 0,14 | 0,09 |
| Chuva, se o jogador ligar | 0,70, 2 camadas | 0,55, 2 | 0,35, 1 | força 0 |
| Grão e aberração | desligados, força 0 | igual | igual | igual |

## Gráficos do GTA que o instalador escreve

Só se a chave já existir em `settings.xml`.

| Chave | Ultra | High | Medium | Low |
| --- | --- | --- | --- | --- |
| TextureQuality | 2 | 2 | 1 | 0 |
| ShaderQuality | 2 | 2 | 1 | 0 |
| ShadowQuality | 3 | 2 | 1 | 0 |
| ReflectionQuality | 2 | 2 | 1 | 0 |
| ParticleQuality | 2 | 1 | 1 | 0 |
| GrassQuality | 3 | 2 | 1 | 0 |
| PostFX | 3 | 2 | 1 | 0 |
| AnisotropicFiltering | 16 | 16 | 8 | 4 |
| SSAO | 2 | 2 | 1 | 0 |
| WaterQuality | 2 | 1 | 1 | 0 |
| Shadow_SoftShadows | 3 | 2 | 1 | 0 |
| LodScale | 1 | 0,8 | 0,4 | 0 |
| Shadow_Distance | 1,2 | 1 | 1 | 1 |

Leitura usada: textura e shader 0–2, sombra e post FX 0–3, grama 0–5, reflexo 0–3, anisotrópico até 16. O jogo pode regravar um valor que não aceitar. O backup continua sendo o arquivo de antes do FGM.

## Só recomendação

Não são escritos pelo instalador:

- MSAA e TXAA
- versão do DirectX
- FXAA
- profundidade de campo
- motion blur
- Ultra Shadows
- densidade de cidade e pedestres
- `MaxLodScale` e streaming em voo

Ultra fica melhor com FXAA ligado e DOF desligado. Ultra Shadows e distância estendida ficam a critério de quem tem folga de FPS.
