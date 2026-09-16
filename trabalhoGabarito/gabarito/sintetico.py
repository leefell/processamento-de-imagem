"""Geração de folhas preenchidas e "fotos" sintéticas com resposta conhecida.

Ferramenta de testes e de avaliação (scripts/gerar_amostras.py). `folha_preenchida` também é usada pelo
app para pré-visualizar o gabarito quando as respostas são selecionadas manualmente (sem foto).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from gabarito import layout
from gabarito.folha import renderizar_folha
from gabarito.modelos import Rect

PRETO_CANETA = (25, 25, 30)
AZUL_CANETA = (30, 60, 160)

FONTE_FORMA = "arial.ttf"
FONTE_CURSIVA = "segoesc.ttf"


@dataclass(frozen=True)
class Marca:
    questao: int
    alternativa: str
    tipo: str = "cheio"
    cor: tuple[int, int, int] = PRETO_CANETA


def _desenhar_marca(d: ImageDraw.ImageDraw, q: Rect, marca: Marca, rng: random.Random, s: int) -> None:
    x0, y0, x1, y1 = q.x, q.y, q.x + q.w, q.y + q.h
    if marca.tipo == "cheio":
        j = lambda: rng.uniform(2, 6) * s
        d.polygon([(x0 + j(), y0 + j()), (x1 - j(), y0 + j()), (x1 - j(), y1 - j()), (x0 + j(), y1 - j())], fill=marca.cor)
        y = y0 + 4 * s
        while y < y1 - 4 * s:
            d.line([(x0 + j(), y), (x1 - j(), y + 5 * s)], fill=marca.cor, width=6 * s)
            y += 7 * s
    elif marca.tipo == "x":
        m = 7 * s
        d.line([(x0 + m, y0 + m), (x1 - m, y1 - m)], fill=marca.cor, width=4 * s)
        d.line([(x1 - m, y0 + m), (x0 + m, y1 - m)], fill=marca.cor, width=4 * s)
    elif marca.tipo == "traco":
        cy = (y0 + y1) / 2
        d.line([(x0 + 6 * s, cy), (x1 - 6 * s, cy)], fill=marca.cor, width=5 * s)
    elif marca.tipo == "parcial":
        d.rectangle([x0 + 4 * s, y0 + 4 * s, x0 + q.w * 0.4, y1 - 4 * s], fill=marca.cor)
    else:
        raise ValueError(f"tipo de marca desconhecido: {marca.tipo}")


def folha_preenchida(
    marcas=(),
    *,
    fatores_quadrados: tuple[float, float] = (1.0, 1.0),
    nome: str | None = None,
    cpf: str | None = None,
    rg: str | None = None,
    fonte_texto: str = FONTE_FORMA,
    cor_texto: tuple[int, int, int] = AZUL_CANETA,
    escala: int = 2,
    seed: int = 0,
) -> Image.Image:
    """Folha impressa (300 DPI por padrão) com marcações e textos desenhados."""
    rng = random.Random(seed)
    s = escala
    img = renderizar_folha(escala)
    d = ImageDraw.Draw(img)

    quadrados: dict[tuple[int, str], Rect] = {}
    for questao in layout.QUESTOES:
        for alternativa in layout.ALTERNATIVAS:
            r = layout.celula(questao, alternativa)
            fator = rng.uniform(*fatores_quadrados)
            cx, cy = r.centro
            lado = r.w * fator
            q = Rect(round((cx - lado / 2) * s), round((cy - lado / 2) * s), round(lado * s), round(lado * s))
            if fator != 1.0:
                apagar = r.expandir(0.2)
                d.rectangle([apagar.x * s, apagar.y * s, (apagar.x + apagar.w) * s, (apagar.y + apagar.h) * s], fill="white")
                d.rectangle([q.x, q.y, q.x + q.w, q.y + q.h], outline=(0, 0, 0), width=3 * s)
            quadrados[(questao, alternativa)] = q

    for marca in marcas:
        _desenhar_marca(d, quadrados[(marca.questao, marca.alternativa)], marca, rng, s)

    for texto, campo in ((nome, layout.CAMPO_NOME), (cpf, layout.CAMPO_CPF), (rg, layout.CAMPO_RG)):
        if texto:
            fonte = ImageFont.truetype(fonte_texto, 42 * s)
            d.text(((campo.x + 20) * s, (campo.y + campo.h / 2) * s), texto, font=fonte, fill=cor_texto, anchor="lm")
    return img


def fotografar(
    folha: Image.Image,
    *,
    rotacao: float = 0.0,
    perspectiva: float = 0.0,
    escala: float = 0.55,
    sombra: float = 0.0,
    desfoque: float = 0.0,
    ruido: float = 0.0,
    fundo: tuple[int, int, int] = (60, 52, 45),
    qualidade_jpeg: int = 88,
    seed: int = 0,
) -> np.ndarray:
    """Simula uma foto de celular da folha sobre uma mesa. Retorna BGR."""
    rng = np.random.default_rng(seed)
    pagina = cv2.resize(np.array(folha), None, fx=escala, fy=escala, interpolation=cv2.INTER_AREA)
    h, w = pagina.shape[:2]

    lado = int(math.hypot(w, h) * 1.15)
    cantos = np.array([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]])
    cantos += rng.uniform(-perspectiva, perspectiva, cantos.shape) * w
    a = math.radians(rotacao)
    rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    destino = cantos @ rot.T + lado / 2

    origem = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    homografia = cv2.getPerspectiveTransform(origem, np.float32(destino))
    foto = cv2.warpPerspective(pagina, homografia, (lado, lado), flags=cv2.INTER_LINEAR, borderValue=fundo)
    foto = foto.astype(np.float32)

    if sombra:
        direcao = rng.uniform(0, 2 * math.pi)
        yy, xx = np.mgrid[0:lado, 0:lado].astype(np.float32) / lado
        t = xx * math.cos(direcao) + yy * math.sin(direcao)
        t = (t - t.min()) / (t.max() - t.min())
        foto *= (1 - sombra * t)[..., None]
    if desfoque:
        foto = cv2.GaussianBlur(foto, (0, 0), desfoque)
    if ruido:
        foto += rng.normal(0, ruido * 255, foto.shape).astype(np.float32)

    bgr = cv2.cvtColor(np.clip(foto, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    _, jpeg = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, qualidade_jpeg])
    return cv2.imdecode(jpeg, cv2.IMREAD_COLOR)
