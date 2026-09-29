# Arquitetura

```text
FiveM (DX11) → plugins\dxgi.dll (ReShade 6.8, ou um ReShade já instalado) → preset FGM → tela
```

Não há script de servidor, NUI nem resource. Os shaders leem só a imagem final, pelo cabeçalho `FGM.fxh`. Não pedem profundidade.

## Ordem

Quality: `FGM_Lut`, `FGM_Bloom`, `FGM_Sharp`, `FGM_Vignette`, `FGM_Rain`.

Performance: a mesma lista sem `FGM_Bloom`, com nitidez, vinheta e chuva mais baixas.

A LUT vem primeiro. O bloom só soma luz acima do limiar 0,80. A nitidez vem depois. A vinheta não fecha o centro. A chuva fica por último e desloca a amostra da imagem na gota.

## LUT

`grade()` em `tools/build_dist.py` gera uma faixa 32³, 1024×32. Quality usa contraste 1,09 a partir dos meios-tons, sombra cerca de 6,5% mais escura, tinta fria na sombra e quente na luz, saturação 0,91, um empurrão curto no azul de céu e no laranja de pôr do sol. Verde dominante recebe menos tinta, para vegetação e tons próximos de pele não virarem azul. Performance usa contraste 1,045, sombra 3% e saturação 0,95.

A LUT não sabe a hora do jogo. Pixel escuro escurece um pouco. Pixel que já é céu ou pôr do sol muda de cor dentro do quadro que o servidor desenhou.

## Chuva e sangue

`FGM_Rain.fx` desenha gotas procedurais com o timer do ReShade. A máscara exige cena escura, pouca saturação e distância do centro.

Não existe `FGM_Damage.fx`. O campo `effects.damage_blood` do manifesto fica `unavailable` até haver um sinal local que não leia memória do processo. O restante do mod não espera esse shader.

## Instalador

`tools/fgm-install-lib.ps1` é a implementação. `Instalar-FGM.ps1` é a entrada. O estado fica em `FiveM.app\FGM-state.json` e o backup em `FiveM.app\FGM-Backup`.

Trocar de edição copia a nova lista, apaga arquivos de pacote que só existiam na edição anterior e não mexe no backup original. Reparar recoloca arquivo ausente ou com hash diferente do manifesto.
