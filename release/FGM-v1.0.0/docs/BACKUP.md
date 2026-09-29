# Backup

Antes de substituir qualquer arquivo, o instalador copia o original para:

```text
%LOCALAPPDATA%\FiveM\FiveM.app\FGM-Backup\<data-hora>\files\
```

O recibo fica em `FGM-state.json`, na pasta `FiveM.app`. Para cada original ele guarda:

- caminho relativo dentro de `plugins`
- caminho do backup
- SHA-256 do arquivo original

A segunda instalação e a troca de edição não substituem esse backup pelo arquivo do FGM. O original do jogador continua sendo o da primeira vez.

Também entram no backup, quando já existem:

- `ReShade.ini`
- `dxgi.dll`, se for um ReShade mais antigo que a versão mínima e for atualizado

Não são copiados nem alterados:

- `CitizenFX.ini`
- `update.rpf`
- `GTA5.exe`
- `FiveM.exe`

A desinstalação restaura esses backups e apaga só o que o FGM tinha criado.
