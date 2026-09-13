import numpy as np

from gabarito import visualizacao
from gabarito.modelos import Celula, EstadoCelula, LeituraFolha, Questao, Rect, StatusQuestao


def _leitura_com(estado: EstadoCelula) -> tuple[LeituraFolha, Rect]:
    rect = Rect(100, 100, 72, 72)
    celula = Celula(1, "A", 0.8, estado, rect)
    questao = Questao(1, StatusQuestao.RESPONDIDA, "A", (celula,))
    alinhada = np.full((300, 300, 3), 255, np.uint8)
    return LeituraFolha((questao,), alinhada), rect


def _cor_na_borda(img, rect):
    return tuple(int(v) for v in img[rect.y - 2, rect.x + rect.w // 2])


def test_grade_devolve_imagem_rgb_do_mesmo_tamanho():
    leitura, _ = _leitura_com(EstadoCelula.MARCADO)
    img = visualizacao.desenhar_grade(leitura)
    assert img.shape == leitura.alinhada.shape
    assert leitura.alinhada.min() == 255  # não altera a original


def test_cor_do_contorno_depende_do_estado():
    for estado, cor in visualizacao.CORES_RGB.items():
        leitura, rect = _leitura_com(estado)
        assert _cor_na_borda(visualizacao.desenhar_grade(leitura), rect) == cor
