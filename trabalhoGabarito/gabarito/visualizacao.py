"""Imagem "grade detectada": a folha alinhada com cada célula contornada pelo estado lido."""

from __future__ import annotations

import cv2
import numpy as np

from gabarito.modelos import EstadoCelula, LeituraFolha

CORES_RGB = {
    EstadoCelula.MARCADO: (52, 199, 89),  # verde
    EstadoCelula.DUVIDA: (255, 159, 10),  # laranja/amarelo
    EstadoCelula.VAZIO: (174, 174, 178),  # cinza
}

AFASTAMENTO = 3
ESPESSURA = 5


def desenhar_grade(leitura: LeituraFolha) -> np.ndarray:
    """Retorna uma cópia RGB da folha alinhada com contornos coloridos e % de preenchimento."""
    img = cv2.cvtColor(leitura.alinhada, cv2.COLOR_BGR2RGB)
    for questao in leitura.questoes:
        for celula in questao.celulas:
            r, cor = celula.rect, CORES_RGB[celula.estado]
            a = AFASTAMENTO
            cv2.rectangle(img, (r.x - a, r.y - a), (r.x + r.w + a, r.y + r.h + a), cor, ESPESSURA)
            cv2.putText(
                img,
                f"{celula.preenchimento:.0%}",
                (r.x + 8, r.y + r.h + 26),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                cor,
                2,
                cv2.LINE_AA,
            )
    return img
