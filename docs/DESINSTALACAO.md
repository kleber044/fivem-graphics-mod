# Desinstalação

A remoção apaga só os arquivos que este pacote colocou em `plugins` e devolve os que tinham sido substituídos. O ReShade em si (`dxgi.dll`, `ReShade.ini`) permanece, porque não faz parte do pacote.

## Pelo manifesto

O contrato está em `dist/quality/manifest.json` ou `dist/performance/manifest.json`.

Para cada item de `files`:

1. Se a instalação guardou backup daquele destino, copie o backup de volta para o mesmo caminho.
2. Se não havia arquivo antes, apague o destino.
3. Não toque na lista `do_not_touch`.

`tools/apply_manifest.py` faz exatamente isso quando existe o recibo gerado por ele:

```text
python3 tools/apply_manifest.py uninstall --edition quality --plugins CAMINHO\plugins --backup CAMINHO\backup-fgm
```

No Windows o instalador futuro usa a mesma regra. O detalhe está em `INTEGRACAO_INSTALADOR.md`.

## Na mão

1. Feche o FiveM.
2. Abra `%LOCALAPPDATA%\FiveM\FiveM.app\plugins`.
3. Apague o preset da edição: `FGM-Quality.ini` ou `FGM-Performance.ini`.
4. Apague a pasta `reshade-shaders\Shaders\FGM`.
5. Apague a pasta `reshade-shaders\Textures\FGM`.
6. Se você tinha substituído algum desses arquivos, copie o backup de volta antes de apagar.
7. Deixe `dxgi.dll`, `d3d11.dll` (se você tiver renomeado) e `ReShade.ini` no lugar, a menos que queira remover o ReShade por completo.

## Remover o ReShade também

Isso é separado do FGM.

1. Apague `dxgi.dll` (ou `d3d11.dll`, se tiver sido renomeado) de `plugins`.
2. Apague `ReShade.ini` somente se você não quiser mais nenhuma configuração do ReShade.
3. Se você colou uma linha de reconhecimento em `CitizenFX.ini`, restaure o backup desse arquivo.
4. Confira que a pasta do GTA V não ficou com `dxgi.dll`.

Não restaure nem apague `update.rpf`. Este pacote nunca o altera.
