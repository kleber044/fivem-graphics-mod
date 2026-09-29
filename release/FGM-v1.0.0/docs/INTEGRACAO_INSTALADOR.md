# Integração com o aplicativo

A entrada no Windows é `Instalar-FGM.ps1`. Os atalhos `.cmd` da release só chamam esse script. O aplicativo de venda pode usar os mesmos argumentos.

Pasta da release: `release/FGM-v1.0.0`.

O contrato por edição está em:

- `Quality/manifest.json` e `installer-manifests/quality.json`
- `Performance/manifest.json` e `installer-manifests/performance.json`
- `installer-manifests/commands.json`

## Detectar o FiveM

1. Expandir `%LOCALAPPDATA%`.
2. Usar `FiveM\FiveM.app` se essa pasta existir.
3. Exigir `CitizenFX.ini` ou `FiveM.exe` dentro dela.
4. Se faltar a pasta ou o marcador, mostrar o caminho tentado e parar. Não criar `FiveM.app` nem `plugins` nesse caso.
5. Instalação portátil: o usuário informa a pasta `FiveM.app` em `-FiveMRoot`. A mesma regra do marcador vale.

`plugins` só é criada depois que o FiveM foi reconhecido e o `dxgi.dll` existente, se houver, não é um hook estranho.

## Detectar o ReShade

| Situação | Ação |
| --- | --- |
| Sem `dxgi.dll` e sem `d3d11.dll` ReShade | Baixar o setup oficial, extrair `ReShade64.dll`, gravar como `plugins\dxgi.dll` e copiar a licença BSD |
| `dxgi.dll` contém ReShade e a versão é 5.0.0 ou mais nova, ou a versão não pôde ser lida | Reutilizar. Não substituir a DLL |
| `dxgi.dll` contém ReShade anterior a 5.0.0 | Backup e troca pela 6.8.0 |
| `dxgi.dll` não contém ReShade | Parar. Não substituir |
| Só `d3d11.dll` contém ReShade | Reutilizar esse arquivo e não criar um segundo `dxgi.dll` |

A versão sai do recurso `FileVersion` da DLL. O download usa a URL, o Referer e os dois SHA-256 de `reshade-official.json`. O setup oficial não é executado.

## Comandos

Todos recebem a pasta da release como diretório do script. Para chamar de outro lugar, passe `-PackageRoot`.

```text
powershell -NoProfile -ExecutionPolicy Bypass -File Instalar-FGM.ps1 -Command install -Edition quality
powershell -NoProfile -ExecutionPolicy Bypass -File Instalar-FGM.ps1 -Command install -Edition performance
powershell -NoProfile -ExecutionPolicy Bypass -File Instalar-FGM.ps1 -Command switch -Edition performance
powershell -NoProfile -ExecutionPolicy Bypass -File Instalar-FGM.ps1 -Command repair
powershell -NoProfile -ExecutionPolicy Bypass -File Instalar-FGM.ps1 -Command uninstall
```

`install` na edição já ativa repara. `install` na outra edição troca. `switch` exige uma instalação anterior.

Código de saída 0 é sucesso. Erro vai para a saída de erro e o código é 1. A frase de sucesso é `FGM install ok`, `FGM switch ok`, `FGM repair ok` ou `FGM uninstall ok`.

## Backup e estado

Estado: `%LOCALAPPDATA%\FiveM\FiveM.app\FGM-state.json`.

Backup: `%LOCALAPPDATA%\FiveM\FiveM.app\FGM-Backup\<data-hora>\files\`.

Cada item de `files` no estado tem `relative`, `sha256`, `action` (`created`, `replaced` ou `reused`) e `kind` (`package`, `runtime`, `license` ou `ini`). `originals` lista o que foi guardado, com o SHA-256 original. `runtime.action` diz se a DLL foi criada, trocada ou reutilizada. `edition` e `version` dizem o que está ativo.

O manifesto da edição lista o que pode ser copiado, com `source`, `destination`, `destination_dir`, `sha256`, `bytes`, `backup_if_exists` e `restore_on_uninstall`. A divisão entre criado e substituído só existe depois da instalação, no estado, porque depende do PC.

Antes de copiar, o instalador recalcula o SHA-256 da origem e compara com o manifesto. Se divergir, para sem gravar o estado.

## Troca, reparo, remoção

Troca: instala a lista da edição nova, apaga arquivos `kind=package` que não estão nessa lista e atualiza `PresetPath`. O backup original não é refeito com arquivo do FGM.

Reparo: confere cada arquivo do manifesto. Se faltar ou o hash não bater, copia de novo. Se o `dxgi.dll` que o FGM criou sumiu, baixa outra vez. Não apaga o backup.

Remoção: percorre `files` de trás para frente. `reused` fica. Se houver original, restaura. Senão, apaga. Remove o estado. Mantém `FGM-Backup`.

## Arquivos que não entram na cópia

`CitizenFX.ini`, `update.rpf`, `GTA5.exe`, `FiveM.exe` e qualquer `.exe`. O manifesto também os lista em `do_not_touch`.

`ReShade.ini`, `dxgi.dll` e `d3d11.dll` são tratados à parte, com backup, e não são apagados quando pertenciam ao jogador.
