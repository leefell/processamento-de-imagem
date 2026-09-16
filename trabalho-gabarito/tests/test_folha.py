import cv2
import numpy as np
import pytest

from gabarito import folha, layout


def _detectar(imagem_rgb):
    cinza = cv2.cvtColor(imagem_rgb, cv2.COLOR_RGB2GRAY)
    dicionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    detector = cv2.aruco.ArucoDetector(dicionario, cv2.aruco.DetectorParameters())
    cantos, ids, _ = detector.detectMarkers(cinza)
    return {int(i): c.reshape(4, 2) for i, c in zip(ids.ravel(), cantos)} if ids is not None else {}


@pytest.mark.parametrize("escala", [1, 2])
def test_folha_tem_tamanho_a4_na_escala(escala):
    img = folha.renderizar_folha(escala)
    assert img.size == (layout.LARGURA * escala, layout.ALTURA * escala)


@pytest.mark.parametrize("escala", [1, 2])
def test_marcadores_da_folha_sao_detectados_na_posicao_do_layout(escala):
    img = np.array(folha.renderizar_folha(escala))
    detectados = _detectar(img)
    assert set(detectados) == {0, 1, 2, 3}
    for id_marcador, (cx, cy) in layout.CANTOS_EXTERNOS.items():
        px, py = detectados[id_marcador][id_marcador] / escala
        assert abs(px - cx) <= 2 and abs(py - cy) <= 2


def test_celulas_vazias_tem_borda_escura_e_interior_branco():
    img = np.array(folha.renderizar_folha(1).convert("L"))
    r = layout.celula(3, "C")
    interior = img[r.y + 10 : r.y + r.h - 10, r.x + 10 : r.x + r.w - 10]
    borda = img[r.y : r.y + 2, r.x : r.x + r.w]
    assert interior.min() > 200
    assert borda.mean() < 100


def test_pdf_gerado_e_um_pdf():
    dados = folha.folha_pdf_bytes()
    assert dados.startswith(b"%PDF")
