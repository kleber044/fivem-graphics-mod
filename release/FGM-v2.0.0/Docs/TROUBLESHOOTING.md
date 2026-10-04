# Problemas

**O instalador diz que o FiveM não está instalado.** A pasta `%LOCALAPPDATA%\FiveM\FiveM.app` não existe ou não tem `CitizenFX.ini` nem `FiveM.exe`. Nada foi criado.

**Existe dxgi.dll e ele não é ReShade.** Outro programa usa esse arquivo. O FGM não substitui. Tire o conflito à mão se souber o que é, ou deixe como está.

**O hash do ReShade não confere.** O download não é o arquivo pinado em `tools/reshade-official.json`. Nada é instalado. Confira a rede e tente de novo. Não use DLL de outro site.

**O preset não aparece.** Confirme que o jogo foi fechado durante a instalação e que `ReShade.ini` aponta para `FGM-Ultra.ini` ou o preset do perfil escolhido. `Reparar.cmd` reescreve essa chave sem apagar as outras.

**A chuva do shader aparece no menu.** Não deveria: a técnica nasce desmarcada. Se foi marcada, desmarque `FGM_Rain`. Força zero também não desenha.

**O poste continua amarelo.** White LED é o padrão de Ultra e High. Neutral, no Medium e no Low, chega perto e ainda deixa um resto. Farol amarelo parecido com poste pode clarear: a máscara é local, não sabe o nome do objeto.

**O dia ficou forte.** A calma do dia e a proteção de pele já limitam isso. Se ainda assim quiser menos cor, baixe Vivacidade e Calma do dia no overlay. Não é preciso reinstalar.

**O settings.xml não mudou.** O arquivo não estava em Documentos, ou as chaves não existiam. O FGM não cria chave nova. Ajuste pelo menu do jogo usando `docs/PERFIS.md`.

**Quero voltar atrás.** `Desinstalar.cmd`. O `settings.xml` e os arquivos de `plugins` que existiam antes voltam do backup.
