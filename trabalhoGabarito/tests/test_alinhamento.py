import io

import cv2
import numpy as np
import pytest
from PIL import Image

from gabarito import alinhamento, folha, layout
from gabarito.alinhamento import MarcadoresNaoEncontrados


def _bgr(img_pil):
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def test_carregar_imagem_aplica_orientacao_exif():
    retrato = Image.new("RGB", (40, 60), "white")
    exif = Image.Exif()
    exif[0x0112] = 6
    buffer = io.BytesIO()
    retrato.save(buffer, "JPEG", exif=exif)

    img = alinhamento.carregar_imagem(buffer.getvalue())

    assert img.shape[:2] == (40, 60)


def test_carregar_imagem_rejeita_arquivo_que_nao_e_imagem():
    with pytest.raises(alinhamento.ImagemInvalida):
        alinhamento.carregar_imagem(b"isto nao e uma imagem")


def _pdf(*paginas):
    buffer = io.BytesIO()
    paginas[0].save(buffer, "PDF", resolution=300, save_all=True, append_images=list(paginas[1:]))
    return buffer.getvalue()


def test_carregar_pdf_renderiza_a_pagina_e_os_marcadores_sao_encontrados(tmp_path):
    dados = folha.folha_pdf_bytes()
    caminho = tmp_path / "folha.pdf"
    caminho.write_bytes(dados)

    for origem in (dados, caminho, str(caminho)):
        img = alinhamento.carregar_imagem(origem)
        assert img.ndim == 3 and img.shape[0] > img.shape[1]
        assert alinhamento.alinhar(img).shape == (layout.ALTURA, layout.LARGURA, 3)


def test_pdf_com_varias_paginas_usa_a_primeira():
    marcada = folha.renderizar_folha(2)
    marcada.paste((0, 0, 0), (1000, 1300, 1100, 1400))
    branca = Image.new("RGB", marcada.size, "white")

    img = alinhamento.carregar_imagem(_pdf(marcada, branca))

    alinhada = alinhamento.alinhar(img)
    assert alinhada.shape == (layout.ALTURA, layout.LARGURA, 3)
    assert alinhada[650:700, 500:550].mean() < 60


def test_pdf_corrompido_gera_imagem_invalida():
    with pytest.raises(alinhamento.ImagemInvalida) as erro:
        alinhamento.carregar_imagem(b"%PDF-1.4 isto nao e um pdf de verdade")
    assert "PDF" in str(erro.value)


def test_alinhar_folha_de_impressao_volta_ao_tamanho_padrao():
    alta = _bgr(folha.renderizar_folha(2))
    padrao = _bgr(folha.renderizar_folha(1))

    alinhada = alinhamento.alinhar(alta)

    assert alinhada.shape == (layout.ALTURA, layout.LARGURA, 3)
    diferenca = cv2.absdiff(cv2.GaussianBlur(alinhada, (5, 5), 0), cv2.GaussianBlur(padrao, (5, 5), 0))
    assert diferenca.mean() < 6


def test_alinhar_desfaz_folha_de_cabeca_para_baixo():
    padrao = _bgr(folha.renderizar_folha(1))
    invertida = cv2.rotate(padrao, cv2.ROTATE_180)

    alinhada = alinhamento.alinhar(invertida)

    assert cv2.absdiff(alinhada, padrao).mean() < 6


def test_marcador_coberto_gera_erro_dizendo_quais_cantos_faltam():
    img = _bgr(folha.renderizar_folha(1))
    for id_marcador in (2, 3):
        r = layout.marcador(id_marcador)
        img[r.y : r.y + r.h, r.x : r.x + r.w] = 255

    with pytest.raises(MarcadoresNaoEncontrados) as erro:
        alinhamento.alinhar(img)

    assert erro.value.faltando == [2, 3]
    assert "inferior direito" in str(erro.value) and "inferior esquerdo" in str(erro.value)
