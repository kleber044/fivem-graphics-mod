# Testes

No repositório, com Python 3:

```text
python3 tools/build_dist.py
python3 tools/validate_dist.py
python3 tools/verify_hashes.py
python3 tools/preview_grade.py
python3 tools/preview_distance.py
python3 tools/install_test.py
python3 tools/uninstall_test.py
```

`validate_dist.py` confere manifesto schema 3, SHA-256, chuva fora de `Techniques=`, grão e aberração desligados, bloom ausente no Low, postes depois do bloom nos outros, White LED com 8 amostras no Ultra, Neutral com 4 no Low, asfalto menor no Low do que no Ultra, e ausência de resource, DLL e EXE.

`preview_grade.py` desenha cenas sintéticas e aplica a mesma conta dos shaders. Cobre dia, noite, chuva com força zero, poste, halo, rastro, luz distante, montanha, pele, roupa, camisa, nuvem, céu e vegetação. As imagens saem em `/opt/cursor/artifacts` quando o teste roda na nuvem: `comparacao-dia.png`, `comparacao-noite.png`, `comparacao-chuva.png`, `comparacao-poste.png`. A ordem das faixas de dia e noite é original, Low, Medium, High, Ultra.

`preview_distance.py` mede o Ultra na distância: montanha, mata distante, horizonte, carro em primeiro plano, céu e rua ao entardecer. Cada faixa é o original ao lado do Ultra. O teste recusa véu cinza, perda de contraste na serra e céu lavado. As cópias que entram no pacote ficam em `docs/previews`.

`install_test.py` e `uninstall_test.py` usam uma pasta falsa de FiveM e um `settings.xml` falso. Cobrem instalação, atalho Quality, troca para Low, reparo, backup do settings, restauração byte a byte, `dxgi.dll` alheio, hash adulterado e ReShade reutilizado.

## Uma rodada no FiveM

Feche o jogo, instale Ultra, entre num servidor que permita ReShade e percorra a lista abaixo antes de trocar de perfil. A ideia é uma sessão, não um teste por arquivo.

1. Ultra de dia: horizonte, montanha, mata distante, céu, vegetação, pele, roupa colorida, carro, parede branca e asfalto. A distância não pode ir para cinza. A pele não pode ir para cinza nem laranja. O céu não pode estourar branco nem ganhar véu.
2. Ultra de noite: poste branco, luz distante branca, asfalto do poste sem amarelo, neon e semáforo nas cores deles, horizonte sem leite.
3. Ultra com chuva do jogo, e só então marcar `FGM_Rain`. No menu e com céu limpo a técnica continua desmarcada e sem gotas.
4. Carro em alta velocidade: o rastro do poste não volta amarelo.
5. Estrada molhada e seca: detalhe discreto, sem textura flutuando e sem sumir.
6. Árvore e grama: verde natural, sem halo de nitidez e sem neon.
7. FPS no mesmo trajeto, anotado por alguns minutos.
8. Feche o jogo, instale Medium, repita dia, noite e o mesmo trajeto de FPS.
9. Feche o jogo, instale Low, repita. O visual continua FGM, com menos bloom e menos reflexo. Confira se o `settings.xml` baixou e se `Desinstalar.cmd` devolve o gráfico anterior.

Não há como este repositório medir o FPS dentro da cidade. A tabela de `docs/PERFORMANCE.md` é contagem de amostras, não um benchmark.
