# Instalação

O pacote é um resource normal do FiveM. Não há arquivo do GTA para substituir e não há chave para colar.

## 1. Colocar o resource

Copie a pasta do projeto para o servidor, com este nome:

```
resources/fivem-graphics-mod
```

A pasta precisa conter `fxmanifest.lua` na raiz.

## 2. Ligar no server.cfg

```
ensure fivem-graphics-mod
setr fgm_profile quality
```

`fgm_profile` aceita `quality` ou `performance`. Esse valor é só o padrão para quem ainda não escolheu um perfil. A escolha do jogador fica salva no cliente e tem prioridade.

Coloque este `ensure` depois de `spawnmanager` e antes de outro resource que também altere timecycle ou `visualsettings`.

## 3. Subir

No console do servidor:

```
ensure fivem-graphics-mod
```

Ou reinicie o servidor. Cada jogador recebe o resource no próximo connect. Quem já está online pode usar `restart fivem-graphics-mod`.

## 4. Escolher a versão no jogo

| Comando | Efeito |
| --- | --- |
| `/grafico quality` | Versão principal, melhor qualidade visual |
| `/grafico performance` | Versão leve, menos efeito e menos custo |
| `/grafico desligar` | Tira o pacote e aplica a restauração de sessão |
| `/grafico status` | Mostra perfil, período do dia e se a chuva está ativa |

Atalhos aceitos: `qualidade`, `cinematico`, `perf`, `fps`, `leve`, `off`.

## 5. ReShade (opcional)

O resource já faz o visual sozinho. ReShade é um extra no cliente, fora do servidor.

1. Instale o ReShade oficial no executável do FiveM, com o pacote de shaders padrão.
2. Copie `optional/reshade/Quality.ini` ou `optional/reshade/Performance.ini` para a pasta do ReShade.
3. Selecione o preset no menu do ReShade (Home).
4. Use o preset Quality junto com `/grafico quality`, e o Performance junto com `/grafico performance`.

Se algum shader não existir na sua instalação, desligue essa técnica no menu. O resource do servidor continua funcionando.

## Conferência manual no cliente

Entre no servidor e observe:

- Dia claro, por volta das 12h: contraste presente, céu sem saturação forte, bloom contido
- 6h e 18h: calor de nascer e pôr do sol
- 23h: noite mais escura, poste e farol ainda visíveis
- Clima `RAIN` ou `THUNDER`: poça, reflexo e gotas na borda da tela; o centro continua livre
- Dentro de interior: o grau baixa e as gotas somem
- Dano: manchas nas bordas que somem em cerca de 2 segundos

Para comparar as versões, alterne `/grafico quality` e `/grafico performance` no mesmo horário e clima.
