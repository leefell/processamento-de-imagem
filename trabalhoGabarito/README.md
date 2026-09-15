# Corretor de gabarito

Lê a foto (ou o PDF) de uma folha de respostas (8 questões, alternativas A–D) e diz quantas questões o aluno acertou.
Anula questões com mais de uma marcação ou com marcação incompleta, lê Nome/CPF/RG por OCR e aguenta fotos tortas,
com sombra, e impressões com quadrados de tamanhos diferentes.

📚 **Documentação didática completa (teoria + aplicação): [docs/README.md](docs/README.md)**

Design: [specs/2026-09-13-corretor-gabarito-design.md](specs/2026-09-13-corretor-gabarito-design.md)

## Começo rápido

### Opção 1: Via Docker (Recomendado)

Não precisa instalar Python, PyTorch ou dependências locais:

```bash
docker compose up --build
```

Acesse em **http://localhost:8501**. Os modelos do EasyOCR já são baixados durante o build da imagem, então a primeira correção já roda sem lentidão!

Para parar:
```bash
docker compose down
```

### Opção 2: Local (Windows)

```powershell
winget install Python.Python.3.12        # se ainda não tiver Python
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abre em http://localhost:8501. Guia completo, dicas de impressão e solução de problemas:
[docs/01-como-executar.md](docs/01-como-executar.md).

> Na execução local sem Docker, o EasyOCR baixa os modelos no primeiro uso (~20–30 s). Corrija uma folha qualquer
> **antes** da apresentação.

## Uso

1. Imprima a folha (botão **Baixar folha para imprimir** no app ou `python scripts/gerar_folha.py`).
2. Informe o **gabarito oficial**: selecione a alternativa de cada questão na própria interface (mais rápido), ou
   envie a foto/PDF da folha-mestre, ou um JSON `{"1": "A", ..., "8": "D"}`.
3. Envie a foto/PDF da **folha do aluno** e veja a nota.

Sem impressora? `python scripts/gerar_amostras.py` gera fotos sintéticas e um PDF em `amostras/sinteticas/`.

## Scripts

| Comando | O que faz |
|---|---|
| `python -m pytest` | 88 testes automáticos (`-m ocr` roda o teste do OCR real) |
| `python scripts/gerar_folha.py` | Gera a folha para imprimir (PDF + PNG) |
| `python scripts/gerar_amostras.py` | Gera fotos/PDF sintéticos com resposta conhecida |
| `python scripts/avaliar.py <pasta>` | Mede acertos de leitura e OCR numa pasta de amostras |
| `python scripts/experimentos.py [nome]` | Desliga uma parte do algoritmo e mostra quais testes quebram |
| `python scripts/gerar_figuras_docs.py` | Regera as figuras de `docs/img/` |

(Use `.\.venv\Scripts\python.exe` no lugar de `python`.)

## Estrutura

| Arquivo | Função |
|---|---|
| `gabarito/layout.py` | Coordenadas da folha (fonte única para desenhar e ler) |
| `gabarito/folha.py` | Desenha a folha (PNG/PDF) |
| `gabarito/alinhamento.py` | Foto/PDF → ArUco → homografia → folha padrão |
| `gabarito/marcacoes.py` | Máscara de tinta → % por quadrado → vazio/dúvida/marcado → resposta |
| `gabarito/ocr.py` | Nome/CPF/RG com EasyOCR |
| `gabarito/correcao.py` | Gabarito oficial (foto ou JSON) × aluno |
| `gabarito/leitura.py` | `ler_folha()`: junta alinhamento, marcações e OCR |
| `gabarito/visualizacao.py` | Imagem "grade detectada" |
| `gabarito/interface_html.py`, `estilo.css`, `app.py` | Interface Streamlit |
| `gabarito/sintetico.py` | Folhas e fotos sintéticas para testes; também gera a pré-visualização do gabarito manual |
| `docs/` | Documentação, roteiro da apresentação e resultados |
