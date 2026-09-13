"""Desenho da folha de respostas a partir de layout.py."""

from __future__ import annotations

import io

import cv2
from PIL import Image, ImageDraw, ImageFont

from gabarito import layout
from gabarito.modelos import Rect

DICIONARIO_ARUCO = cv2.aruco.DICT_4X4_50

PRETO = (0, 0, 0)
CINZA_TEXTO = (90, 90, 90)
CINZA_CAMPO = (120, 120, 120)
CINZA_MOLDURA = (210, 210, 210)
FUNDO_INSTRUCAO = (242, 242, 242)


def _fonte(tamanho: int, negrito: bool = False) -> ImageFont.FreeTypeFont:
    nomes = ("arialbd.ttf", "DejaVuSans-Bold.ttf") if negrito else ("arial.ttf", "DejaVuSans.ttf")
    for nome in nomes:
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default(tamanho)


def _escalar(r: Rect, s: int) -> tuple[int, int, int, int]:
    return (r.x * s, r.y * s, (r.x + r.w) * s, (r.y + r.h) * s)


def _texto_centrado(desenho: ImageDraw.ImageDraw, xy: tuple[float, float], texto: str, fonte, cor) -> None:
    desenho.text(xy, texto, font=fonte, fill=cor, anchor="mm")


def renderizar_folha(escala: int = 2) -> Image.Image:
    """Folha em branco. escala=1 → 150 DPI (folha padrão); escala=2 → 300 DPI (impressão)."""
    s = escala
    img = Image.new("RGB", (layout.LARGURA * s, layout.ALTURA * s), "white")
    d = ImageDraw.Draw(img)

    dicionario = cv2.aruco.getPredefinedDictionary(DICIONARIO_ARUCO)
    for id_marcador in layout.CANTOS_EXTERNOS:
        r = layout.marcador(id_marcador)
        marca = cv2.aruco.generateImageMarker(dicionario, id_marcador, r.w * s)
        img.paste(Image.fromarray(marca).convert("RGB"), (r.x * s, r.y * s))

    meio = layout.LARGURA / 2 * s
    _texto_centrado(d, (meio, 85 * s), "Folha de Respostas", _fonte(44 * s, negrito=True), PRETO)
    _texto_centrado(d, (meio, 135 * s), "Tópicos em Tecnologia da Informação", _fonte(22 * s), CINZA_TEXTO)

    # Instruções
    instr = layout.INSTRUCOES
    d.rounded_rectangle(_escalar(instr, s), radius=16 * s, fill=FUNDO_INSTRUCAO)
    y_meio = instr.y + instr.h / 2
    frase1 = "Preencha TODO o quadrado com caneta preta ou azul."
    frase2 = "Marque apenas uma alternativa por questão. Não rasure."
    _texto_centrado(d, (meio, (y_meio - 16) * s), frase1, _fonte(21 * s, negrito=True), PRETO)
    _texto_centrado(d, (meio, (y_meio + 16) * s), frase2, _fonte(21 * s), CINZA_TEXTO)

    # Identificação
    fonte_rotulo = _fonte(26 * s, negrito=True)
    for rotulo, campo, x_rotulo in (
        ("Nome:", layout.CAMPO_NOME, 100),
        ("CPF:", layout.CAMPO_CPF, 100),
        ("RG:", layout.CAMPO_RG, 700),
    ):
        d.text((x_rotulo * s, (campo.y + campo.h / 2) * s), rotulo, font=fonte_rotulo, fill=PRETO, anchor="lm")
        d.rounded_rectangle(_escalar(campo, s), radius=10 * s, outline=CINZA_CAMPO, width=2 * s)

    # Grade de respostas
    primeira = layout.celula(1, "A")
    d.rounded_rectangle(_escalar(layout.MOLDURA_GRADE, s), radius=20 * s, outline=CINZA_MOLDURA, width=2 * s)

    fonte_grade = _fonte(30 * s, negrito=True)
    for alternativa in layout.ALTERNATIVAS:
        cx, _ = layout.celula(1, alternativa).centro
        _texto_centrado(d, (cx * s, (primeira.y - 40) * s), alternativa, fonte_grade, PRETO)
    for questao in layout.QUESTOES:
        _, cy = layout.celula(questao, "A").centro
        _texto_centrado(d, (370 * s, cy * s), f"{questao}.", fonte_grade, PRETO)
        for alternativa in layout.ALTERNATIVAS:
            d.rectangle(_escalar(layout.celula(questao, alternativa), s), outline=PRETO, width=3 * s)

    rodape = layout.RODAPE
    _texto_centrado(
        d,
        (meio, (rodape.y + rodape.h / 2) * s),
        "Não dobre a folha. Na foto, os quatro quadrados dos cantos precisam aparecer.",
        _fonte(18 * s),
        CINZA_TEXTO,
    )
    return img


def folha_pdf_bytes() -> bytes:
    """Folha em PDF A4 (300 DPI), pronta para imprimir."""
    buffer = io.BytesIO()
    renderizar_folha(2).save(buffer, "PDF", resolution=300)
    return buffer.getvalue()
