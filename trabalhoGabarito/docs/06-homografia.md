# 6. Homografia: endireitando a folha

## Teoria

### 6.1 O problema da perspectiva

Quando fotografamos uma folha "de lado", ela não aparece como um retângulo: vira um **quadrilátero qualquer**. O lado
mais distante da câmera fica menor, e linhas paralelas deixam de parecer paralelas. Girar e redimensionar não basta
para desfazer isso.

### 6.2 A família das transformações geométricas

Cada tipo de transformação consegue "desfazer" certos efeitos. Os **graus de liberdade** são quantos números
precisamos para descrevê-la:

| Transformação | O que faz | Graus de liberdade | Preserva |
|---|---|---|---|
| Translação | Desloca | 2 | Tudo, menos a posição |
| Rígida (Euclidiana) | Desloca + gira | 3 | Distâncias e ângulos |
| Similaridade | + muda escala | 4 | Ângulos e proporções |
| Afim | + estica e cisalha | 6 | **Retas paralelas continuam paralelas** |
| **Projetiva (homografia)** | + **perspectiva** | **8** | Só retas continuam retas |

A foto de uma folha em perspectiva só é corrigida pela **homografia**, a mais geral das transformações que levam
retas em retas.

> Ideia-chave: **a folha é um plano**. Toda foto de um plano, de qualquer ângulo, se relaciona com a folha "vista de
> frente" por **uma única homografia**. Isso vale para o plano inteiro, não só para os cantos.

### 6.3 A matemática (sem medo)

A homografia é uma **matriz 3 × 3**:

```
      ┌ h11  h12  h13 ┐
  H = │ h21  h22  h23 │
      └ h31  h32   1  ┘
```

Para levar um ponto `(x, y)` da foto para `(x', y')` na folha:

```
 ┌ u ┐     ┌ x ┐
 │ v │ = H │ y │        e depois       x' = u / w      y' = v / w
 └ w ┘     └ 1 ┘
```

Esse "1" extra e a divisão por `w` são as **coordenadas homogêneas**. A divisão por `w` é o que cria o efeito de
perspectiva: pontos "mais longe" são divididos por um número maior e ficam mais próximos entre si.

- `h13` e `h23`: **translação**.
- `h11, h12, h21, h22`: **rotação, escala, cisalhamento** (a parte afim).
- `h31` e `h32`: **perspectiva**. Se forem 0, então `w = 1` e a transformação é só afim.

### 6.4 Quantos pontos são necessários?

A matriz tem **8 incógnitas** (o último elemento é fixado em 1). Cada par de pontos correspondentes
`(x, y) → (x', y')` dá **2 equações** (uma para x', outra para y'). Logo, **4 pontos dão 8 equações** e determinam a
homografia exatamente.

É por isso que usamos **4 marcadores**: 3 cantos não bastariam para a perspectiva.
`cv2.getPerspectiveTransform` monta e resolve esse sistema linear 8 × 8.

### 6.5 Aplicando na imagem: mapeamento inverso e interpolação

Um jeito ingênuo de endireitar seria percorrer cada pixel da foto e "jogá-lo" na folha. Isso deixa **buracos**, porque
nem todo pixel de destino recebe alguém. O `cv2.warpPerspective` faz o contrário (**mapeamento inverso**):

> Para **cada pixel da folha de destino**, calcula de **onde ele vem** na foto (usando `H⁻¹`) e busca a cor lá.

O ponto de origem quase nunca cai exatamente num pixel inteiro, por exemplo `(812,25; 403,5)`. É preciso
**interpolar**:

| Método | Como funciona | Resultado |
|---|---|---|
| Vizinho mais próximo | Pega o pixel mais perto | Rápido, mas serrilhado |
| **Bilinear** | Média ponderada dos 4 vizinhos | Suave, o padrão para rotações |
| Área (`INTER_AREA`) | Média de todos os pixels que "caem" dentro do pixel de destino | O melhor para **reduzir** imagens |

**Exemplo de interpolação bilinear.** Os 4 vizinhos valem:

```
 (0,0) = 100    (1,0) = 200
 (0,1) =  50    (1,1) = 150
```

Queremos o valor em `(0,25; 0,5)`:
1. Na horizontal, linha de cima: `100 + 0,25 · (200 − 100) = 125`
2. Na horizontal, linha de baixo: `50 + 0,25 · (150 − 50) = 75`
3. Na vertical, entre as duas: `125 + 0,5 · (75 − 125) = 100`

## Como aplicamos

### 6.6 O código

```python
origem  = np.float32([encontrados[i] for i in range(4)])                 # cantos na foto
destino = np.float32([layout.CANTOS_EXTERNOS[i] for i in range(4)]) * SUPERAMOSTRAGEM  # cantos na folha padrão
homografia = cv2.getPerspectiveTransform(origem, destino)
grande = cv2.warpPerspective(imagem_bgr, homografia,
                             (layout.LARGURA * 2, layout.ALTURA * 2),
                             flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
return cv2.resize(grande, (layout.LARGURA, layout.ALTURA), interpolation=cv2.INTER_AREA)
```

Os cantos de destino são **as posições dos marcadores no layout**: `(50, 50)`, `(1190, 50)`, `(1190, 1704)` e
`(50, 1704)`. Assim, depois da transformação, **todo o resto da folha cai exatamente nas coordenadas do `layout.py`**.

### 6.7 Um exemplo com números reais

Na foto de exemplo (`img/02_foto.jpg`, 2716 × 2716 px) os cantos externos foram encontrados em:

| Marcador | Na foto (x, y) | Na folha padrão |
|---|---|---|
| ID 0 | (583, 654) | (50, 50) |
| ID 1 | (1811, 292) | (1190, 50) |
| ID 2 | (2136, 2180) | (1190, 1704) |
| ID 3 | (867, 2445) | (50, 1704) |

A homografia calculada foi:

```
      ┌  0,9685   −0,1530   −413,02 ┐
  H = │  0,2755    0,9264   −714,97 │
      └  4,9·10⁻⁵  3,1·10⁻⁶   1     ┘
```

Leitura da matriz: o bloco `0,9685 / 0,2755 / −0,153 / 0,9264` é quase uma rotação. A primeira coluna aponta ~16°
e a segunda ~9°; se fosse rotação pura os dois ângulos seriam iguais, e a diferença vem da perspectiva e do
cisalhamento (a foto foi girada 12° **e** inclinada). `−413` e `−715` deslocam a folha para a origem; `h31 = 0,000049`
é pequeno, mas não zero, e é a perspectiva. Conferindo o canto ID 2:

```
 u = 0,9685·2136 − 0,1530·2180 − 413,02 ≈ 1322,2
 v = 0,2755·2136 + 0,9264·2180 − 714,97 ≈ 1893,1
 w = 0,0000488·2136 + 0,0000031·2180 + 1 ≈ 1,111
 x' = u / w ≈ 1190,1     y' = v / w ≈ 1703,9   ✓  (esperado: 1190, 1704)
```

O `w = 1,111` (e não 1) mostra a divisão de perspectiva agindo: esse canto estava "mais longe" na foto simulada.

![Folha alinhada](img/04_folha_alinhada.png)

### 6.8 Por que gerar o dobro e depois reduzir?

O `warpPerspective` **não aceita** `INTER_AREA`. Quando a folha na foto é **maior** que a folha padrão (o caso normal
em fotos de celular), a transformação está **reduzindo** a imagem, e a interpolação bilinear pura pode "pular" linhas
finas (o traço da borda de um quadrado tem só 3 px). A solução:

1. `warpPerspective` para **2× o tamanho** (2480 × 3508), com bilinear;
2. `resize` para 1240 × 1754 com `INTER_AREA`, que faz a média de cada bloco 2 × 2.

Isso se chama **superamostragem**.

### 6.9 `BORDER_REPLICATE`

Se algum pixel de destino "vier de fora" da foto, ele recebe a cor da borda mais próxima em vez de preto. Isso evita
faixas pretas artificiais, que seriam confundidas com tinta.

### 6.10 O que a homografia **não** corrige

- **Papel dobrado ou curvado**: deixa de ser um plano, e uma única homografia não descreve a foto. Pequenas curvaturas
  são absorvidas pelo refinamento local (capítulo 8); dobras fortes, não.
- **Distorção de lente** (efeito "olho de peixe"): celulares modernos já corrigem quase toda.
