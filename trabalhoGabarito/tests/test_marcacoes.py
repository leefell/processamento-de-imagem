import cv2
import numpy as np
import pytest

from gabarito import folha, layout, marcacoes
from gabarito.modelos import EstadoCelula, Rect, StatusQuestao

V, D, M = EstadoCelula.VAZIO, EstadoCelula.DUVIDA, EstadoCelula.MARCADO

AZUL_CANETA = (160, 60, 30)  # BGR


def _folha_padrao() -> np.ndarray:
    return cv2.cvtColor(np.array(folha.renderizar_folha(1)), cv2.COLOR_RGB2BGR)


def _preencher(img, r: Rect, cor=(20, 20, 20)):
    cv2.rectangle(img, (r.x + 3, r.y + 3), (r.x + r.w - 4, r.y + r.h - 4), cor, thickness=-1)


def _x(img, r: Rect, espessura=5):
    cv2.line(img, (r.x + 8, r.y + 8), (r.x + r.w - 8, r.y + r.h - 8), (20, 20, 20), espessura)
    cv2.line(img, (r.x + r.w - 8, r.y + 8), (r.x + 8, r.y + r.h - 8), (20, 20, 20), espessura)


def _redesenhar_quadrado(img, r: Rect, fator: float, desloc=(0, 0)) -> Rect:
    """Apaga a célula impressa e desenha outra de tamanho/posição diferentes (impressão torta)."""
    folga = r.expandir(0.2)
    img[folga.y : folga.y + folga.h, folga.x : folga.x + folga.w] = 255
    cx, cy = r.centro
    lado = round(r.w * fator)
    novo = Rect(round(cx - lado / 2) + desloc[0], round(cy - lado / 2) + desloc[1], lado, lado)
    cv2.rectangle(img, (novo.x, novo.y), (novo.x + novo.w - 1, novo.y + novo.h - 1), (0, 0, 0), 3)
    return novo


@pytest.mark.parametrize(
    "preenchimento, esperado",
    [(0.0, V), (0.15, V), (0.16, D), (0.49, D), (0.50, M), (1.0, M)],
)
def test_classificar_por_faixas(preenchimento, esperado):
    assert marcacoes.classificar(preenchimento) is esperado


@pytest.mark.parametrize(
    "estados, status, letra",
    [
        ([M, V, V, V], StatusQuestao.RESPONDIDA, "A"),
        ([V, V, V, M], StatusQuestao.RESPONDIDA, "D"),
        ([V, V, V, V], StatusQuestao.EM_BRANCO, None),
        ([M, M, V, V], StatusQuestao.ANULADA_MULTIPLA, None),
        ([M, M, D, V], StatusQuestao.ANULADA_MULTIPLA, None),
        ([M, D, V, V], StatusQuestao.ANULADA_AMBIGUA, None),
        ([V, D, V, V], StatusQuestao.ANULADA_AMBIGUA, None),
    ],
)
def test_status_da_questao(estados, status, letra):
    assert marcacoes.status_questao(estados) == (status, letra)


def test_folha_em_branco_tem_todas_as_questoes_em_branco():
    questoes = marcacoes.ler_marcacoes(_folha_padrao())
    assert [q.numero for q in questoes] == list(layout.QUESTOES)
    assert all(q.status is StatusQuestao.EM_BRANCO for q in questoes)
    assert all(c.preenchimento < 0.05 for q in questoes for c in q.celulas)


def test_le_preenchimento_preto_azul_multiplo_e_x():
    img = _folha_padrao()
    _preencher(img, layout.celula(1, "A"))
    _preencher(img, layout.celula(2, "B"), cor=AZUL_CANETA)
    _preencher(img, layout.celula(4, "A"))
    _preencher(img, layout.celula(4, "C"))
    _x(img, layout.celula(5, "D"))

    q = {q.numero: q for q in marcacoes.ler_marcacoes(img)}

    assert (q[1].status, q[1].letra) == (StatusQuestao.RESPONDIDA, "A")
    assert (q[2].status, q[2].letra) == (StatusQuestao.RESPONDIDA, "B")
    assert q[3].status is StatusQuestao.EM_BRANCO
    assert q[4].status is StatusQuestao.ANULADA_MULTIPLA
    assert q[5].status is StatusQuestao.ANULADA_AMBIGUA


def test_papel_liso_com_ruido_nao_vira_tinta():
    # Sem tinta nenhuma, o Otsu ainda escolhe um corte e separaria o ruído do papel em
    # "claro" e "escuro". A trava LIMIAR_MIN/LIMIAR_MAX impede que isso vire tinta.
    rng = np.random.default_rng(0)
    papel = np.clip(235 + rng.normal(0, 4, (400, 400, 3)), 0, 255).astype(np.uint8)
    mascara = marcacoes.mascara_tinta(papel)
    assert np.count_nonzero(mascara) / mascara.size < 0.01


def test_sombra_forte_nao_vira_marcacao():
    img = _folha_padrao().astype(np.float32)
    gradiente = np.linspace(1.0, 0.45, img.shape[1], dtype=np.float32)[None, :, None]
    img = (img * gradiente).astype(np.uint8)
    questoes = marcacoes.ler_marcacoes(img)
    assert all(q.status is StatusQuestao.EM_BRANCO for q in questoes)


@pytest.mark.parametrize("fator", [0.85, 1.15])
def test_quadrados_impressos_com_tamanho_diferente(fator):
    img = _folha_padrao()
    cheio = _redesenhar_quadrado(img, layout.celula(6, "B"), fator)
    _preencher(img, cheio)
    for alternativa in ("A", "C", "D"):
        _redesenhar_quadrado(img, layout.celula(6, alternativa), fator)

    q6 = marcacoes.ler_marcacoes(img)[5]

    assert (q6.status, q6.letra) == (StatusQuestao.RESPONDIDA, "B")


def test_refinamento_acompanha_quadrado_deslocado():
    img = _folha_padrao()
    deslocado = _redesenhar_quadrado(img, layout.celula(7, "C"), 1.0, desloc=(16, 16))
    _preencher(img, deslocado)

    celula = marcacoes.ler_marcacoes(img)[6].celulas[2]

    assert celula.preenchimento > 0.9
    assert abs(celula.rect.x - deslocado.x) <= 3 and abs(celula.rect.y - deslocado.y) <= 3
