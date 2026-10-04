# Arquitetura

```text
FiveM (DX11) → plugins\dxgi.dll (ReShade 6.8, ou um ReShade já instalado) → preset do perfil → tela
```

Não há script de servidor, NUI nem resource. Os shaders leem só a imagem final, pelo cabeçalho `FGM.fxh`. Não pedem profundidade, não leem memória e não distinguem o menu do jogo.

## Perfis

Ultra, High, Medium e Low. Quality é outro nome de Ultra. Performance é outro nome de Low. O estado gravado usa o nome canônico.

Cada perfil leva a própria LUT, a própria textura de asfalto e a própria lista de técnicas. Trocar de perfil apaga o arquivo de pacote que só existia no perfil anterior.

## Ordem

A ordem ligada, quando o passo existe naquele perfil:

1. `FGM_Exposure` — viés curto, some no branco. Ultra e High não ligam.
2. `FGM_Shadows` — abre só o preto esmagado
3. `FGM_Lut` — contraste, céu e pôr do sol da textura. A joelha da textura já existe aqui.
4. `FGM_Color` — vivacidade seletiva, menor de dia
5. `FGM_AmbientTone` — sombra um fio mais neutra. Ultra não liga: a distância pouco saturada virava cinza.
6. `FGM_Day` — só verde, amarelo e azul já saturados. Não puxa montanha nem mata distante para o luma.
7. `FGM_Night` — véu azul do céu, sai cedo de dia
8. `FGM_Contrast` — meio-tom; ausente no Low
9. `FGM_Tonemap` — joelha leve, depois da LUT. Não repete a joelha inteira.
10. `FGM_HighlightRecovery` — só canal acima de 0,94
11. `FGM_ColorProtection` — trava pele laranja, branco e verde neon
12. `FGM_ClearView` — de dia, só leite alto sem cor; a noite continua no leite baixo. Entra antes do bloom.
13. `FGM_Bloom` — ausente no Low; entra antes dos postes
14. `FGM_Lamps` — núcleo, halo, reflexo claro e rastro
15. `FGM_Roads` — detalhe de asfalto
16. `FGM_ReflectionsEnhance` — ausente no Low
17. `FGM_Sharp`
18. `FGM_Vignette`

Fora de `Techniques=`, só no overlay: `FGM_FilmGrain`, `FGM_ChromaticAberration`, `FGM_Rain`.

Cada passo de cor devolve pele e roupa para a cor com que aquele passo recebeu o pixel. O branco alto não fica mais claro do que entrou. `FGM_ColorProtection` é a trava final, sem o quadro original: o ReShade não compartilha textura entre arquivos `.fx`.

## O que cada shader faz

Não há shader só para aumentar a lista. Exposição não é a joelha. A joelha da LUT não é repetida por inteiro no tonemap. A recuperação de canal não trata céu a 0,88. O dia não dessatura o que já está lavado. O ClearView de dia não escurece montanha nem árvore distante. O asfalto não faz bloom.

No Ultra, exposição e tom de ambiente ficam de fora. Os dois levantavam ou esfriavam o meio-tom e, junto com a calma do dia e o véu largo, empilhavam um filtro cinza na distância. Poste, noite, asfalto, reflexo, pele e chuva desligada continuam como estavam.

## Postes

`FGM_Lamps.fx` separa núcleo, halo, fio, reflexo claro e rastro alongado. O alvo é branco neutro, com a mesma luminância. Parede, fachada, rua contínua, farol branco, neon, semáforo e freio ficam de fora. Ultra e High leem 8 amostras. Medium e Low leem 4. O rastro de 18 px existe nos quatro, para a luz não voltar amarela em velocidade.

## Asfalto

`FGM_Roads.fx` multiplica um detalhe só onde o pixel já parece asfalto. A textura muda de tamanho com o perfil: 1024, 512, 512 e 256. Isso não substitui o material do mundo. Ver `docs/ROAD_MOD.md`.

## Configuração do GTA

O instalador pode alterar chaves que já existem em `Documents\Rockstar Games\GTA V\settings.xml`. Antes, o arquivo inteiro vai para `FGM-Backup`. A desinstalação devolve esses bytes. Chave ausente não é criada. MSAA, DX, DOF, motion blur e Ultra Shadows não entram nessa lista.

## Instalador

`tools/fgm-install-lib.ps1` é a implementação. O estado fica em `FiveM.app\FGM-state.json`.
