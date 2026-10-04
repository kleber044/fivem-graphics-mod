# Integração com o instalador

O app futuro pode chamar o mesmo script, sem duplicar a regra.

```text
powershell -NoProfile -ExecutionPolicy Bypass -File Instalar-FGM.ps1 -Command install -Edition ultra
```

Edições aceitas: `ultra`, `high`, `medium`, `low`, `quality`, `performance`. As duas últimas viram `ultra` e `low` antes de qualquer cópia.

Comandos: `install`, `switch`, `repair`, `uninstall`.

Saída em texto:

- `FGM install ok edition=ultra`
- `FGM switch ok edition=low`
- `FGM repair ok edition=high`
- `FGM uninstall ok`
- `FGM settings ok keys=TextureQuality,ShaderQuality,...`
- `FGM settings skip reason=settings.xml ausente`

Código 0 é sucesso. Código 1 escreve o motivo no erro padrão e não deveria deixar estado novo se a falha foi antes da gravação. Hash de pacote inválido não grava estado.

Parâmetros opcionais:

- `-FiveMRoot` para um FiveM fora do `%LOCALAPPDATA%`
- `-PackageRoot` se o app não estiver com os `.cmd` na mesma pasta do script
- `-RuntimeDll` só em teste, para não baixar o ReShade
- `-SettingsXml` se o `settings.xml` não estiver em Documentos

O estado fica em `FiveM.app\FGM-state.json`. O app pode ler `edition`, `version` e `settings.applied` dali. Não edite esse JSON à mão.

Os manifestos em `installer-manifests\` repetem origem, destino e SHA-256. O app não precisa copiar arquivo por conta própria: o script já recusa destino fora de `plugins`, recusa executável e recusa `CitizenFX.ini`.

`graphics.json`, na raiz da release, é a tabela que o script aplica. O app pode mostrar essa tabela antes de instalar. Mudar o JSON sem mudar o script não cria chave que o jogo não tenha.
