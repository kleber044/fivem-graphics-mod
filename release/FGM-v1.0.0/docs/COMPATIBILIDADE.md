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
| Gotas na lente | duas camadas e distorção | uma camada e distorção menor |

A noite fica um pouco mais escura, com o preto ainda separado do zero para o detalhe não sumir. Cores muito saturadas descem. Verde de vegetação recebe menos tinta azul.

Céu, sol, poça, cone de farol e sombra do mundo continuam os que o servidor desenhou. O pacote só trata o quadro pronto. Farol e poste que já estão claros ganham halo na Quality. Reflexo de rua molhada e brilho de poça são shaders do jogo; um pós-processo não troca esses materiais.

## Chuva

As gotas não leem o clima do GTA. Elas aparecem quando o quadro está escuro e pouco saturado, principalmente nas bordas, com tamanho variado, movimento e um desvio leve da imagem atrás da gota. No sol elas somem. Túnel e interior escuro também podem mostrar gota.

No ReShade, a técnica `FGM_Rain` tem os controles Força das gotas, Camadas e Distorção. Performance já abre com valores menores.

## Sangue ao tomar dano

Não está implementado e o mod não depende dele.

O shader local recebe o quadro colorido. A vida do personagem e o evento de dano não chegam nesse estágio. Sem isso, uma mancha vermelha seria um efeito falso.

Não usamos leitura de memória, ASI, hook de processo nem DLL fora do ReShade oficial. Essas vias deixam de ser um mod gráfico e podem ser tratadas como trapaça.

O manifesto marca `effects.damage_blood` como `unavailable`. Um sinal futuro só entra se for uma fonte local, documentada e sem leitura invasiva. Até lá não há shader de sangue no pacote.

## Edições

Quality e Performance não ficam ativas juntas. Trocar de uma para a outra remove os arquivos que só existiam na edição anterior, inclusive o bloom e a LUT que não pertencem à nova.
