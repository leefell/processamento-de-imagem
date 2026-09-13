# Corretor de Gabarito — Design

**Data:** 2026-09-13
**Disciplina:** Tópicos em Tecnologia da Informação (Prof. Ivan Oliveira Lopes)
**Origem:** `specs/Trabalho Gabarito (1).pptx`

## 1. Objetivo

Software que lê a folha de respostas de uma prova a partir de uma **foto de celular** e informa
**quantas questões foram respondidas corretamente**.

Enunciado do professor:
- A prova tem **8 questões**, cada uma com **4 alternativas (A–D)**.
- O software deve dizer quantas questões foram respondidas corretamente.

Requisitos adicionais combinados com o professor:
- Stack livre (não precisa ser MATLAB); uso de IA liberado.
- Questão com **mais de uma alternativa marcada é anulada**.
- A folha deve pedir que o quadrado seja **totalmente preenchido**.
- Ler o **Nome** manuscrito e verificar o comportamento com **letra de forma** e **cursiva**.
- Tratar **impressões tortas** (ex.: quadrados impressos com tamanhos diferentes).
- Layout da folha livre.
- **Entrega:** apresentar funcionando (só demonstração), dizendo o que deu certo e o que não deu.

## 2. Decisões

| Tema | Decisão |
|---|---|
| Stack | Python 3.12 + OpenCV + NumPy + Pillow |
| Entrada | Arquivo de foto de celular (JPG/PNG/HEIC) ou **PDF** (1ª página renderizada a 200 DPI com `pypdfium2`; pedido depois do design inicial) |
| Gabarito oficial | Foto de uma folha-mestre **ou** arquivo JSON |
| OCR (Nome, CPF, RG) | EasyOCR (`pt`), local |
| Interface | App web local em Streamlit, visual Apple-like (implementado com a skill `frontend-design`) |
| Folha | Gerada por código (PDF/PNG) a partir de um layout único |
| Localização da folha | 4 marcadores ArUco nos cantos + homografia + refinamento local por célula |
| Marca fraca | 3 faixas: vazio / dúvida / marcado; dúvida anula a questão |

## 3. Arquitetura

```
trabalhoGabarito/
├── gabarito/
│   ├── __init__.py
│   ├── layout.py        # fonte única da verdade das coordenadas
│   ├── folha.py         # desenha a folha (Pillow, 300 DPI) → PNG/PDF
│   ├── alinhamento.py   # foto → ArUco → homografia → folha padrão
│   ├── marcacoes.py     # folha padrão → % preenchimento → estado → resposta por questão
│   ├── ocr.py           # recorte de Nome/CPF/RG → EasyOCR
│   ├── correcao.py      # gabarito oficial × aluno → Resultado; carga de JSON
│   ├── leitura.py       # ler_folha(imagem) orquestra alinhamento + marcações (+ OCR opcional)
│   ├── visualizacao.py  # overlay "grade detectada"
│   ├── interface_html.py # HTML do placar, réplica da folha e identificação (função pura, testada)
│   ├── sintetico.py     # folhas/fotos sintéticas para testes e avaliação (não usado pelo app)
│   └── modelos.py       # dataclasses e enums
├── app.py               # Streamlit
├── estilo.css           # visual Apple-like
├── .streamlit/config.toml
├── scripts/
│   ├── gerar_folha.py
│   ├── gerar_amostras.py
│   └── avaliar.py
├── amostras/{sinteticas,reais}/
├── tests/
├── docs/{resultados.md,apresentacao.md}
├── requirements.txt
└── README.md
```

Princípios:
- `layout.py` é usado tanto por quem **desenha** a folha quanto por quem **lê**, então as coordenadas nunca divergem.
- O pipeline não depende do Streamlit: `ler_folha(imagem) -> LeituraFolha` é testável com pytest.
- Folha-mestre e folha do aluno passam pelo **mesmo** pipeline; muda só a validação.
- O leitor EasyOCR é criado uma vez (lazy singleton; `st.cache_resource` no app).

## 4. Layout da folha (`layout.py`)

- Espaço de coordenadas canônico: **A4 a 150 DPI → 1240 × 1754 px**. A folha impressa é desenhada a 300 DPI
  (fator 2) a partir das mesmas coordenadas.
- 4 marcadores ArUco `DICT_4X4_50`: ID 0 sup-esq, 1 sup-dir, 2 inf-dir, 3 inf-esq, com margem branca em volta.
- O **canto externo** de cada marcador é o ponto de referência da homografia.
- Campos: caixas **Nome** (linha inteira), **CPF** e **RG**.
- Grade de respostas 8 × 4: rótulos 1–8 nas linhas, A–D nas colunas, quadrados de 72 px com borda preta,
  passo de 150 px (colunas) e 118 px (linhas). As janelas de busca (+30% por lado) não se sobrepõem, e nada entra
  na zona de silêncio dos marcadores (ambas as regras são verificadas em `tests/test_layout.py`).
- Instrução impressa: *"Preencha TODO o quadrado com caneta preta ou azul. Não rasure. Marque apenas uma alternativa por questão."*
- O layout mantém a aparência da folha do professor (Nome/CPF/RG no topo, questões à esquerda, respostas à direita).

## 5. Pipeline de leitura

### 5.1 Alinhamento (`alinhamento.py`)
1. Carregar a imagem aplicando a **orientação EXIF**; HEIC via `pillow-heif`. PDF (detectado pelos bytes `%PDF-`
   ou pela extensão): renderizar só a 1ª página a 200 DPI; PDF corrompido/sem páginas → `ImagemInvalida`.
2. Converter para cinza e detectar ArUco (`cv2.aruco.ArucoDetector`). Se a imagem for grande, detectar numa versão
   reduzida (lado maior ≤ 2000 px) e reescalar os cantos.
3. Exigir IDs 0–3. Se faltar algum: `MarcadoresNaoEncontrados(faltando=[...])`, com nomes legíveis dos cantos.
4. `getPerspectiveTransform` (cantos externos → cantos canônicos) e `warpPerspective` para o **dobro** de
   1240 × 1754, com interpolação linear, reduzindo depois com `INTER_AREA` (o warp não suporta `INTER_AREA`).

### 5.2 Máscara de tinta
1. Canal = **mínimo entre R, G e B** (tinta azul e preta ficam escuras; papel fica claro).
2. Compensar sombra: estimar o fundo com **dilatação 101×101** (maior que qualquer mancha de tinta) + desfoque e
   dividir o canal por esse fundo.
3. Limiarizar com Otsu, mantendo o limiar entre 100 e 200 → máscara binária de tinta.

### 5.3 Células (`marcacoes.py`)
1. Para cada célula esperada, buscar numa janela 30% maior (por lado) um contorno cuja caixa tenha entre 0,75× e
   1,3× o lado esperado e centro mais próximo do esperado. Se não encontrar, usar o retângulo do template.
2. Medir o preenchimento na **região interna** (retângulo encolhido ~20% por lado).
3. Classificar (constantes ajustáveis):

| % preenchido | Estado |
|---|---|
| ≤ 15% | `VAZIO` |
| > 15% e < 50% | `DUVIDA` |
| ≥ 50% | `MARCADO` |

### 5.4 Resposta por questão

| Situação na linha A–D | Status |
|---|---|
| exatamente 1 `MARCADO` e 0 `DUVIDA` | `RESPONDIDA` (letra) |
| 0 `MARCADO` e 0 `DUVIDA` | `EM_BRANCO` |
| ≥ 2 `MARCADO` | `ANULADA_MULTIPLA` |
| ≥ 1 `DUVIDA` e ≤ 1 `MARCADO` | `ANULADA_AMBIGUA` |

### 5.5 OCR (`ocr.py`)
- Recortar cada campo da folha alinhada (sem a borda), ampliar 2× e passar ao EasyOCR `Reader(['pt'])`.
- Allowlists: CPF `0123456789.-`; RG `0123456789.-Xx`; Nome sem allowlist.
- Juntar os fragmentos da esquerda para a direita; retornar `CampoOCR(texto, confianca)` com a confiança média.
- Confiança < 0,40 aparece como "baixa confiança". **Falha de OCR nunca bloqueia a correção.**

## 6. Gabarito oficial e correção (`correcao.py`)

- **Por foto:** `ler_folha` na folha-mestre; as 8 questões precisam sair `RESPONDIDA`. Caso contrário,
  `GabaritoInvalido` lista as questões com problema.
- **Por JSON:** `{"1":"A", ..., "8":"D"}` com as 8 chaves obrigatórias e valores de A a D. Qualquer desvio gera `GabaritoInvalido` com mensagem clara.
- **Pontuação:** ponto só quando a letra do aluno é igual à oficial. `EM_BRANCO` e `ANULADA_*` valem 0.
- `Resultado`: `acertos`, `erradas`, `em_branco`, `anuladas`, `total=8` e uma linha por questão
  (oficial, aluno, status, % das 4 células).

## 7. Interface (`app.py`)

Página única, coluna central, sem sidebar, com três cartões:
1. **Gabarito oficial:** controle segmentado *Foto da folha-mestre | Arquivo JSON*, upload, pílulas `1 A · 2 C …` e botão *Trocar gabarito*.
2. **Folha do aluno:** bloqueado até o gabarito ser carregado; upload JPG/PNG/HEIC.
3. **Resultado:** número grande `X / 8`; contagem de erradas/em branco/anuladas; Nome/CPF/RG com indicador
   de confiança; tabela por questão; expander *Ver processamento* (original → alinhada → grade detectada com
   contornos verde/amarelo/cinza e %); botão *Corrigir outra folha* (mantém o gabarito).
- Rodapé: *Baixar folha para imprimir* (PDF).
- Estado em `st.session_state`.
- Erros aparecem dentro do cartão, em linguagem humana (ex.: "Não encontrei os cantos inferior-esquerdo e
  inferior-direito — enquadre a folha inteira").
- Visual Apple-like: fundo `#F5F5F7`, cartões brancos arredondados com sombra suave, texto `#1D1D1F`, acento
  `#0071E3`, fonte do sistema, bastante espaço em branco. Tema em `.streamlit/config.toml` + CSS mínimo.
  Os detalhes finais saem da skill `frontend-design`.

## 8. Testes

- `scripts/gerar_amostras.py` gera fotos sintéticas com resposta esperada conhecida: preenchimento total preto/azul,
  X, traço, meio preenchido, dupla, branco; rotação 5°/30°/180°, perspectiva, quadrados impressos a 85–115%,
  escala, desfoque, ruído, sombra, fundo escuro.
- pytest:
  - `layout`: células dentro da página, sem sobreposição, marcadores nos cantos.
  - `marcacoes`: faixas de classificação e tabela de status.
  - `alinhamento`/`leitura`: amostras sintéticas lidas corretamente; marcador ausente gera erro nomeando os cantos.
  - `correcao`: contagens; mestre com problema e JSON inválido são rejeitados.
  - `ocr`: só smoke test, marcado `@pytest.mark.ocr` (fora da execução padrão).
- Fotos reais em `amostras/reais/` (com `.json` esperado) e `scripts/avaliar.py` geram a tabela de
  `docs/resultados.md`, que alimenta o "o que deu certo / o que não deu".

## 9. Apresentação (`docs/apresentacao.md`)

1. Folha gerada: ArUco e instrução de preenchimento.
2. Foto da folha-mestre → pílulas do gabarito.
3. Aluno normal → nota → *Ver processamento*.
4. Marcação dupla e X → anuladas.
5. Foto torta, com sombra ou girada → funciona.
6. Nome em letra de forma vs cursiva → comparar a confiança do OCR.
7. Tabela de resultados: o que deu certo e o que não deu.

## 10. Setup e riscos

- Python 3.12, `.venv` e `pip install -r requirements.txt`. Usar **`opencv-python-headless`** (o EasyOCR já
  depende dele; instalar junto com `opencv-python` gera conflito no `cv2`). Testado com OpenCV 5.0,
  Streamlit 1.63 e EasyOCR 1.7.2.
- O EasyOCR instala o PyTorch CPU (centenas de MB) e baixa os modelos no primeiro uso. **Rodar uma vez antes da
  apresentação.**
- Expectativa: letra de forma razoável, **cursiva provavelmente ruim** (limitação conhecida do EasyOCR, a relatar).
- Marcador cortado na foto → leitura impossível; o app orienta a refazer a foto.

## 11. Fora do escopo

Webcam ao vivo, correção em lote, banco de dados/histórico, login, número de questões variável pela interface
(o layout é parametrizado no código, mas o app assume 8 × 4) e deploy.
