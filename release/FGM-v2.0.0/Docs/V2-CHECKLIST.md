# Checklist da 2.0.0

[OK] Produto local, sem resource, sem fxmanifest, sem server.cfg.
[OK] Quatro perfis: Ultra, High, Medium, Low. Quality instala Ultra. Performance instala Low.
[OK] Shaders próprios com função separada: exposição, sombra, LUT, cor, ambiente, dia, noite, contraste, tonemap, recuperação de luz, proteção, ClearView, bloom, postes, asfalto, reflexo, nitidez, vinheta, grão, aberração e chuva.
[OK] Chuva, grão e aberração nascem desligados. Low guarda a força da chuva em zero.
[OK] Postes em branco neutro, com máscara de núcleo, halo, reflexo e rastro. Sem leitura de memória.
[OK] Dia com calma de saturação e proteção de pele, roupa, branco e verde.
[OK] Noite com véu mais baixo que o dia e abertura só do preto esmagado.
[OK] Asfalto original em 1024, 512 e 256. Sem textura da Rockstar e sem edição de update.rpf.
[OK] settings.xml com backup, aplicação das chaves existentes e restauração. MSAA, executáveis e CitizenFX.ini ficam de fora.
[OK] Instalador, reparo, troca de perfil e desinstalação.
[OK] ReShade só da fonte oficial, com SHA-256, sem binário na release.
[OK] Licenças, documentação, manifestos e release `FGM-v2.0.0`.
[OK] Testes offline de regressão visual, pacote, hash, instalação e desinstalação.

[PENDENTE] Substituição real do material de rua do GTA. Motivo: exigiria `update.rpf` ou resource no servidor, e os dois estão fora do produto. No lugar entra o detalhe em espaço de tela.
[PENDENTE] Chuva automática. Motivo: o ReShade não recebe o clima do servidor sem resource ou leitura de memória.
[PENDENTE] FPS medido dentro do FiveM. Motivo: não há jogo nesta máquina. A contagem de amostras está em `docs/PERFORMANCE.md`. A rodada única está em `docs/TESTES.md`.
[PENDENTE] MSAA, Ultra Shadows, FXAA, DOF e distância estendida automática. Motivo: o custo e o conflito variam por PC. Ficam como recomendação.
