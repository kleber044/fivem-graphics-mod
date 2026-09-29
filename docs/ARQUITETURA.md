# Arquitetura

Um único resource entrega as duas versões. Quality é o padrão. Performance reduz bloom, distância de sombra, partículas de chuva, reflexo e quantidade de gotas na tela.

O resource não abre servidor, não fala com o portal Cfx.re e não lê chave nenhuma.

## Mapa dos arquivos

| Arquivo | Função |
| --- | --- |
| `fxmanifest.lua` | Declara scripts, NUI e os XML de timecycle. |
| `shared/config.lua` | Limiar de chuva, força do timecycle e custo de cada versão (sombra, luz, gotas). |
| `shared/profiles.lua` | Traduz hora do relógio em dia, golden hour ou noite, e escolhe o modifier. |
| `shared/timecycle.lua` | Valores de cor, céu, bloom, sombra e reflexo. Fonte do XML. |
| `shared/visual_settings.lua` | Farol, corona, bloom, poça, luz distante e chuva, mais a tabela `restore`. |
| `timecycle/quality.xml` | Modifiers `fgm_quality_day`, `fgm_quality_golden`, `fgm_quality_night`, `fgm_quality_rain`. |
| `timecycle/performance.xml` | Os quatro equivalents `fgm_perf_*`. |
| `client/main.lua` | Comando `/grafico`, relógio, clima e interior. |
| `client/visuals.lua` | Aplica e limpa timecycle, visual settings e trilha de chuva. |
| `client/screen.lua` | Avisa a NUI sobre chuva, dano e vida baixa. |
| `server/main.lua` | Só registra a subida do resource e o convar padrão. |
| `nui/` | Gotas e sangue. Não captura mouse nem teclado. |
| `optional/reshade/` | Presets opcionais. O resource funciona sem eles. |
| `backup/visualsettings-restauracao.txt` | Cópia legível dos valores de restauração. |
| `tools/sync_timecycle_xml.py` | Regenera o XML a partir do Lua. |
| `tools/test_profiles.lua` | Testa horário, nomes e a diferença Quality vs Performance. Roda fora do jogo. |

## Como o visual é escolhido

A cada ciclo o cliente lê a hora e o clima.

- 5h–8h e 17h–20h usam o modifier golden (nascer e pôr do sol).
- 20h–5h usa a noite, mais escura, com ambiente artificial um pouco mais alto para poste e janela.
- O resto do dia usa o modifier de dia.
- `RAIN`, `THUNDER`, `CLEARING` ou `GetRainLevel` acima de `0.15` ligam o modifier extra de chuva, as poças e as gotas.
- Interior reduz a força do timecycle e esconde as gotas.
- Dentro de veículo as gotas diminuem, como para-brisa, e não cobrem o meio da tela.

Quality mantém bloom baixo de propósito (`postfx_intensity_bloom` 0.18 de dia, limiar de brilho alto). Performance fica abaixo disso e encurta `dir_shadow_distance_multiplier`.

## Efeitos de tela

A NUI é um HTML transparente.

- Chuva: riscos e gotas paradas nas bordas. Uma máscara radial deixa o centro limpo. Quality usa 22 riscos; Performance usa 9.
- Sangue: só depois de um dano de pelo menos 3 pontos de vida ou de colete. As manchas nascem nas bordas, somem em cerca de 2,3 segundos e não passam de um punhado ao mesmo tempo.
- Vida baixa: vinheta vermelha fraca, no máximo 0,55 de opacidade, só quando a vida útil cai de 45%.

## ReShade

`optional/reshade/Quality.ini` pede nitidez leve, bloom baixo e vinheta curta. `Performance.ini` deixa só um pouco de nitidez, para custar um passe a menos. Nenhum dos dois aumenta saturação de propósito. Os shaders vêm da instalação oficial do ReShade; este repositório não inclui o programa.

## O que só o cliente FiveM confirma

Sintaxe, XML e a prévia das gotas podem ser checados fora do jogo. O encaixe com o timecycle do GTA, o farol e a chuva do mundo pedem um teste manual no cliente, com `/grafico quality` e `/grafico performance`.
