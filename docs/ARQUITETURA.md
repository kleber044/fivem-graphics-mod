# Arquitetura

```text
FiveM (DX11) → plugins\dxgi.dll (ReShade 6.8, ou um ReShade já instalado) → preset FGM → tela
```

Não há script de servidor, NUI nem resource. Os shaders leem só a imagem final, pelo cabeçalho `FGM.fxh`. Não pedem profundidade.

## Ordem

Quality, ativas: `FGM_Lut`, `FGM_ClearView`, `FGM_Bloom`, `FGM_Lamps`, `FGM_Sharp`, `FGM_Vignette`.

Performance, ativas: `FGM_Lut`, `FGM_ClearView`, `FGM_Lamps`, `FGM_Sharp`, `FGM_Vignette`. A vivacidade, o horizonte e a nitidez ficam mais baixos, e não há bloom.

`FGM_Rain` está nas duas edições, mas fora de `Techniques=`. O preset só a lista em `TechniqueSorting=`, desmarcada. Enquanto estiver desmarcada, o passo não roda: menu, clima limpo e noite seca ficam sem gotas.

A LUT vem primeiro e já aplica a vivacidade seletiva. `FGM_ClearView` reduz o véu branco antes do bloom, para o halo não espalhar essa névoa. O bloom da Quality continua só acima do limiar 0,80. `FGM_Lamps` entra depois do bloom: o núcleo do poste é neutralizado por último, senão o bloom devolve o amarelo para cima dele. A nitidez vem depois. A vinheta não fecha o centro. Se o jogador marcar `FGM_Rain`, ela entra por último.

## LUT

`grade()` em `tools/build_dist.py` gera uma faixa 32³, 1024×32. Quality usa contraste 1,11 a partir dos meios-tons, sombra cerca de 6% mais escura, tinta fria na sombra e um empurrão curto no azul de céu e no laranja de pôr do sol. Verde dominante recebe menos dessa tinta. Performance usa contraste 1,055 e sombra 2,8%. A LUT não reduz mais a saturação global.

A vivacidade fica no shader `FGM_Lut.fx`, no slider Vivacidade. Quality abre em 0,36 e Performance em 0,22. O ganho prefere meios-tons pouco saturados. Sombra, branco neutro, cor que já está forte e tom de pele recebem pouco. Verde da vegetação tem um acréscimo próprio, 0,28 na Quality e 0,14 na Performance, e para quando o verde já é alto.

A LUT não sabe a hora do jogo. Pixel escuro escurece um pouco. Pixel que já é céu ou pôr do sol muda de cor dentro do quadro que o servidor desenhou.

## Postes

`FGM_Lamps.fx` tem três níveis no slider Postes: 1 Soft (0,62), 2 Neutral (0,82) e 3 White LED (1,00). Quality abre em White LED. Performance abre em Neutral. No White LED o núcleo vai até o branco da própria luminância, sem ganhar brilho e sem passar para o azul. O halo mais fraco não entra nessa conta e continua quente.

O anel tem 32 pixels. Quality lê 8 amostras e tira a média; Performance lê 4. A média, em vez do ponto mais claro, deixa o núcleo passar mesmo quando o brilho em volta ainda é o halo. A faixa de cor é mais larga que a anterior, para pegar o âmbar do jogo, e continua cortando saturação alta de neon e semáforo.

O shader não recebe o tipo da luz. Farol quase branco, neon, semáforo, emergência, janela grande e pôr do sol ficam de fora. Um poste maior que o anel continua âmbar. Uma janela quente minúscula pode ser tratada como poste. O manifesto marca `effects.street_lamps` como `local-approximation`.

## Horizonte

`FGM_ClearView.fx` estima névoa branca por cor: luminância média-alta e saturação baixa. Não usa profundidade. O slider Horizonte vai de 0 a 3. Quality abre em 3 (força 0,34). Performance abre em 2 (força 0,22). Sombra, luz estourada e cor já saturada não entram, então a cena inteira não escurece e a neblina real só perde o leite. Não há kernel, para não desenhar halo. O manifesto marca `effects.clear_view` como `local-approximation`.

## Chuva e sangue

`FGM_Rain.fx` desenha gotas na lente com o timer do ReShade: borda da tela, tamanho variado, movimento e um desvio curto da imagem atrás da gota. `RainStrength` é a intensidade. Quality guarda 0,72, duas camadas e distorção 1,00. Performance guarda 0,30, uma camada e distorção 0,35. Esses números só valem depois que a técnica é marcada.

Não há leitura de clima. `GET_RAIN_LEVEL` e o estado do servidor não chegam a um shader de ReShade. Uma resource cliente foi descartada: este pacote não é resource. Profundidade do GTA fica bloqueada no multijogador e não serve de sinal. Ler memória, usar ASI ou hook de processo também fica de fora. Uma heurística de quadro escuro e pouco saturado foi removida: ela acendia gotas no menu, à noite, em túnel e em interior, e as escondia na chuva de dia.

O manifesto marca `effects.screen_rain` como `manual-toggle`. Isso não é detecção automática.

Não existe `FGM_Damage.fx`. O campo `effects.damage_blood` do manifesto fica `unavailable` até haver um sinal local que não leia memória do processo. O restante do mod não espera esse shader.

## Instalador

`tools/fgm-install-lib.ps1` é a implementação. `Instalar-FGM.ps1` é a entrada. O estado fica em `FiveM.app\FGM-state.json` e o backup em `FiveM.app\FGM-Backup`.

Trocar de edição copia a nova lista, apaga arquivos de pacote que só existiam na edição anterior e não mexe no backup original. Reparar recoloca arquivo ausente ou com hash diferente do manifesto.
