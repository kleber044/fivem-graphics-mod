# FGM — mod gráfico local para FiveM

Pacote visual para o PC do jogador. A pasta de teste é `release/FGM-v1.0.0`.

No Windows, feche o FiveM e dê dois cliques em `Instalar-Quality.cmd` ou `Instalar-Performance.cmd`. O script acha o FiveM, baixa o ReShade 6.8.0 em reshade.me se ainda não houver um compatível, copia os shaders desta edição e seleciona o preset. `Desinstalar.cmd` devolve o backup.

Não há resource de servidor. Quality e Performance não ficam ativas ao mesmo tempo.

Postes âmbar e pequenos ficam mais brancos nas duas edições, sem subir o brilho e sem esfriar o resto da noite. O slider Branco dos postes controla isso. Farol branco, neon e semáforo não entram nessa troca.

`FGM_Rain` começa desligado. O ReShade local não detecta o clima do servidor nem o menu do FiveM, então não há gotas até o jogador marcar a técnica quando a chuva do jogo está na tela. Desmarcar some com elas. Sangue ao tomar dano não faz parte do pacote: um shader não vê a vida do personagem, e leitura de memória não entra neste produto.

O detalhe está em `docs/`.
