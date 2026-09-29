# Compatibilidade

## Onde funciona

O preset entra no PC do jogador e altera a imagem **depois** que o FiveM desenha o quadro. Por isso:

- não depende de resource no servidor;
- não depende de `server.cfg`;
- não pede cargo de administrador nem ação do dono da cidade;
- vale em qualquer servidor que deixe o ReShade carregar.

O jogador precisa instalar no próprio Windows, na pasta `plugins` do FiveM, e carregar o preset no overlay do ReShade.

## Onde não funciona

- Servidor ou anticheat que encerra o jogo ao achar `dxgi.dll`, `d3d11.dll` ou ReShade. Não há variante “invisível” neste produto.
- FiveM aberto sem o ReShade na pasta `plugins`.
- Modo história, se você recortou o `dxgi.dll` para fora da pasta do GTA V (é o recomendado).
- As duas edições ao mesmo tempo. Instale Quality **ou** Performance.

Arquivo de resource (`fxmanifest.lua`, `__resource.lua`) não faz parte da entrega e não deve ser recriado para “forçar” o visual.

## O que a imagem consegue mudar

| Pedido | No pacote |
| --- | --- |
| Cor natural, contraste, noite um pouco mais escura | LUT 32³ gerada neste projeto. Pixel escuro desce e esfria; pixel claro sobe um pouco para o quente. |
| Nascer e pôr do sol | A LUT aquece o que já está claro. Ela não troca o relógio nem o céu do servidor. |
| Faróis e luzes urbanas | Edição Quality: bloom só acima de um limiar alto, para halo em farol, poste e sol. Performance: sem esse passe. |
| Nitidez | Máscara de contraste curta, mais forte em Quality. |
| Chuva na tela | Shader procedural nas bordas, com heurística de cena escura e pouco saturada. |
| Reflexo, poça, sombra, céu geométrico | Não mudam. Isso é desenho do jogo, não da imagem final. |

A chuva **não lê o clima do GTA**. Cena de dia clara fica sem gota. Noite, chuva e também túnel ou interior escuro podem mostrar gota. Dá para desligar só `FGM_Rain` no ReShade e manter o resto.

## Sangue na borda quando o jogador toma dano

Não está implementado.

O ReShade, do jeito usado aqui, só enxerga a imagem colorida já pronta. Ele não recebe a vida do ped, o evento de dano nem a arma. Sem essa informação, qualquer mancha vermelha seria um efeito falso, ligado o tempo todo ou por uma cor parecida com sangue na cena.

Ler a vida na memória do processo, injetar ASI ou criar um resource cliente exigiria outro tipo de programa. Isso deixa de ser um mod gráfico local, costuma ser bloqueado pelo mesmo anticheat que já observa DLL extra, e não entra neste produto.

Por isso a entrega traz só o que funciona de forma local e segura: grade, bloom controlado, nitidez, vinheta e gotas.
