# Desempenho

O custo abaixo é a contagem de amostras de textura por pixel com a técnica ligada, lida no shader. Não é um FPS medido dentro do FiveM. Essa medição fica para a rodada única no jogo.

| Técnica | Amostras | Faixa | Onde entra |
| --- | --- | --- | --- |
| Exposure, Shadows, Ambient, Contrast, Tonemap, Highlight, Protection, ClearView, Vignette | 1 | baixo | vários saem cedo |
| LUT | 3 | baixo | todos |
| Color, Day, Night | 5 | baixo | Day sai à noite, Night sai de dia |
| Sharp | 5 | baixo | folha, borda e pele perdem força |
| Roads | 2 | baixo | sai fora do asfalto |
| Bloom | 5, 9 ou 13 | médio | Medium, High, Ultra |
| Lamps | 12 ou 20 no pixel amarelo | médio | 4 amostras saem antes, se não houver amarelo |
| Reflections | 5 ou 9 | médio | Medium, High, Ultra, e só no asfalto |
| Rain, se ligada | cerca de 20 | médio | desligada no preset |
| Grão | 1 | baixo | desligado |
| Aberração | 3 | baixo | desligada |

Low não carrega bloom nem reflexo. A textura de asfalto do Low tem 256 px. A do Ultra tem 1024 px, cerca de 3 MB em RGB8 sem compressão de GPU. High e Medium usam 512 px. O perfil Low não recebe o PNG de 1024.

O que foi evitado de propósito:

- um passo a mais para repetir a mesma conta
- kernel grande no ClearView
- bloom em superfície clara
- nitidez em borda forte
- amostras de poste em pixel que não é amarelo
- carregar a textura grande num perfil leve

Ligar grão, aberração e chuva ao mesmo tempo custa o que a tabela soma. O padrão não liga nenhum dos três.
