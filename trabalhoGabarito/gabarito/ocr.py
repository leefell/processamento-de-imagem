"""Leitura de Nome, CPF e RG manuscritos com EasyOCR."""

from __future__ import annotations

import cv2
import numpy as np

from gabarito import layout
from gabarito.modelos import CampoOCR, Identificacao, Rect

IDIOMAS = ["pt"]
ALLOWLIST_CPF = "0123456789.-"
ALLOWLIST_RG = "0123456789.-Xx"

MARGEM_CAMPO = 8
AMPLIACAO = 2

CONFIANCA_MEDIA = 0.40
CONFIANCA_ALTA = 0.70


def recortar_campo(folha_bgr: np.ndarray, campo: Rect) -> np.ndarray:
    """Recorte em tons de cinza, sem a borda, ampliado para ajudar o OCR."""
    m = MARGEM_CAMPO
    recorte = folha_bgr[campo.y + m : campo.y + campo.h - m, campo.x + m : campo.x + campo.w - m]
    cinza = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
    return cv2.resize(cinza, None, fx=AMPLIACAO, fy=AMPLIACAO, interpolation=cv2.INTER_CUBIC)


def juntar_fragmentos(fragmentos) -> CampoOCR:
    """Une os pedaços devolvidos pelo readtext (bbox, texto, confiança) em um único campo."""
    if not fragmentos:
        return CampoOCR("", 0.0)
    ordenados = sorted(fragmentos, key=lambda f: min(p[0] for p in f[0]))
    texto = " ".join(str(f[1]).strip() for f in ordenados).strip()
    confianca = float(np.mean([f[2] for f in ordenados]))
    return CampoOCR(texto, confianca)


def nivel_confianca(campo: CampoOCR) -> str:
    if not campo.texto:
        return "vazio"
    if campo.confianca >= CONFIANCA_ALTA:
        return "alta"
    if campo.confianca >= CONFIANCA_MEDIA:
        return "média"
    return "baixa"


class LeitorOCR:
    """Chamável `alinhada -> Identificacao`. O modelo é carregado no primeiro uso (demora alguns segundos)."""

    def __init__(self) -> None:
        self._reader = None

    def _leitor(self):
        if self._reader is None:
            import easyocr

            self._reader = easyocr.Reader(IDIOMAS, gpu=False, verbose=False)
        return self._reader

    def _ler(self, folha_bgr: np.ndarray, campo: Rect, allowlist: str | None = None) -> CampoOCR:
        recorte = recortar_campo(folha_bgr, campo)
        return juntar_fragmentos(self._leitor().readtext(recorte, detail=1, allowlist=allowlist))

    def __call__(self, folha_bgr: np.ndarray) -> Identificacao:
        return Identificacao(
            nome=self._ler(folha_bgr, layout.CAMPO_NOME),
            cpf=self._ler(folha_bgr, layout.CAMPO_CPF, ALLOWLIST_CPF),
            rg=self._ler(folha_bgr, layout.CAMPO_RG, ALLOWLIST_RG),
        )
