# Instalação

Feche o FiveM. Na pasta `release/FGM-v2.0.0`, dê dois cliques em um destes arquivos:

- `Instalar-Ultra.cmd`
- `Instalar-High.cmd`
- `Instalar-Medium.cmd`
- `Instalar-Low.cmd`

`Instalar-Quality.cmd` instala Ultra. `Instalar-Performance.cmd` instala Low.

O script procura `%LOCALAPPDATA%\FiveM\FiveM.app` e exige `CitizenFX.ini` ou `FiveM.exe`. Se a pasta não existir, ele para e não cria nada.

## O que ele copia

Só para `FiveM.app\plugins`:

- os shaders daquele perfil
- a LUT daquele perfil
- a textura de asfalto daquele perfil
- o preset `FGM-Ultra.ini`, `FGM-High.ini`, `FGM-Medium.ini` ou `FGM-Low.ini`
- `ReShade.ini`, com o preset selecionado e o caminho dos shaders acrescentado

Arquivo que já estava em `plugins` é copiado para `FiveM.app\FGM-Backup\<data-hora>\` antes de ser substituído. A troca de perfil não mexe nesse primeiro backup. Arquivo que só existia no perfil anterior e foi criado pelo FGM é apagado.

## ReShade

Se `plugins\dxgi.dll` já for um ReShade 5.0.0 ou mais novo, ele permanece. O mesmo vale para `d3d11.dll` quando for o ReShade. Um `dxgi.dll` que não é ReShade não é substituído.

Se não houver ReShade compatível, o instalador baixa `https://reshade.me/downloads/ReShade_Setup_6.8.0.exe`, confere o SHA-256 do setup e o da `ReShade64.dll`, e grava a DLL como `plugins\dxgi.dll` junto com `ReShade-BSD-3-Clause.txt`. O binário não vem no zip do FGM.

## Gráficos do GTA

Se existir `Documents\Rockstar Games\GTA V\settings.xml`, ou a mesma pasta no OneDrive, o arquivo inteiro é copiado para o backup e as chaves listadas em `docs/PERFIS.md` são trocadas, somente quando já estão no arquivo. Se o arquivo não existir, a instalação dos shaders continua e o script avisa `FGM settings skip`.

Nada é escrito em `FiveM.exe`, `GTA5.exe`, `update.rpf` ou `CitizenFX.ini`.

## Depois

Abra o FiveM e entre num servidor que permita ReShade local. O preset do perfil já fica selecionado. Home abre o overlay. `FGM_Rain` aparece desmarcado.
