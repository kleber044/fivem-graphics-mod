# Instalação

Este pacote é instalado no **Windows do jogador**. Não entre na pasta `resources` do servidor e não edite `server.cfg`.

Instale só uma edição por vez. Quality e Performance usam os mesmos nomes de shader; a segunda cópia substitui a primeira.

## 1. Requisitos

- GTA V atualizado e FiveM instalado pelo cliente oficial.
- Windows com o jogo em DirectX 11 (o padrão do FiveM).
- Servidor que não bloqueie ReShade. Se o anticheat da cidade fechar o jogo ao detectar `dxgi.dll`, o mod não tem como contornar isso.

## 2. Instalar o ReShade

O binário do ReShade **não vem neste pacote**. Baixe o instalador sem suporte a add-ons em [https://reshade.me/](https://reshade.me/).

1. Aponte o instalador para `GTA5.exe` na pasta do GTA V.
2. Escolha DirectX 10/11/12.
3. Não marque pacotes de shaders de terceiros. Este produto traz os shaders dele.
4. **Recorte** (não deixe cópia) estes arquivos da pasta do GTA V para a pasta `plugins` do FiveM:
   - `dxgi.dll`
   - `ReShade.ini`
5. Se o instalador também criou `reshade-shaders` no GTA V, recorte essa pasta para o mesmo `plugins`. Os shaders FGM entram dentro dela no passo seguinte.

A pasta `plugins` fica em:

```text
%LOCALAPPDATA%\FiveM\FiveM.app\plugins
```

No Explorer essa pasta `FiveM.app` aparece com o nome **FiveM Application Data**. O caminho real continua `FiveM.app`.

Confirme que `dxgi.dll` não ficou na pasta do GTA V, para o modo história não abrir com ReShade.

## 3. Copiar a edição

Escolha `dist/quality` ou `dist/performance`. Cada arquivo listado em `manifest.json` vai para o `destination` correspondente. A pasta de destino de cada um está em `destination_dir`.

Na prática, com a edição Quality, o resultado dentro de `plugins` é:

```text
plugins\
  dxgi.dll                         (ReShade, já instalado; não substituir)
  ReShade.ini                      (ReShade, já instalado; não substituir)
  FGM-Quality.ini
  reshade-shaders\
    Shaders\FGM\                   (FGM.fxh e os .fx desta edição)
    Textures\FGM\fgm_quality_lut.png
```

A edição Performance usa `FGM-Performance.ini` e `fgm_performance_lut.png`, e não inclui `FGM_Bloom.fx`.

`LEIA-ME.txt` fica só na pasta da edição. Não precisa ir para `plugins`.

Se já existir um arquivo nosso de uma instalação anterior, faça backup antes de substituir. Veja `BACKUP.md`.

## 4. Aviso do CitizenFX.ini

Em algumas versões o FiveM escreve no F8 um aviso do ReShade 5 e pede uma linha em `CitizenFX.ini`, na pasta `FiveM.app` (não dentro de `plugins`).

Se isso aparecer:

1. Copie `CitizenFX.ini` para outro lugar antes de editar.
2. Cole **somente** a linha que o próprio console F8 mostrar.
3. Não apague o resto do arquivo e não invente um ID. O identificador é desta instalação.

Este pacote não altera `CitizenFX.ini`.

## 5. Ligar o preset

1. Abra o FiveM e entre num servidor compatível.
2. Pressione Home para abrir o ReShade.
3. Na barra de preset, use o botão de pasta e selecione `FGM-Quality.ini` ou `FGM-Performance.ini` dentro de `plugins`.
4. As técnicas FGM devem aparecer ativas, nesta ordem: LUT, bloom (só Quality), nitidez, vinheta, chuva.

Se o ReShade não abrir, o F8 costuma dizer se `dxgi.dll` foi ignorado. O fórum da Cfx já registrou dois contornos usados por jogadores, sem trocar arquivo do jogo: renomear `dxgi.dll` para `d3d11.dll` na pasta `plugins`, ou adicionar a linha de reconhecimento que o próprio F8 imprime. Faça um de cada vez e mantenha o backup.

## 6. O que conferir no jogo

- A imagem fica um pouco mais contrastada, com sombra mais fria e luz mais quente.
- Faróis e postes ganham um halo curto na edição Quality. Na Performance esse halo não existe.
- Bordas da tela escurecem de leve. O centro continua livre.
- Em cena escura e pouco colorida, gotas aparecem nas bordas. No sol elas somem. Túnel e interior escuro também podem mostrar gota; desligue a técnica `FGM_Rain` no ReShade se incomodar.
- Não espere céu, poça ou fachada diferentes dos que o servidor já desenha. Isso está fora do pós-processamento.
