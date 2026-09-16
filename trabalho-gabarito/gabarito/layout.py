"""Fonte única da verdade das coordenadas da folha.

Tudo é expresso no espaço da folha padrão: A4 a 150 DPI (1240 × 1754 px).
O desenho da folha (folha.py) e a leitura (alinhamento.py / marcacoes.py) usam
estas mesmas constantes, então as posições nunca divergem.
"""

from gabarito.modelos import Rect

LARGURA = 1240
ALTURA = 1754

QUESTOES = range(1, 9)
ALTERNATIVAS = ("A", "B", "C", "D")

MARCADOR_LADO = 100
MARCADOR_MARGEM = 50

_ESQ = MARCADOR_MARGEM
_DIR = LARGURA - MARCADOR_MARGEM
_TOPO = MARCADOR_MARGEM
_BASE = ALTURA - MARCADOR_MARGEM
CANTOS_EXTERNOS = {0: (_ESQ, _TOPO), 1: (_DIR, _TOPO), 2: (_DIR, _BASE), 3: (_ESQ, _BASE)}
NOMES_CANTOS = {0: "superior esquerdo", 1: "superior direito", 2: "inferior direito", 3: "inferior esquerdo"}


def marcador(id_marcador: int) -> Rect:
    """Área ocupada pelo marcador `id_marcador` na folha."""
    cx, cy = CANTOS_EXTERNOS[id_marcador]
    x = cx if cx == _ESQ else cx - MARCADOR_LADO
    y = cy if cy == _TOPO else cy - MARCADOR_LADO
    return Rect(x, y, MARCADOR_LADO, MARCADOR_LADO)


INSTRUCOES = Rect(200, 172, 840, 86)

CAMPO_NOME = Rect(230, 285, 910, 80)
CAMPO_CPF = Rect(230, 395, 420, 80)
CAMPO_RG = Rect(780, 395, 360, 80)

CELULA_LADO = 72
GRADE_X0 = 480
GRADE_Y0 = 620
PASSO_X = 150
PASSO_Y = 118

MOLDURA_GRADE = Rect(280, 520, 840, 1050)
RODAPE = Rect(200, 1630, 840, 50)

FOLGA_BUSCA = 0.30


def celula(questao: int, alternativa: str) -> Rect:
    """Quadrado da alternativa `alternativa` (A–D) da questão `questao` (1–8)."""
    linha = questao - 1
    coluna = ALTERNATIVAS.index(alternativa)
    return Rect(GRADE_X0 + coluna * PASSO_X, GRADE_Y0 + linha * PASSO_Y, CELULA_LADO, CELULA_LADO)
