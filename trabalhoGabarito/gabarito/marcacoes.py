"""Leitura das marcações na folha padrão (já alinhada)."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from gabarito import layout
from gabarito.modelos import Celula, EstadoCelula, Questao, Rect, StatusQuestao

# Faixas de classificação (fração de tinta na parte interna do quadrado).
LIMITE_VAZIO = 0.15  # até aqui: vazio
LIMITE_MARCADO = 0.50  # a partir daqui: marcado; entre os dois: dúvida

# Parte da borda ignorada em cada lado ao medir o preenchimento.
MARGEM_INTERNA = 0.20

# Tamanho aceito para o quadrado encontrado, relativo ao esperado.
TAMANHO_MIN, TAMANHO_MAX = 0.75, 1.30

# Limiar de tinta (após normalizar o fundo) fica preso nesta faixa, para uma folha
# quase sem tinta não levar o Otsu a separar ruído do papel.
LIMIAR_MIN, LIMIAR_MAX = 100, 200

# Maior que qualquer mancha de tinta, para a dilatação "apagar" a tinta e sobrar o fundo.
KERNEL_FUNDO = 101


@dataclass(frozen=True)
class EtapasMascara:
    """Resultados intermediários da segmentação de tinta (usados também nas figuras da documentação)."""

    canal: np.ndarray  # menor valor entre B, G e R de cada pixel
    fundo: np.ndarray  # estimativa do papel sem tinta (iluminação)
    normalizada: np.ndarray  # canal ÷ fundo: papel ≈ 255 mesmo na sombra
    limiar_otsu: float  # limiar sugerido pelo Otsu
    limiar: float  # limiar usado (Otsu preso entre LIMIAR_MIN e LIMIAR_MAX)
    mascara: np.ndarray  # 255 = tinta, 0 = papel


def etapas_mascara(folha_bgr: np.ndarray) -> EtapasMascara:
    # Mínimo dos canais: papel é claro em todos; tinta azul tem R baixo, preta tem tudo baixo.
    canal = folha_bgr.min(axis=2) if folha_bgr.ndim == 3 else folha_bgr
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (KERNEL_FUNDO, KERNEL_FUNDO))
    fundo = cv2.GaussianBlur(cv2.dilate(canal, kernel), (0, 0), 15)
    normalizada = cv2.divide(canal, np.maximum(fundo, 1), scale=255)
    limiar_otsu, _ = cv2.threshold(normalizada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    limiar = float(np.clip(limiar_otsu, LIMIAR_MIN, LIMIAR_MAX))
    mascara = np.where(normalizada < limiar, 255, 0).astype(np.uint8)
    return EtapasMascara(canal, fundo, normalizada, float(limiar_otsu), limiar, mascara)


def mascara_tinta(folha_bgr: np.ndarray) -> np.ndarray:
    """Máscara 0/255 com tudo que é tinta (preta, azul...) e sem o efeito de sombras."""
    return etapas_mascara(folha_bgr).mascara


def classificar(preenchimento: float) -> EstadoCelula:
    if preenchimento <= LIMITE_VAZIO:
        return EstadoCelula.VAZIO
    if preenchimento >= LIMITE_MARCADO:
        return EstadoCelula.MARCADO
    return EstadoCelula.DUVIDA


def status_questao(estados: list[EstadoCelula]) -> tuple[StatusQuestao, str | None]:
    """Aplica as regras de anulação a uma linha A–D."""
    marcados = [i for i, e in enumerate(estados) if e is EstadoCelula.MARCADO]
    duvidas = sum(e is EstadoCelula.DUVIDA for e in estados)
    if len(marcados) >= 2:
        return StatusQuestao.ANULADA_MULTIPLA, None
    if duvidas:
        return StatusQuestao.ANULADA_AMBIGUA, None
    if marcados:
        return StatusQuestao.RESPONDIDA, layout.ALTERNATIVAS[marcados[0]]
    return StatusQuestao.EM_BRANCO, None


def localizar_quadrado(mascara: np.ndarray, esperado: Rect) -> Rect:
    """Procura, perto da posição esperada, o quadrado realmente impresso.

    Compensa impressões com escala/posição levemente diferentes do template.
    Se nada plausível for encontrado, devolve a posição esperada.
    """
    janela = esperado.expandir(layout.FOLGA_BUSCA)
    recorte = mascara[janela.y : janela.y + janela.h, janela.x : janela.x + janela.w]
    contornos, _ = cv2.findContours(recorte, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    ex, ey = esperado.centro
    melhor, melhor_dist = esperado, float("inf")
    for contorno in contornos:
        x, y, w, h = cv2.boundingRect(contorno)
        if not (TAMANHO_MIN <= w / esperado.w <= TAMANHO_MAX and TAMANHO_MIN <= h / esperado.h <= TAMANHO_MAX):
            continue
        candidato = Rect(janela.x + x, janela.y + y, w, h)
        cx, cy = candidato.centro
        dist = (cx - ex) ** 2 + (cy - ey) ** 2
        if dist < melhor_dist:
            melhor, melhor_dist = candidato, dist
    return melhor


def medir_preenchimento(mascara: np.ndarray, quadrado: Rect) -> float:
    interno = quadrado.encolher(MARGEM_INTERNA)
    regiao = mascara[interno.y : interno.y + interno.h, interno.x : interno.x + interno.w]
    return float(np.count_nonzero(regiao)) / regiao.size if regiao.size else 0.0


def ler_marcacoes(folha_bgr: np.ndarray) -> list[Questao]:
    """Lê as 8 questões de uma folha já alinhada ao tamanho padrão."""
    mascara = mascara_tinta(folha_bgr)
    questoes = []
    for numero in layout.QUESTOES:
        celulas = []
        for alternativa in layout.ALTERNATIVAS:
            quadrado = localizar_quadrado(mascara, layout.celula(numero, alternativa))
            preenchimento = medir_preenchimento(mascara, quadrado)
            celulas.append(Celula(numero, alternativa, preenchimento, classificar(preenchimento), quadrado))
        status, letra = status_questao([c.estado for c in celulas])
        questoes.append(Questao(numero, status, letra, tuple(celulas)))
    return questoes
