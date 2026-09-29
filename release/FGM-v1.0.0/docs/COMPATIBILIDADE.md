# Compatibilidade

O FGM funciona no PC do jogador, em servidores FiveM que deixam o ReShade carregar. Não depende do dono da cidade, de permissão administrativa nem de resource.

Ele não tenta atravessar Pure Mode, anticheat ou qualquer bloqueio. Se o servidor ou o anticheat impedir `dxgi.dll`, o mod não entra. Não há variante escondida.

## O que a imagem muda

| Efeito | Quality | Performance |
| --- | --- | --- |
| LUT cinematográfica | contraste e split de céu/pôr do sol mais presentes | a mesma direção, mais curta |
| Bloom | só em pixels já muito claros | ausente |
| Nitidez | máscara curta | mais baixa |
| Vinheta | leve, centro aberto | mais leve |
| Gotas na lente | desligadas; ao marcar, duas camadas e distorção | desligadas; ao marcar, uma camada e distorção menor |

A noite fica um pouco mais escura, com o preto ainda separado do zero para o detalhe não sumir. Cores muito saturadas descem. Verde de vegetação recebe menos tinta azul.

Céu, sol, poça, cone de farol e sombra do mundo continuam os que o servidor desenhou. O pacote só trata o quadro pronto. Farol e poste que já estão claros ganham halo na Quality. Reflexo de rua molhada e brilho de poça são shaders do jogo; um pós-processo não troca esses materiais.

## Chuva

A chuva do GTA e do FiveM continua a do jogo: partículas, poça, som e clima do servidor não são substituídos. O FGM só pode acrescentar gotas na lente, como água batendo na câmera.

Isso não liga sozinho. O ReShade instalado no PC recebe o quadro já desenhado. Esse quadro não diz se o servidor marcou chuva, qual é a intensidade nativa, nem se a imagem é o menu do FiveM. Tratar menu, noite ou túnel como chuva estava errado e foi removido. Não existe detecção automática neste pacote.

Com o preset de fábrica:

- sem a técnica marcada, não há gotas, inclusive no menu e em clima limpo;
- a chuva do jogo, quando existe, aparece sozinha, sem a camada extra da lente.

Para ver as gotas na tela:

1. Espere a chuva do jogo aparecer.
2. Abra o overlay do ReShade com Home.
3. Marque a técnica `FGM_Rain`.
4. Se a chuva do jogo estiver mais forte, suba Força das gotas. Quality já sugere 0,72 e duas camadas. Performance sugere 0,30 e uma camada.
5. Quando a chuva terminar, desmarque `FGM_Rain`. As gotas somem no quadro seguinte.

O menu do FiveM não é reconhecido pelo shader. A garantia de menu limpo vale enquanto `FGM_Rain` permanece desmarcada, que é o padrão e o estado depois que a chuva acaba. Se a técnica ficar marcada, o menu também mostra gotas. Desmarque antes de voltar a ele.

## Sangue ao tomar dano

Não está implementado e o mod não depende dele.

O shader local recebe o quadro colorido. A vida do personagem e o evento de dano não chegam nesse estágio. Sem isso, uma mancha vermelha seria um efeito falso.

Não usamos leitura de memória, ASI, hook de processo nem DLL fora do ReShade oficial. Essas vias deixam de ser um mod gráfico e podem ser tratadas como trapaça.

O manifesto marca `effects.damage_blood` como `unavailable`. Um sinal futuro só entra se for uma fonte local, documentada e sem leitura invasiva. Até lá não há shader de sangue no pacote.

## Edições

Quality e Performance não ficam ativas juntas. Trocar de uma para a outra remove os arquivos que só existiam na edição anterior, inclusive o bloom e a LUT que não pertencem à nova.
