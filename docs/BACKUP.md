# Backup

Este pacote não substitui arquivos originais do GTA V nem do FiveM. O visual entra e sai pela sessão do resource.

## O que fica guardado no projeto

`backup/visualsettings-restauracao.txt` lista cada chave que o resource altera com `SetVisualSettingFloat`, com o valor aplicado quando o resource para ou quando o jogador usa `/grafico desligar`.

A mesma tabela está em `shared/visual_settings.lua`, no campo `restore`. Os perfis Quality e Performance só escrevem chaves que existem nessa lista, para a parada conseguir reverter o que o resource ligou.

`SetVisualSettingFloat` não grava disco. Fechar o FiveM faz o cliente ler de novo o `visualsettings.dat` da instalação do jogo. Essa é a restauração completa.

## Antes de instalar em um servidor que já tem outro visual

Guarde a pasta de resources e o `server.cfg` atual:

```bash
tar -czf backup-resources.tgz resources server.cfg
```

Se outro resource já substitui `visualsettings.dat` ou timecycle com o mesmo nome de modifier, anote a ordem dos `ensure`. Este pacote usa modifiers próprios (`fgm_quality_*` e `fgm_perf_*`) e não reaproveita o nome dos XML originais do jogo (`w_clear.xml`, `w_rain.xml` e os demais).

## Se você já tinha trocado arquivos do jogo manualmente

Isso fica fora deste resource. Para voltar ao original do GTA:

1. Feche o FiveM e o jogo.
2. Na Steam ou no Rockstar Launcher, use a verificação de integridade dos arquivos do GTA V.
3. Apague presets ReShade antigos se eles ainda estiverem selecionados.
4. Só então instale este resource.

Não copie um `visualsettings.dat` de pacote de terceiros para dentro desta pasta. O projeto não distribui esse arquivo.

## Timecycle

Os XML em `timecycle/` são modifiers novos, gerados de `shared/timecycle.lua`. Eles não são cópia dos XML do jogo. Apagar o resource tira esses modifiers do cliente no próximo carregamento.
