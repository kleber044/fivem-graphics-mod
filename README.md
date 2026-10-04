# FGM 2.0.0 — mod gráfico local para FiveM

Pacote visual para o PC do jogador. A pasta de teste é `release/FGM-v2.0.0`.

No Windows, feche o FiveM e dê dois cliques em `Instalar-Ultra.cmd`, `Instalar-High.cmd`, `Instalar-Medium.cmd` ou `Instalar-Low.cmd`. O script acha o FiveM, baixa o ReShade 6.8.0 em reshade.me se ainda não houver um compatível, copia só os arquivos daquele perfil e seleciona o preset. Se existir `settings.xml` do GTA em Documentos, ele é copiado para o backup e as chaves gráficas que já estão lá recebem o valor do perfil. `Desinstalar.cmd` devolve o backup dos shaders e o `settings.xml` original.

Não há resource de servidor. Um perfil substitui o outro.

`Instalar-Quality.cmd` instala Ultra. `Instalar-Performance.cmd` instala Low.

Ultra é o visual principal: pele e roupa ficam na cor do jogo, o dia perde o excesso de saturação, o véu branco do horizonte desce, e à noite o poste, o halo, a luz distante, o rastro e o reflexo claro no asfalto ficam em branco neutro. High chega perto, com menos bloom e menos amostras. Medium equilibra. Low guarda a mesma direção com o mínimo de passos e sem bloom.

`FGM_Rain`, o grão e a aberração cromática começam desligados. O ReShade local não vê o clima do servidor nem o menu do FiveM. Sangue ao tomar dano não faz parte do pacote.

O asfalto é uma textura original deste repositório, usada só como detalhe em espaço de tela. O FGM não edita `update.rpf`.

O detalhe está em `docs/`.
