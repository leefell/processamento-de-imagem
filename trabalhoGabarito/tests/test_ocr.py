import cv2
import numpy as np
import pytest

from gabarito import layout, ocr
from gabarito.modelos import CampoOCR


def test_recorte_do_campo_ignora_a_borda_e_amplia():
    folha = np.full((layout.ALTURA, layout.LARGURA, 3), 255, np.uint8)
    c = layout.CAMPO_NOME
    cv2.rectangle(folha, (c.x, c.y), (c.x + c.w, c.y + c.h), (0, 0, 0), 2)

    recorte = ocr.recortar_campo(folha, c)

    assert recorte.ndim == 2
    assert recorte.shape[0] > c.h  # ampliado
    assert recorte.min() == 255  # a borda impressa não entra no recorte


def test_juntar_fragmentos_ordena_da_esquerda_para_a_direita_e_tira_media():
    fragmentos = [
        ([[300, 0], [400, 0], [400, 40], [300, 40]], "Silva", 0.6),
        ([[10, 0], [120, 0], [120, 40], [10, 40]], "Maria", 0.8),
    ]
    campo = ocr.juntar_fragmentos(fragmentos)
    assert campo.texto == "Maria Silva"
    assert campo.confianca == pytest.approx(0.7)


def test_juntar_fragmentos_vazio():
    assert ocr.juntar_fragmentos([]) == CampoOCR("", 0.0)


@pytest.mark.parametrize("confianca, nivel", [(0.0, "baixa"), (0.39, "baixa"), (0.4, "média"), (0.69, "média"), (0.7, "alta")])
def test_nivel_de_confianca(confianca, nivel):
    assert ocr.nivel_confianca(CampoOCR("x", confianca)) == nivel


def test_campo_vazio_tem_nivel_proprio():
    assert ocr.nivel_confianca(CampoOCR("", 0.0)) == "vazio"


@pytest.mark.ocr
def test_smoke_easyocr_le_nome_em_letra_de_forma():
    from gabarito.alinhamento import alinhar
    from gabarito.sintetico import folha_preenchida, fotografar

    foto = fotografar(folha_preenchida(nome="MARIA SILVA", cpf="123.456.789-00", rg="12.345.678-9"), seed=2)
    identificacao = ocr.LeitorOCR()(alinhar(foto))

    assert "MARIA" in identificacao.nome.texto.upper()
    assert "123" in identificacao.cpf.texto
