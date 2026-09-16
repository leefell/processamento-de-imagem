"""Estruturas de dados compartilhadas pelo pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np


class EstadoCelula(Enum):
    VAZIO = "vazio"
    DUVIDA = "dúvida"
    MARCADO = "marcado"


class StatusQuestao(Enum):
    RESPONDIDA = "respondida"
    EM_BRANCO = "em branco"
    ANULADA_MULTIPLA = "anulada (marcação múltipla)"
    ANULADA_AMBIGUA = "anulada (marcação ambígua)"

    @property
    def anulada(self) -> bool:
        return self in (StatusQuestao.ANULADA_MULTIPLA, StatusQuestao.ANULADA_AMBIGUA)


@dataclass(frozen=True)
class Rect:
    """Retângulo em pixels da folha padrão (canto superior esquerdo + tamanho)."""

    x: int
    y: int
    w: int
    h: int

    @property
    def centro(self) -> tuple[float, float]:
        return (self.x + self.w / 2, self.y + self.h / 2)

    def encolher(self, fracao: float) -> Rect:
        """Encolhe `fracao` do tamanho em cada lado, mantendo o centro."""
        dx, dy = round(self.w * fracao), round(self.h * fracao)
        return Rect(self.x + dx, self.y + dy, self.w - 2 * dx, self.h - 2 * dy)

    def expandir(self, fracao: float) -> Rect:
        """Aumenta `fracao` do tamanho em cada lado, mantendo o centro."""
        return self.encolher(-fracao)

    def intersecta(self, outro: Rect) -> bool:
        return (
            self.x < outro.x + outro.w
            and outro.x < self.x + self.w
            and self.y < outro.y + outro.h
            and outro.y < self.y + self.h
        )


@dataclass(frozen=True)
class Celula:
    questao: int
    alternativa: str
    preenchimento: float
    estado: EstadoCelula
    rect: Rect


@dataclass(frozen=True)
class Questao:
    numero: int
    status: StatusQuestao
    letra: str | None
    celulas: tuple[Celula, ...]

    @property
    def marcadas(self) -> list[str]:
        """Alternativas com estado MARCADO (útil para exibir marcações múltiplas)."""
        return [c.alternativa for c in self.celulas if c.estado is EstadoCelula.MARCADO]


@dataclass(frozen=True)
class CampoOCR:
    texto: str
    confianca: float


@dataclass(frozen=True)
class Identificacao:
    nome: CampoOCR
    cpf: CampoOCR
    rg: CampoOCR


@dataclass(frozen=True)
class LeituraFolha:
    questoes: tuple[Questao, ...]
    alinhada: np.ndarray
    identificacao: Identificacao | None = None
    erro_ocr: str | None = None


@dataclass(frozen=True)
class LinhaResultado:
    numero: int
    oficial: str
    aluno: Questao
    correta: bool


@dataclass(frozen=True)
class Resultado:
    linhas: tuple[LinhaResultado, ...]

    @property
    def total(self) -> int:
        return len(self.linhas)

    @property
    def acertos(self) -> int:
        return sum(linha.correta for linha in self.linhas)

    @property
    def erradas(self) -> int:
        return sum(linha.aluno.status is StatusQuestao.RESPONDIDA and not linha.correta for linha in self.linhas)

    @property
    def em_branco(self) -> int:
        return sum(linha.aluno.status is StatusQuestao.EM_BRANCO for linha in self.linhas)

    @property
    def anuladas(self) -> int:
        return sum(linha.aluno.status.anulada for linha in self.linhas)
