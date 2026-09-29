# Arquitetura

O produto é um preset de pós-processamento. O FiveM desenha o quadro; o ReShade, carregado de `plugins`, aplica os shaders FGM nessa imagem. Não há script Lua, NUI, resource nem arquivo de servidor.

```text
jogo (DX11) → ReShade em plugins\dxgi.dll → técnicas do preset FGM → tela
```

Os shaders leem só `ReShade::BackBuffer`. Não pedem buffer de profundidade, então continuam válidos quando o servidor ou o cliente bloqueia depth.

## Ordem das técnicas

Quality: `FGM_Lut`, `FGM_Bloom`, `FGM_Sharp`, `FGM_Vignette`, `FGM_Rain`.

Performance: a mesma lista sem `FGM_Bloom`. Nitidez, vinheta e chuva usam valores menores no `.ini`.

A LUT vem primeiro para a cor já estar definida. O bloom só soma luz em pixels que continuam muito claros. A nitidez vem depois do bloom para não acentuar o halo. A vinheta escurece a borda sem fechar o centro. A chuva fica por último para a gota não ser afiada de novo.

## LUT

`tools/build_dist.py` gera uma LUT 32×32×32 em faixa horizontal: largura 1024, altura 32. O eixo X é `fatia azul * 32 + vermelho`; o eixo Y é o verde. `FGM_Lut.fx` amostra as duas fatias vizinhas e interpola.

A função `grade()` é a fonte da cor, aplicada no mesmo espaço sRGB que o shader lê:

- Quality: contraste 1,08 só a partir dos meios-tons, sombra cerca de 6% mais escura com tinta fria, luz com tinta quente, saturação 0,93.
- Performance: contraste 1,04, sombra cerca de 3% mais escura, a mesma direção de cor, saturação 0,96.

Uma LUT não sabe a hora do jogo. “Noite mais escura” significa que pixel escuro recebe um escurecimento curto, sem ir para o preto. “Pôr do sol” significa que pixel já claro esquenta um pouco, sem saturação estourada. Céu, nuvem e sol continuam os do servidor; só a cor do quadro muda.

## Bloom, nitidez, vinheta, chuva

- `FGM_Bloom.fx` ignora pixel abaixo do limiar (0,78 na Quality). Farol e poste que já estão claros ganham halo. O resto da rua não é lavado.
- `FGM_Sharp.fx` é uma máscara de quatro vizinhos. Não é o CAS da AMD.
- `FGM_Vignette.fx` usa a distância ao centro.
- `FGM_Rain.fx` desenha gotas procedurais com o `timer` do ReShade. A máscara exige cena escura, pouca saturação e distância do centro. Não consulta o clima do jogo.

## Sangue

Não há shader de sangue. A limitação está em `COMPATIBILIDADE.md`.

## Pastas

```text
src/shaders/          fonte dos .fx e do FGM.fxh
tools/build_dist.py   gera dist/quality e dist/performance
tools/validate_dist.py
tools/apply_manifest.py
tools/preview_grade.py
dist/<edição>/manifest.json
dist/<edição>/FGM-*.ini
dist/<edição>/reshade-shaders/...
docs/
```

O manifesto é o contrato do instalador: origem no pacote, pasta e arquivo de destino no PC, backup e restauração.
