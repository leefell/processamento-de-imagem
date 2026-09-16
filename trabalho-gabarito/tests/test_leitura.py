"""Leitura de ponta a ponta sobre fotos sintéticas com defeitos de impressão e de câmera."""

import pytest

from gabarito import leitura
from gabarito.modelos import CampoOCR, Identificacao, StatusQuestao
from gabarito.sintetico import AZUL_CANETA, Marca, folha_preenchida, fotografar

R, B, MU, AM = (
    StatusQuestao.RESPONDIDA,
    StatusQuestao.EM_BRANCO,
    StatusQuestao.ANULADA_MULTIPLA,
    StatusQuestao.ANULADA_AMBIGUA,
)

MARCAS = [
    Marca(1, "A"),
    Marca(2, "C", cor=AZUL_CANETA),
    Marca(3, "D"),
    Marca(4, "B"),
    Marca(4, "D"),
    Marca(5, "A", tipo="x"),
    Marca(7, "B", cor=AZUL_CANETA),
    Marca(8, "C", tipo="parcial"),
]
ESPERADO = {1: (R, "A"), 2: (R, "C"), 3: (R, "D"), 4: (MU, None), 5: (AM, None), 6: (B, None), 7: (R, "B"), 8: (AM, None)}

CENARIOS = {
    "reta": dict(),
    "girada_5": dict(rotacao=5),
    "girada_30": dict(rotacao=30),
    "de_cabeca_para_baixo": dict(rotacao=180),
    "perspectiva": dict(perspectiva=0.08),
    "sombra": dict(sombra=0.5),
    "sombra_forte": dict(sombra=0.75, rotacao=-12, perspectiva=0.06),
    "desfocada_e_ruidosa": dict(desfoque=1.5, ruido=0.04),
    "pequena_na_foto": dict(escala=0.35),
    "tudo_junto": dict(rotacao=-12, perspectiva=0.06, sombra=0.4, desfoque=1.0, ruido=0.03),
}


def _conferir(leitura_folha):
    obtido = {q.numero: (q.status, q.letra) for q in leitura_folha.questoes}
    assert obtido == ESPERADO


@pytest.mark.parametrize("cenario", CENARIOS)
def test_le_foto_sintetica(cenario):
    foto = fotografar(folha_preenchida(MARCAS), seed=7, **CENARIOS[cenario])
    _conferir(leitura.ler_folha(foto))


@pytest.mark.parametrize("fatores", [(0.85, 0.95), (1.05, 1.15), (0.85, 1.15)])
def test_le_folha_com_quadrados_impressos_de_tamanhos_diferentes(fatores):
    img = folha_preenchida(MARCAS, fatores_quadrados=fatores, seed=3)
    foto = fotografar(img, rotacao=4, perspectiva=0.04, seed=3)
    _conferir(leitura.ler_folha(foto))


def test_le_folha_preenchida_enviada_como_pdf():
    import io

    from gabarito.alinhamento import carregar_imagem

    buffer = io.BytesIO()
    folha_preenchida(MARCAS).save(buffer, "PDF", resolution=300)

    _conferir(leitura.ler_folha(carregar_imagem(buffer.getvalue())))


def test_ler_folha_repassa_a_folha_alinhada_para_o_ocr():
    recebido = {}

    def ocr_falso(alinhada):
        recebido["shape"] = alinhada.shape
        return Identificacao(CampoOCR("Maria", 0.9), CampoOCR("123", 0.8), CampoOCR("45", 0.7))

    resultado = leitura.ler_folha(fotografar(folha_preenchida(MARCAS), seed=1), ocr=ocr_falso)

    assert recebido["shape"] == (1754, 1240, 3)
    assert resultado.identificacao.nome.texto == "Maria"
    assert resultado.erro_ocr is None


def test_falha_no_ocr_nao_impede_a_leitura_das_respostas():
    def ocr_quebrado(_):
        raise RuntimeError("modelo não carregou")

    resultado = leitura.ler_folha(fotografar(folha_preenchida(MARCAS), seed=1), ocr=ocr_quebrado)

    assert resultado.identificacao is None
    assert "modelo não carregou" in resultado.erro_ocr
    _conferir(resultado)
