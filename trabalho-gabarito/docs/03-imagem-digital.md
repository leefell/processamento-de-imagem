# 3. Imagem digital

Antes de qualquer técnica, é preciso entender **o que o computador recebe** quando abrimos uma foto.

## Teoria

### 3.1 Uma imagem é uma matriz de números

Uma imagem digital é uma **grade de pixels**. Em uma imagem em **tons de cinza**, cada pixel guarda **um número**
que diz o quão claro ele é. No formato mais comum (8 bits, `uint8`), esse número vai de **0 (preto)** a
**255 (branco)**.

Um pedaço de 5 × 5 pixels de uma folha com um traço de caneta poderia ser:

```
      x=0  x=1  x=2  x=3  x=4
y=0 [ 238  240  236  239  241 ]    ← papel (claro)
y=1 [ 237   62   58  235  240 ]
y=2 [ 239   55   40   61  238 ]    ← tinta (escuro)
y=3 [ 240  236   64   57  237 ]
y=4 [ 241  239  238  240  236 ]
```

Tudo o que o software faz são **contas com essas matrizes**: comparar valores, somar, multiplicar, procurar padrões.

### 3.2 Coordenadas

- A origem `(0, 0)` fica no **canto superior esquerdo**.
- **x** cresce para a **direita** (colunas); **y** cresce para **baixo** (linhas).
- Em Python/NumPy o acesso é `imagem[y, x]`, **linha primeiro**. É uma fonte clássica de confusão: o *tamanho* é
  descrito como "largura × altura", mas o `shape` da matriz vem como `(altura, largura)`.

> No MATLAB das aulas é igual (`img(linha, coluna)`), só que os índices começam em **1** em vez de 0.

### 3.3 Imagens coloridas: canais

Uma imagem colorida tem **3 matrizes empilhadas**, uma por **canal**: vermelho (R), verde (G) e azul (B). Cada pixel
vira um trio de números. Exemplos:

| Cor | R | G | B |
|---|---|---|---|
| Branco do papel | 235 | 235 | 235 |
| Preto da caneta | 25 | 25 | 30 |
| Azul da caneta | 30 | 60 | 160 |
| Vermelho | 200 | 30 | 40 |

O `shape` de uma foto colorida é `(altura, largura, 3)`.

> ⚠️ **O OpenCV guarda as cores na ordem B, G, R**, e não R, G, B. É uma herança histórica da biblioteca. Por isso o
> código tem conversões como `cv2.cvtColor(img, cv2.COLOR_RGB2BGR)` sempre que passa uma imagem do Pillow (RGB) para o
> OpenCV (BGR).

### 3.4 De colorido para cinza

A conversão mais comum usa uma **média ponderada**, porque o olho humano é mais sensível ao verde:

```
cinza = 0,299·R + 0,587·G + 0,114·B
```

É o que o `rgb2gray` do MATLAB e o `cv2.COLOR_BGR2GRAY` fazem. No [capítulo 7](07-segmentacao-da-tinta.md) veremos
que, **para achar tinta**, usamos outra ideia: o **menor** dos três canais.

### 3.5 Resolução e DPI

**DPI** (*dots per inch*, pontos por polegada) liga pixels a tamanho físico. Uma polegada tem 25,4 mm.

A folha **A4** mede 210 × 297 mm, ou seja, 8,27 × 11,69 polegadas:

| DPI | Tamanho da A4 em pixels | Onde usamos |
|---|---|---|
| 150 | **1240 × 1754** | "Folha padrão": onde toda a leitura acontece |
| 200 | 1654 × 2339 | Conversão de PDF para imagem |
| 300 | 2480 × 3508 | Folha gerada para impressão |

Com isso dá para converter qualquer medida. Um quadradinho de resposta tem 72 px na folha padrão:
72 ÷ 150 = 0,48 polegada ≈ **12,2 mm** no papel.

### 3.6 Formatos de arquivo

| Formato | Característica | Impacto para nós |
|---|---|---|
| **JPG** | Compressão **com perda**: descarta detalhes e cria pequenos "ruídos" nas bordas | Foto de celular vem assim; o algoritmo precisa tolerar ruído |
| **PNG** | Compressão **sem perda** | Prints e imagens geradas |
| **HEIC** | Formato padrão do iPhone | Aberto com `pillow-heif` |
| **PDF** | Documento com páginas, não uma imagem | Precisa ser **renderizado** (desenhado em pixels) antes |

### 3.7 Orientação EXIF

O celular nem sempre "gira" os pixels quando você tira a foto deitado. Muitas vezes ele salva os pixels como o
sensor capturou e grava uma **etiqueta EXIF** dizendo "exiba girado 90°". A galeria respeita a etiqueta, mas uma
leitura ingênua dos pixels não, e a foto chega deitada.

## Como aplicamos

Tudo isso está em `carregar_imagem` (`gabarito/alinhamento.py`):

```python
def carregar_imagem(origem):
    """Abre JPG/PNG/HEIC (respeitando a orientação EXIF) ou a 1ª página de um PDF. Retorna BGR."""
    if _eh_pdf(origem):
        return cv2.cvtColor(np.array(_renderizar_pdf(origem)), cv2.COLOR_RGB2BGR)
    ...
    with Image.open(fonte) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")   # aplica a etiqueta EXIF
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)  # Pillow (RGB) → OpenCV (BGR)
```

- **Detectar PDF:** todo arquivo PDF começa com os bytes `%PDF-`. O código olha esse "número mágico" em vez de
  confiar no nome do arquivo.
- **Renderizar PDF:** o PDF mede em **pontos** (1 ponto = 1/72 polegada). Para obter 200 DPI, a página é desenhada
  com escala `200 / 72 ≈ 2,78`:
  ```python
  documento[0].render(scale=DPI_PDF / 72).to_pil()
  ```
  Usamos 200 DPI porque fica acima da folha padrão (150 DPI), sem perder detalhe, e não pesa demais.
- **Qualquer formato vira a mesma coisa:** uma matriz NumPy BGR `(altura, largura, 3)`. Daqui para frente o resto do
  programa não precisa saber se veio de foto, print ou PDF.

## Para fixar

1. Uma foto tem `shape = (3000, 4000, 3)`. Qual a largura? *(Resposta: 4000 pixels; o shape é altura, largura, canais.)*
2. Por que a caneta azul `(R=30, G=60, B=160)` fica escura no canal R? *(Porque o valor de R é baixo: 30.)*
3. Quantos milímetros tem o marcador ArUco de 100 px da folha padrão? *(100 ÷ 150 × 25,4 ≈ 16,9 mm.)*
