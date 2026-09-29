# Problemas comuns

## O instalador diz que o FiveM não está instalado

Ele só aceita `%LOCALAPPDATA%\FiveM\FiveM.app` quando existe `CitizenFX.ini` ou `FiveM.exe`. Instalação portátil pode ser indicada com `-FiveMRoot` apontando para essa pasta `FiveM.app`. Outro caminho é recusado e nada é criado.

## O download do ReShade falhou

A mensagem aparece antes de copiar shaders, quando a runtime ainda não está no PC. Confira a internet e se `https://reshade.me` abre. O arquivo baixado tem de bater com o SHA-256 de `tools/reshade-official.json`. Se não bater, a instalação para.

## Já existe um dxgi.dll

Se o arquivo não contém ReShade, o instalador para e deixa o arquivo como está. Não renomeie um hook de outro programa para forçar o FGM.

Se for um ReShade 5 ou mais novo, ele é mantido. Se for mais antigo que 5.0.0, o instalador guarda o DLL no backup e coloca o 6.8.0.

## O overlay não abre

O padrão do ReShade é a tecla Home. Se o F8 mostrar um aviso do ReShade 5 pedindo uma linha em `CitizenFX.ini`, copie o arquivo antes e cole somente a linha que o próprio F8 imprimir. O FGM não edita esse arquivo: o identificador é desta instalação.

Alguns jogadores precisam renomear `dxgi.dll` para `d3d11.dll` dentro de `plugins`. Faça isso só se o F8 indicar que `dxgi.dll` foi ignorado, e rode o reparo depois se o estado ainda apontar para `dxgi.dll`.

## O servidor fecha o jogo ou o ReShade não carrega

Pure Mode e anticheat podem bloquear a DLL. O FGM não contorna isso. Entre em outro servidor que permita mod gráfico local.

## Aparecem gotas sem chuva, ou no menu

`FGM_Rain` não detecta o clima. Se a técnica estiver marcada no overlay, as gotas entram em qualquer quadro, inclusive no menu e com o céu limpo. Desmarque `FGM_Rain`. O preset de fábrica já a entrega desmarcada.

## A chuva do jogo está na tela e não há gotas na lente

Isso é o padrão. Abra o ReShade com Home e marque `FGM_Rain`. Força das gotas controla a intensidade. Desmarque de novo quando a chuva acabar.

## As duas edições parecem misturadas

Feche o FiveM e rode de novo `Instalar-Quality.cmd` ou `Instalar-Performance.cmd`. A troca apaga bloom e LUT da edição que saiu.

## Quero voltar atrás

`Desinstalar.cmd` restaura o backup. A pasta `FGM-Backup` continua disponível se precisar conferir o SHA-256 de um original.
