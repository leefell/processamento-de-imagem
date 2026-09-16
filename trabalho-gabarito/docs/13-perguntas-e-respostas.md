# 13. Perguntas e respostas

Perguntas que o professor ou a turma podem fazer, com respostas curtas e o capítulo onde está a explicação completa.

## Sobre a abordagem

**Por que vocês não usaram a folha do professor?**
O layout era livre. Nossa folha tem **marcadores ArUco** nos cantos, que permitem achar e endireitar a folha em
qualquer foto. A folha original não tem nenhuma referência desse tipo, e localizar a grade nela seria bem menos
confiável. → [Cap. 4](04-a-folha.md), [5](05-marcadores-aruco.md)

**Por que ArUco e não 4 quadrados pretos?**
Quadrados pretos são todos iguais: não dizem **qual** canto é qual. Com a folha girada 180° o programa se confundiria.
Cada ArUco tem um **ID** e uma orientação própria. → [Cap. 5.6](05-marcadores-aruco.md)

**Por que homografia e não só girar a imagem?**
Rotação não desfaz **perspectiva** (celular inclinado). A homografia corrige rotação, escala, deslocamento **e**
perspectiva de uma vez, e é a transformação certa para a foto de um plano. → [Cap. 6](06-homografia.md)

**Por que exatamente 4 marcadores?**
A homografia tem 8 incógnitas; cada ponto dá 2 equações; 4 pontos dão 8 equações. → [Cap. 6.4](06-homografia.md)

**E se a folha estiver de cabeça para baixo?**
Funciona. O ID de cada marcador diz qual canto da folha ele é, independentemente de como aparece na foto.
→ [Cap. 5.4](05-marcadores-aruco.md)

## Sobre a leitura

**Como o programa sabe se um quadrado está pintado?**
Mede a **fração de pixels de tinta** na parte interna do quadrado: até 15% é vazio, a partir de 50% é marcado, e o
que fica entre os dois é dúvida. → [Cap. 8](08-leitura-das-marcacoes.md)

**Por que medir só a parte de dentro do quadrado?**
Porque a **borda impressa** também é preta. Medindo o quadrado inteiro, todo quadrado vazio pareceria parcialmente
pintado; o experimento `sem_margem_interna` quebra 20 testes. → [Cap. 8.5](08-leitura-das-marcacoes.md)

**Por que não usar só a imagem em tons de cinza?**
Na conversão comum o azul pesa pouco, e caneta azul clara vira cinza médio. Usamos o **menor canal (R, G ou B)**:
papel é claro em todos, tinta é escura em pelo menos um. → [Cap. 7.1](07-segmentacao-da-tinta.md)

**O que é o método de Otsu?**
Um jeito automático de escolher o limiar entre escuro e claro: testa todos os cortes e fica com o que **maximiza a
variância entre as duas classes**. → [Cap. 7.5](07-segmentacao-da-tinta.md)

**Como vocês tratam sombra?**
Estimamos como seria o papel sem tinta (dilatação com janela maior que qualquer mancha de tinta + desfoque) e
**dividimos** a imagem por essa estimativa. A sombra multiplica tudo por um fator, e a divisão cancela esse fator.
→ [Cap. 7.3](07-segmentacao-da-tinta.md)

**E se os quadrados forem impressos com tamanhos diferentes?**
Dois mecanismos: o **refinamento local** procura o quadrado real perto da posição esperada, e a **região interna**
medida é pequena o bastante para ficar dentro de quadrados entre 85% e 115% do tamanho. Há testes para os dois.
→ [Cap. 8.4 e 8.5](08-leitura-das-marcacoes.md)

**O que acontece se o aluno marcar duas alternativas?**
A questão é **anulada** e vale 0; o app mostra "Anulada: marcou mais de uma". → [Cap. 8.7](08-leitura-das-marcacoes.md)

**E se ele fizer um X em vez de pintar?**
Um X ocupa ~24% do miolo, cai na faixa de dúvida e a questão é anulada por "marcação incompleta". Um X muito fino pode
ficar abaixo de 15% e ser lido como em branco, uma limitação conhecida. → [Cap. 8.6 e 8.8](08-leitura-das-marcacoes.md)

**E se ele marcar A e fizer um rabisco leve em C?**
O rabisco, se passar de 15%, é "dúvida", e a questão é anulada. Foi uma decisão do grupo: não dá para saber se o
rabisco era uma segunda resposta. → [Cap. 8.7](08-leitura-das-marcacoes.md)

**Precisa fotografar a folha-mestre para informar o gabarito oficial?**
Não. A forma padrão no app é selecionar a alternativa de cada questão direto na tela (sem foto, sem risco de erro de
leitura); foto/PDF e arquivo JSON continuam disponíveis como alternativas. → [Cap. 10.1](10-correcao-e-interface.md)

**Por que 15% e 50%?**
15% fica bem acima de um quadrado vazio (0%) e abaixo de um X normal; 50% exige um preenchimento de verdade com
margem para imperfeições. São constantes fáceis de ajustar depois dos testes com fotos reais.
→ [Cap. 8.6](08-leitura-das-marcacoes.md)

**Dá para mudar esses 50% sem mexer no código?**
Sim: o expander "Ajustes avançados" do app tem um slider que ajusta o `limite_marcado` na hora, para o gabarito
oficial e para a folha do aluno. Serve para folhas com marcação mais fraca (ex.: X em vez do quadrado todo pintado).
→ [Cap. 8.6](08-leitura-das-marcacoes.md)

## Sobre o OCR

**Como o programa lê o nome?**
Recorta a caixa do Nome da folha já alinhada e passa para o **EasyOCR**, que usa duas redes neurais: uma acha onde há
texto (CRAFT) e outra reconhece os caracteres (CNN + LSTM + CTC). → [Cap. 9](09-ocr.md)

**Funciona com letra cursiva?**
Esperamos que **não muito bem**: o modelo foi treinado principalmente com texto impresso, e em cursiva as letras são
emendadas. É uma limitação que assumimos e medimos com fotos reais. → [Cap. 9.4](09-ocr.md), [resultados](resultados.md)

**Por que não usaram uma IA mais forte para ler a cursiva?**
Foi considerado (a IA recomendou), mas o grupo escolheu uma solução **local, gratuita e sem internet**. O preço é a
cursiva mais fraca, e isso fica explícito na apresentação. → [Cap. 12.2](12-uso-de-ia.md)

**O que acontece se o OCR falhar?**
A nota sai normalmente; só a identificação fica como "Não lido" ou aparece um aviso. → [Cap. 2.4](02-visao-geral.md)

## Sobre o software

**Por que Python e não MATLAB, como nas aulas?**
O professor liberou a escolha. Python + OpenCV tem muito material sobre OMR, bibliotecas gratuitas de OCR para texto
manuscrito e roda sem licença. As operações são as mesmas vistas em aula (limiarização, morfologia, filtros,
transformações). → [Cap. 12.5](12-uso-de-ia.md)

**Como vocês sabem que funciona?**
88 testes automáticos, incluindo 10 cenários de foto simulada (girada, com sombra, desfocada, de cabeça para baixo…),
PDF e impressão com quadrados de tamanhos diferentes, além de testes manuais no navegador. **Com fotos reais**, o
resultado está em [resultados.md](resultados.md). → [Cap. 11](11-testes.md)

**Aceita PDF?**
Sim. A primeira página é convertida em imagem a 200 DPI e segue o mesmo caminho de uma foto. → [Cap. 3](03-imagem-digital.md)

**Quanto tempo leva para corrigir uma folha?**
1–3 segundos. A primeira correção depois de abrir o app leva ~20–30 s, porque o modelo do OCR é carregado na memória.
→ [Cap. 1.3](01-como-executar.md)

**O que a IA fez e o que vocês fizeram?**
A IA entrevistou o grupo, escreveu o spec, o código, os testes e esta documentação. O grupo tomou as decisões de
projeto (várias diferentes da recomendação da IA), testou com folhas reais e é responsável por entender e apresentar.
→ [Cap. 12](12-uso-de-ia.md)
