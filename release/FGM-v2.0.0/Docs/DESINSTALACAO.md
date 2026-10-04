# Desinstalação

Feche o FiveM e dê dois cliques em `Desinstalar.cmd`.

O script lê `FiveM.app\FGM-state.json` e, para cada arquivo que o FGM criou ou substituiu:

- devolve a cópia que estava no backup, se o arquivo já existia
- apaga o arquivo, se o FGM é quem criou

`settings.xml` do GTA, quando foi alterado, volta byte a byte para o que era antes da primeira instalação do FGM.

`CitizenFX.ini`, executáveis e `update.rpf` não entram nessa lista. Um ReShade que já estava instalado e foi só reutilizado continua no lugar. A DLL que o FGM baixou é removida, junto com a licença que ele gravou.

A pasta `FGM-Backup` permanece, para o caso de precisar da cópia. O `FGM-state.json` sai.

Sem o estado, o script para. Ele não varre o disco atrás de shader solto.
