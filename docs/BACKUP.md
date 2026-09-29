# Backup

O pacote não modifica arquivo do GTA V. O risco é substituir, dentro de `plugins`, um shader ou preset que o jogador já tinha com o mesmo caminho.

## O que guardar antes de instalar

Faça uma cópia da pasta inteira, que é o jeito mais simples de voltar atrás:

```text
%LOCALAPPDATA%\FiveM\FiveM.app\plugins
```

Se for editar o aviso do ReShade no F8, copie também:

```text
%LOCALAPPDATA%\FiveM\FiveM.app\CitizenFX.ini
```

## O que o manifesto marca para backup

Todo item em `files` tem `backup_if_exists: true`. A lista pronta está em `backup_files` no mesmo JSON.

A regra é: se o destino **já existe**, copiar esse arquivo para a pasta de backup do instalador, preservando o caminho relativo, e só então gravar o arquivo novo. Se o destino não existe, não há backup e a desinstalação apaga o arquivo.

Arquivos que o manifesto manda não tocar, mesmo que estejam na pasta:

- `{fivem_plugins}\ReShade.ini`
- `{fivem_plugins}\dxgi.dll`
- `{fivem_plugins}\d3d11.dll`
- `%LOCALAPPDATA%\FiveM\FiveM.app\CitizenFX.ini`
- `{gta_root}\update\update.rpf`

`{gta_root}` é a pasta do GTA V onde está `GTA5.exe`. Nada deste produto é gravado lá.

## Onde o teste deste repositório guarda o backup

`tools/apply_manifest.py` grava em `--backup/<edição>/files/` e um `receipt.json` ao lado. A desinstalação só restaura o que esse recibo marcou como `backed_up`.

Não reutilize um recibo de outra edição nem de outro PC.
