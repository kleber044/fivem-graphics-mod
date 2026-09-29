# Desinstalação

Feche o FiveM e dê dois cliques em `Desinstalar.cmd` dentro de `release/FGM-v1.0.0`.

O instalador lê `FiveM.app\FGM-state.json` e só mexe no que esse estado registra.

- Arquivo que já existia antes do FGM volta do backup.
- Arquivo que o FGM criou é apagado. Isso inclui shaders, LUT, preset, `dxgi.dll` e a licença, quando o próprio FGM os criou.
- ReShade que já estava instalado e foi apenas reutilizado permanece.
- Presets de terceiros que não estavam na lista do FGM permanecem.
- `CitizenFX.ini` não é lido para edição e não é restaurado, porque não foi alterado.
- A pasta `FGM-Backup` fica no disco. Apague-a só quando não precisar mais do histórico.

Sem `FGM-state.json` o desinstalador para. Ele não varre `plugins` apagando arquivos por nome.
