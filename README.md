# fivem-graphics-mod

Pacote gráfico para FiveM com visual realista e cinematográfico. O resource aplica o look em tempo real. Ele não substitui arquivos do jogo e não usa chave de servidor.

Há duas versões no mesmo resource:

| Versão | Comando | O que muda |
| --- | --- | --- |
| Quality | `/grafico quality` | Mais cor, céu, reflexo, chuva e nitidez. É o padrão. |
| Performance | `/grafico performance` | Menos bloom, sombra mais curta, menos partículas e menos gotas na tela. |

## O que o mod melhora

- Iluminação, cor e contraste, com saturação contida
- Nitidez leve e vinheta curta, sem bloom estourado
- Céu, nascer e pôr do sol
- Noite um pouco mais escura, com luz urbana e farol ainda legíveis
- Reflexos e poças na chuva
- Gotas na tela durante a chuva, fora do centro da visão
- Sangue breve na borda da tela quando o jogador toma dano

O teste dentro do FiveM fica para depois, no cliente. Este repositório não inicia servidor e não pede chave.

## Instalação rápida

1. Copie esta pasta para `resources/fivem-graphics-mod`.
2. No `server.cfg`, acima de recursos que também mexam em visual:

```
ensure fivem-graphics-mod
setr fgm_profile quality
```

3. Reinicie o resource. No jogo: `/grafico quality` ou `/grafico performance`.

Detalhes, remoção e backup: [docs/INSTALACAO.md](docs/INSTALACAO.md), [docs/DESINSTALACAO.md](docs/DESINSTALACAO.md), [docs/BACKUP.md](docs/BACKUP.md). Como cada arquivo funciona: [docs/ARQUITETURA.md](docs/ARQUITETURA.md).

ReShade é opcional e fica em `optional/reshade/`. O visual principal não depende dele.
