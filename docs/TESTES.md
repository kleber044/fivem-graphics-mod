# Testes

No repositório, com Python 3:

```text
python3 tools/build_dist.py
python3 tools/validate_dist.py
python3 tools/verify_hashes.py
python3 tools/preview_grade.py
python3 tools/install_test.py
python3 tools/uninstall_test.py
```

`validate_dist.py` confere manifesto, SHA-256, LUT PNG, shaders, ausência de bloom na Performance, `FGM_Lamps` depois do bloom na Quality, White LED com 8 amostras na Quality e Neutral com 4 na Performance, `FGM_ClearView` no nível 3 e 2, vivacidade 0,14 e 0,08, calma do dia 0,22 e 0,14, bloom da Quality em limiar 0,93 e quantidade 0,05, `FGM_Rain` fora de `Techniques=` e presente só em `TechniqueSorting=`, e ausência de `fxmanifest.lua`, `server.cfg`, `client/`, `server/`, DLL e EXE dentro de `dist/` e `release/`. A prévia também confere que a nitidez 0,14 permanece a conta antiga, que o pico de luz no chão e na folha não passa disso na Quality, e que o bloom 0,05 não altera asfalto escuro, folha nem reflexo já estourado.

`install_test.py` e `uninstall_test.py` usam uma pasta falsa de FiveM. Cobrem instalação, segunda instalação, Quality para Performance e o inverso, reparo, `dxgi.dll` de outro programa, FiveM ausente, pasta sem marcador, hash adulterado, ReShade compatível reutilizado, `d3d11.dll` já existente, ReShade antigo substituído, arquivo protegido, extração do setup oficial e restauração byte a byte.

O teste dentro do FiveM, com o jogo aberto num servidor, fica no Windows de quem for validar o visual. Estes testes não substituem isso.

As prévias sintéticas saem em imagens `preview-quality-*` e `preview-performance-*`: dia, noite e chuva. À esquerda está o quadro original. À direita entram a grade, a devolução de pele e roupa, a limpeza do horizonte e os postes. A noite tem núcleo de sódio, halo, reflexo no asfalto, luz distante, rastro, cauda de rastro, parede, fachada, rua, leite cinza, janela, farol, neon, semáforo e luz azul. White LED deixa o núcleo em branco neutro, `(0,71, 0,71, 0,71)`, com a mesma luminância. Halo, asfalto, luz distante e rastros também perdem o amarelo. Neutral fica quase no mesmo ponto. Parede, fachada, rua, janela, farol branco, neon e semáforo conservam a cor. O leite cinza desce de cerca de 0,29 para 0,22 na Quality e para 0,25 na Performance, sem mexer na sombra. O dia tem sol, camisa branca, nuvem, calçada clara, céu azul, vegetação, carro, placa, pele, calça e casaco. Pele, calça e casaco ficam na cor do quadro original. A camisa e a nuvem descem um pouco sem virar cinza e sem grudar em 255. O céu azul perde saturação e termina perto de 0,43. A vegetação do dia desce de cerca de 0,36 para 0,25, e continua verde. A névoa do prédio recua de 0,56 para 0,38. O FPS dentro do FiveM não é medido aqui.

O arquivo de chuva compara a lente limpa, com `FGM_Rain` desligado, e a mesma cena depois que a técnica é marcada. Não é uma captura do GTA e não simula detecção de clima: dia e noite recebem a mesma máscara de gota, força zero não pinta pixel, e a força maior cobre mais pixels do que a menor.
