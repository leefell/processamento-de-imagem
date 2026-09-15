"""Ponto de entrada do pipeline: foto → respostas (+ identificação)."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from gabarito.alinhamento import alinhar
from gabarito.marcacoes import LIMITE_MARCADO, LIMITE_VAZIO, ler_marcacoes
from gabarito.modelos import Identificacao, LeituraFolha

LeitorIdentificacao = Callable[[np.ndarray], Identificacao]


def ler_folha(
    imagem_bgr: np.ndarray,
    ocr: LeitorIdentificacao | None = None,
    *,
    limite_vazio: float = LIMITE_VAZIO,
    limite_marcado: float = LIMITE_MARCADO,
) -> LeituraFolha:
    """Alinha a foto e lê as marcações; se `ocr` for passado, lê também Nome/CPF/RG.

    `limite_marcado` controla a sensibilidade da leitura das marcações (ver `marcacoes.ler_marcacoes`).
    Um erro no OCR é registrado em `erro_ocr` mas nunca impede a correção.
    Erros de alinhamento (marcadores não encontrados) são propagados.
    """
    alinhada = alinhar(imagem_bgr)
    questoes = tuple(ler_marcacoes(alinhada, limite_vazio=limite_vazio, limite_marcado=limite_marcado))

    identificacao, erro_ocr = None, None
    if ocr is not None:
        try:
            identificacao = ocr(alinhada)
        except Exception as erro:  # OCR é opcional: qualquer falha vira aviso
            erro_ocr = f"Não foi possível ler Nome/CPF/RG: {erro}"

    return LeituraFolha(questoes, alinhada, identificacao, erro_ocr)
