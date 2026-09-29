# Arquitetura

```text
FiveM (DX11) → plugins\dxgi.dll (ReShade 6.8, ou um ReShade já instalado) → preset FGM → tela
```

Não há script de servidor, NUI nem resource. Os shaders leem só a imagem final, pelo cabeçalho `FGM.fxh`. Não pedem profundidade.

## Ordem

Quality, ativas: `FGM_Lut`, `FGM_Bloom`, `FGM_Sharp`, `FGM_Vignette`.

Performance, ativas: a mesma lista sem `FGM_Bloom`, com nitidez e vinheta mais baixas.

`FGM_Rain` está nas duas edições, mas fora de `Techniques=`. O preset só a lista em `TechniqueSorting=`, desmarcada. Enquanto estiver desmarcada, o passo não roda: menu, clima limpo e noite seca ficam sem gotas.

A LUT vem primeiro. O bloom só soma luz acima do limiar 0,80. A nitidez vem depois. A vinheta não fecha o centro. Se o jogador marcar `FGM_Rain`, ela entra por último e desloca a amostra da imagem na gota.

## LUT

`grade()` em `tools/build_dist.py` gera uma faixa 32³, 1024×32. Quality usa contraste 1,09 a partir dos meios-tons, sombra cerca de 6,5% mais escura, tinta fria na sombra e quente na luz, saturação 0,91, um empurrão curto no azul de céu e no laranja de pôr do sol. Verde dominante recebe menos tinta, para vegetação e tons próximos de pele não virarem azul. Performance usa contraste 1,045, sombra 3% e saturação 0,95.

A LUT não sabe a hora do jogo. Pixel escuro escurece um pouco. Pixel que já é céu ou pôr do sol muda de cor dentro do quadro que o servidor desenhou.

## Chuva e sangue

`FGM_Rain.fx` desenha gotas na lente com o timer do ReShade: borda da tela, tamanho variado, movimento e um desvio curto da imagem atrás da gota. `RainStrength` é a intensidade. Quality guarda 0,72, duas camadas e distorção 1,00. Performance guarda 0,30, uma camada e distorção 0,35. Esses números só valem depois que a técnica é marcada.

Não há leitura de clima. `GET_RAIN_LEVEL` e o estado do servidor não chegam a um shader de ReShade. Uma resource cliente foi descartada: este pacote não é resource. Profundidade do GTA fica bloqueada no multijogador e não serve de sinal. Ler memória, usar ASI ou hook de processo também fica de fora. Uma heurística de quadro escuro e pouco saturado foi removida: ela acendia gotas no menu, à noite, em túnel e em interior, e as escondia na chuva de dia.

O manifesto marca `effects.screen_rain` como `manual-toggle`. Isso não é detecção automática.

Não existe `FGM_Damage.fx`. O campo `effects.damage_blood` do manifesto fica `unavailable` até haver um sinal local que não leia memória do processo. O restante do mod não espera esse shader.

## Instalador

`tools/fgm-install-lib.ps1` é a implementação. `Instalar-FGM.ps1` é a entrada. O estado fica em `FiveM.app\FGM-state.json` e o backup em `FiveM.app\FGM-Backup`.

Trocar de edição copia a nova lista, apaga arquivos de pacote que só existiam na edição anterior e não mexe no backup original. Reparar recoloca arquivo ausente ou com hash diferente do manifesto.
