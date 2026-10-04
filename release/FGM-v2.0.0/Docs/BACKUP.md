# Backup

Na primeira instalação, o FGM cria `FiveM.app\FGM-Backup\<data-hora>\`.

Entram ali:

- cada arquivo de `plugins` que já existia e que o pacote ia substituir
- `ReShade.ini`, se já existia
- `dxgi.dll`, se o FGM for substituir um ReShade antigo
- `game-settings.xml`, cópia integral do `settings.xml` do GTA, se ele for alterado

A troca de perfil e o reparo usam o mesmo backup. Eles não substituem a cópia original por uma versão já modificada pelo FGM.

A desinstalação lê esse backup. Ela não apaga a pasta.

`Reparar.cmd` recoloca shader ausente ou com hash diferente do manifesto do perfil que está no estado, e reescreve as chaves gráficas daquele perfil em cima do `settings.xml` atual, sem jogar fora o backup original.
