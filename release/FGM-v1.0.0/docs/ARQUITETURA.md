# Arquitetura

```text
FiveM (DX11) → plugins\dxgi.dll (ReShade 6.8, ou um ReShade já instalado) → preset FGM → tela
```

Não há script de servidor, NUI nem resource. Os shaders leem só a imagem final, pelo cabeçalho `FGM.fxh`. Não pedem profundidade.

## Ordem

Quality, ativas: `FGM_Lut`, `FGM_ClearView`, `FGM_Bloom`, `FGM_Lamps`, `FGM_Sharp`, `FGM_Vignette`.

Performance, ativas: `FGM_Lut`, `FGM_ClearView`, `FGM_Lamps`, `FGM_Sharp`, `FGM_Vignette`. A vivacidade, o horizonte e a nitidez ficam mais baixos, e não há bloom.

`FGM_Rain` está nas duas edições, mas fora de `Techniques=`. O preset só a lista em `TechniqueSorting=`, desmarcada. Enquanto estiver desmarcada, o passo não roda: menu, clima limpo e noite seca ficam sem gotas.

A LUT vem primeiro e já aplica a vivacidade seletiva. No fim desse passo, pele e roupa com cor voltam ao quadro original. `FGM_ClearView` reduz o véu do horizonte e o leite da noite antes do bloom, para esse véu não ser espalhado. O bloom da Quality só entra acima do limiar 0,93, com quantidade 0,05, para camisa, nuvem e calçada não ganharem halo e o véu distante não ser espalhado. `FGM_Lamps` entra depois do bloom e troca o amarelo da luz por branco neutro: núcleo, halo, ponto distante, rastro e reflexo claro. A superfície ao redor conserva a cor. A nitidez vem depois. A vinheta não fecha o centro. Se o jogador marcar `FGM_Rain`, ela entra por último.

## LUT

`grade()` em `tools/build_dist.py` gera uma faixa 32³, 1024×32. Quality usa contraste 1,06 a partir dos meios-tons e sombra cerca de 4% mais escura. Performance usa contraste 1,035 e sombra 2%. Uma joelha a partir de 0,78 segura o topo: branco continua branco, mas um valor perto de 1,00 não gruda no estouro. O empurrão de céu e de pôr do sol é curto. Verde dominante recebe menos tinta fria.

A vivacidade fica no shader `FGM_Lut.fx`. Quality abre em 0,14 e Performance em 0,08. Verde, azul de céu e laranja forte recebem só uma fração desse ganho. Sombra, branco, pele e cor que já está viva quase não mexem. O extra de vegetação é 0,04 na Quality e zero na Performance. Esses números valem na cena escura.

Quando a vizinhança a 160 pixels está clara, entra a calma do dia. Quality abre em 0,22 e Performance em 0,14. A vivacidade cai, o extra de verde sai, e verde, amarelo e azul perdem um pouco de cor. Branco alto desce um fio, sem virar cinza. Cena escura deixa essa conta em zero, então a noite não muda.

Depois da grade, `FGM_KeepPerson` devolve a cor original da pele e da roupa que já tem saturação. Grama e céu azul claro não entram nessa devolução, para o dia não voltar saturado. O poste amarelo também volta um instante à cor do jogo e o passo seguinte continua trocando essa luz por branco neutro.

## Postes

`FGM_Lamps.fx` tem três níveis no slider Postes: 1 Soft (0,78), 2 Neutral (0,98) e 3 White LED (1,00). Quality abre em White LED. Performance abre em Neutral. O alvo é branco neutro, com a mesma luminância. Não empurra para o azul.

Entra amarelo ou laranja de saturação média que se comporta como luz: pico local, fio fino, halo com queda, ou reflexo mais claro que o chão e mais escuro que a lâmpada. O anel de 56 pixels separa isso de uma superfície contínua. O anel de 140 pixels pega halo largo. Se até a metade escura desse anel está clara, a cena é dia e o pôr do sol fica. Quality lê 8 amostras. Performance lê 4.

Parede, fachada, rua sem o reflexo da lâmpada e janela plana conservam a cor, porque a vizinhança repete o mesmo tom. Farol quase branco, neon, semáforo e freio ficam de fora pela cor. Um farol amarelo, parecido com poste, pode clarear. O manifesto marca `effects.street_lamps` como `local-approximation`.

## Horizonte

`FGM_ClearView.fx` trata duas faixas, sem profundidade e sem kernel. O horizonte de dia, claro e quase sem cor, usa força 0,50 na Quality e 0,34 na Performance, entre cerca de 0,30 e 0,90 de luminância. O véu de dia não passa de 0,52 da luminância do pixel, para o prédio distante clarear sem virar buraco. Cor com saturação acima de cerca de 0,16 fica de fora: pele, roupa, planta e céu saturado não são empurrados. O leite da noite só entra quando a saturação está abaixo de cerca de 0,10, entre 0,12 e 0,46 de luminância, com força 0,14 e 0,09. Sombra escura e branco de camisa ficam de fora. O slider Horizonte vai de 0 a 3. O manifesto marca `effects.clear_view` como `local-approximation`.

## Chuva e sangue

`FGM_Rain.fx` desenha gotas na lente com o timer do ReShade: borda da tela, tamanho variado, movimento e um desvio curto da imagem atrás da gota. `RainStrength` é a intensidade. Quality guarda 0,72, duas camadas e distorção 1,00. Performance guarda 0,30, uma camada e distorção 0,35. Esses números só valem depois que a técnica é marcada.

Não há leitura de clima. `GET_RAIN_LEVEL` e o estado do servidor não chegam a um shader de ReShade. Uma resource cliente foi descartada: este pacote não é resource. Profundidade do GTA fica bloqueada no multijogador e não serve de sinal. Ler memória, usar ASI ou hook de processo também fica de fora. Uma heurística de quadro escuro e pouco saturado foi removida: ela acendia gotas no menu, à noite, em túnel e em interior, e as escondia na chuva de dia.

O manifesto marca `effects.screen_rain` como `manual-toggle`. Isso não é detecção automática.

Não existe `FGM_Damage.fx`. O campo `effects.damage_blood` do manifesto fica `unavailable` até haver um sinal local que não leia memória do processo. O restante do mod não espera esse shader.

## Instalador

`tools/fgm-install-lib.ps1` é a implementação. `Instalar-FGM.ps1` é a entrada. O estado fica em `FiveM.app\FGM-state.json` e o backup em `FiveM.app\FGM-Backup`.

Trocar de edição copia a nova lista, apaga arquivos de pacote que só existiam na edição anterior e não mexe no backup original. Reparar recoloca arquivo ausente ou com hash diferente do manifesto.
