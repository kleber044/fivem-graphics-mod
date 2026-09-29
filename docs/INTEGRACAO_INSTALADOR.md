# Integração com o instalador

Cada edição tem o próprio contrato:

- `dist/quality/manifest.json`
- `dist/performance/manifest.json`

Schema `1`. `kind` é sempre `client-local`. Instale uma edição por vez.

## Campos

| Campo | Uso |
| --- | --- |
| `tokens.fivem_plugins` | `%LOCALAPPDATA%\FiveM\FiveM.app\plugins` |
| `tokens.fivem_plugins_explorer_name` | Nome que o Explorer mostra: `FiveM Application Data\plugins`. Não use esse nome como caminho de arquivo. |
| `preset` | `.ini` que o jogador seleciona no ReShade. |
| `files[].source` | Caminho relativo à pasta da edição, com `/`. |
| `files[].destination_dir` | Pasta de destino no PC, com o token `{fivem_plugins}`. |
| `files[].destination` | Arquivo de destino completo. |
| `files[].backup_if_exists` | `true`: se o destino já existe, copiar antes de substituir. |
| `files[].restore_on_uninstall` | `restore_backup_or_delete`. |
| `backup_files` | Os mesmos destinos, para quem só precisa da lista. |
| `restore_on_uninstall` | A mesma lista, na raiz do JSON. Na desinstalação, percorra de trás para frente. |
| `do_not_touch` | Nunca gravar, apagar ou restaurar estes caminhos. |
| `external_dependencies` | ReShade é obrigatório e **não** vem no pacote. |

Substitua `{fivem_plugins}` pelo caminho real e troque `/` pelo separador do Windows ao gravar.

## Detectar a pasta

1. Expandir `%LOCALAPPDATA%`.
2. Usar `FiveM\FiveM.app\plugins` se `FiveM.app` existir.
3. Se o usuário instalou o FiveM numa pasta portátil, pedir essa pasta. O token padrão cobre a instalação normal.
4. Criar `plugins` se `FiveM.app` existir e `plugins` ainda não existir.
5. Recusar o instalador se `dxgi.dll` e `d3d11.dll` estiverem ambos ausentes, e pedir para instalar o ReShade antes. Não baixe a DLL.

## Instalar

1. Ler o manifesto da edição escolhida.
2. Abortar se já existir um recibo desta edição (instalação duplicada).
3. Para cada item de `files`, na ordem:
   - resolver `destination`;
   - criar `destination_dir` se faltar;
   - se o arquivo de destino existe e `backup_if_exists` é verdadeiro, copiar para `backup/<edição>/files/` mantendo o caminho relativo;
   - copiar `source` por cima;
   - anotar no recibo se houve backup.
4. Não copiar `LEIA-ME.txt`. Ele não está em `files`.
5. Não editar `ReShade.ini`. O jogador escolhe o preset no overlay, ou o instalador pode só abrir a pasta. Mudar `PresetPath` automaticamente sobrescreveria a configuração de quem já usa outro preset.

## Desinstalar

1. Ler o recibo. Sem recibo, não apague às cegas.
2. Para cada arquivo, na ordem inversa de `files`:
   - se o recibo diz que houve backup, restaurar esse backup;
   - se não houve, apagar o destino.
3. Apagar o recibo e a pasta de backup da edição.
4. Deixar `dxgi.dll`, `ReShade.ini` e `CitizenFX.ini` como estavam.

## Ferramenta de referência

`tools/apply_manifest.py` implementa essa regra e inclui um teste sem FiveM:

```text
python3 tools/build_dist.py
python3 tools/apply_manifest.py self-test
```

Uso manual contra uma pasta:

```text
python3 tools/apply_manifest.py install --edition quality --plugins CAMINHO\plugins --backup CAMINHO\backup-fgm
python3 tools/apply_manifest.py uninstall --edition quality --plugins CAMINHO\plugins --backup CAMINHO\backup-fgm
```

O teste confere três coisas: arquivo novo é copiado igual à origem, arquivo que já existia volta no uninstall, e `ReShade.ini` / `dxgi.dll` não mudam.
