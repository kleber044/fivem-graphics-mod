# Compatibilidade

O FGM é um pacote local, no PC do jogador. Não usa ESX, QBCore, vRP, resource, `fxmanifest.lua` nem `server.cfg`.

Funciona em servidor que deixa o jogador usar ReShade. Se o servidor bloqueia com Pure Mode ou outra restrição, o mod não entra. Isso é respeitado: não há bypass, hook de cheat nem leitura de memória.

O shader lê a imagem final. Não depende de profundidade do GTA, que no multijogador costuma vir bloqueada.

Um `dxgi.dll` que não é ReShade fica intocado. O script avisa e não instala o resto por cima dele.

O `settings.xml` é o do GTA em Documentos, o mesmo arquivo que o FiveM usa na maior parte das instalações. Se a cidade ou o cliente guardarem gráfico em outro lugar, o FGM não adivinha: os shaders instalam mesmo assim e as opções ficam como recomendação em `docs/PERFIS.md`.

Não há suporte a add-on do ReShade. A versão pedida é a oficial 6.8.0, e qualquer ReShade 5 ou mais novo já instalado é mantido.
