# FGM — mod gráfico local para FiveM

Pacote visual para o PC do jogador. A pasta de teste é `release/FGM-v1.0.0`.

No Windows, feche o FiveM e dê dois cliques em `Instalar-Quality.cmd` ou `Instalar-Performance.cmd`. O script acha o FiveM, baixa o ReShade 6.8.0 em reshade.me se ainda não houver um compatível, copia os shaders desta edição e seleciona o preset. `Desinstalar.cmd` devolve o backup.

Não há resource de servidor. Quality e Performance não ficam ativas ao mesmo tempo.

Quality é o visual principal: pele e roupa ficam na cor do jogo, a grama e o céu do dia perdem o excesso de saturação, e o véu branco do horizonte desce forte. Debaixo de luz forte, o chão e a folha não recebem bloom nem nitidez extra. À noite o poste, o halo, a luz distante, o rastro e o reflexo no asfalto continuam em branco neutro, com menos leite cinza. Performance segue a mesma direção, com calma do dia mais leve, Neutral e menos vivacidade. Brancos claros continuam brancos, sem estourar. Farol branco, neon, semáforo e janela plana não viram branco, e a chuva na lente continua desligada.

`FGM_Rain` começa desligado. O ReShade local não detecta o clima do servidor nem o menu do FiveM, então não há gotas até o jogador marcar a técnica quando a chuva do jogo está na tela. Desmarcar some com elas. Sangue ao tomar dano não faz parte do pacote: um shader não vê a vida do personagem, e leitura de memória não entra neste produto.

O detalhe está em `docs/`.
