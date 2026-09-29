# Instalação

O FGM é um mod gráfico local. Ele entra na pasta `plugins` do FiveM no Windows do jogador. Não usa `server.cfg`, `fxmanifest.lua` nem resource da cidade.

A pasta pronta para teste é `release/FGM-v1.0.0`.

## No Windows

1. Feche o FiveM.
2. Abra `release/FGM-v1.0.0`.
3. Dê dois cliques em `Instalar-Quality.cmd` ou `Instalar-Performance.cmd`.

O script procura `%LOCALAPPDATA%\FiveM\FiveM.app`. No Explorer essa pasta aparece como FiveM Application Data. Se `CitizenFX.ini` ou `FiveM.exe` não estiver lá, a instalação para e não cria pasta em outro lugar.

Na primeira vez, o instalador baixa `ReShade_Setup_6.8.0.exe` somente de `https://reshade.me/downloads/ReShade_Setup_6.8.0.exe`, confere o SHA-256 e extrai `ReShade64.dll`. O setup gráfico não é executado. A DLL é copiada para `plugins\dxgi.dll`, com o texto da licença BSD ao lado.

Se já existir um ReShade 5 ou mais novo em `dxgi.dll` ou `d3d11.dll`, ele é reutilizado. Um `dxgi.dll` que não seja ReShade interrompe a instalação sem ser substituído.

O preset da edição fica selecionado em `ReShade.ini`. Chaves que já existiam nesse arquivo são mantidas. A cópia anterior vai para `FiveM.app\FGM-Backup\<data-hora>\`.

`FGM_Rain` não entra ligado. No jogo, Home abre o ReShade: marque essa técnica só enquanto a chuva do GTA estiver na tela e desmarque quando ela acabar. O detalhe está em `docs/COMPATIBILIDADE.md`.

## O que não fazer

Não copie a pasta para `resources`. Não edite `server.cfg`. Não instale as duas edições ao mesmo tempo: rode o instalador da outra edição para trocar.

`CitizenFX.ini`, `update.rpf` e os executáveis do GTA e do FiveM não são alterados.
