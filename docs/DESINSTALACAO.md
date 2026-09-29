# Desinstalação

O resource não edita `update.rpf`, `visualsettings.dat` nem a pasta do GTA. Remover o resource desliga o pacote.

## Parar sem apagar

No console do servidor:

```
stop fivem-graphics-mod
```

No cliente, ao parar, o script:

- limpa o timecycle principal e o extra de chuva
- zera a intensidade extra da chuva
- desliga trilha de pneu e pegada molhada forçadas
- devolve sombra e alcance de luz ao valor de sessão
- reaplica as chaves listadas em `shared/visual_settings.lua` (`restore`)
- esconde gotas e sangue

Também dá para desligar só no seu personagem, sem parar o resource para os outros:

```
/grafico desligar
```

## Remover de vez

1. Apague a linha `ensure fivem-graphics-mod` do `server.cfg`.
2. Apague `setr fgm_profile` se tiver colocado.
3. Pare o resource ou reinicie o servidor.
4. Apague a pasta `resources/fivem-graphics-mod`.

Peça para os jogadores reconectarem. Fechar o FiveM recarrega o `visualsettings.dat` dos arquivos do jogo. Isso completa a volta ao visual original, mesmo que outro script tenha alterado floats naquela sessão.

## ReShade

Se você instalou um preset desta pasta:

1. Abra o ReShade e escolha outro preset, ou desligue as técnicas.
2. Apague `Quality.ini` e `Performance.ini` da pasta do ReShade.
3. O ReShade em si pode permanecer instalado. Ele não faz parte do resource.

## O que não precisa desfazer

Não há backup de arquivo do jogo para restaurar por cima da instalação, porque a instalação não troca arquivo nenhum. A lista do que o resource mexe, e os valores usados ao parar, está em [BACKUP.md](BACKUP.md).
