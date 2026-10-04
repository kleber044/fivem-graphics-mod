# Asfalto

O FGM não troca o material de rua do GTA. Isso exigiria editar `update.rpf` ou publicar um resource no servidor. Os dois ficam de fora deste produto.

O que existe é um detalhe original, gerado por `src/roads/gerar_asfalto.py` na hora do build. Não há textura copiada de outro mod nem arquivo da Rockstar.

## Arquivos

| Perfil | Tamanho | Força no shader | Pasta |
| --- | --- | --- | --- |
| Ultra | 1024 | 0,12 | `dist/ultra/roads/` e a cópia em `Textures/FGM/` |
| High | 512 | 0,10 | `dist/high/roads/` |
| Medium | 512 | 0,07 | `dist/medium/roads/` |
| Low | 256 | 0,04 | `dist/low/roads/` |

A cópia que o ReShade lê é `reshade-shaders/Textures/FGM/fgm_road.png`. A pasta `roads/` fica no pacote para inspeção e não é instalada em `plugins`, para não duplicar o arquivo no FiveM.

A imagem é cinza, com média perto de 0,5, agregado fino, sujeira baixa e fissura curta. O shader só multiplica isso onde o pixel já é asfalto: pouca saturação, luminância de chão, sem pele, sem planta, sem céu e sem poste. Fora dessa máscara o passo sai na hora.

## Limite

O detalhe é em espaço de tela. Ele não acompanha o UV do mundo, então não substitui uma faixa pintada no asfalto do jogo e não deve ser forte o bastante para parecer uma textura flutuando. Por isso a força fica entre 0,04 e 0,12.

Não há pop-in de textura de mundo, porque o YTD do jogo não muda. O custo de VRAM é uma textura por perfil, do tamanho da tabela.
