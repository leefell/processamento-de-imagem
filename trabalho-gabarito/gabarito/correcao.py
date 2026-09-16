"""Gabarito oficial (de foto ou JSON) e correção da folha do aluno."""

from __future__ import annotations

import json

from gabarito import layout
from gabarito.modelos import LeituraFolha, LinhaResultado, Resultado, StatusQuestao

Gabarito = dict[int, str]


class GabaritoInvalido(ValueError):
    def __init__(self, mensagem: str, questoes: list[int] | None = None):
        super().__init__(mensagem)
        self.questoes = questoes or []


def gabarito_de_json(conteudo: str | bytes) -> Gabarito:
    """Lê {"1": "A", ..., "8": "D"}; exige as 8 questões e letras de A a D."""
    try:
        dados = json.loads(conteudo)
    except (json.JSONDecodeError, UnicodeDecodeError) as erro:
        raise GabaritoInvalido("O arquivo não é um JSON válido.") from erro
    if not isinstance(dados, dict):
        raise GabaritoInvalido('O JSON deve ser um objeto, por exemplo {"1": "A", "2": "C", ...}.')

    esperadas = {str(n) for n in layout.QUESTOES}
    chaves = {str(k).strip() for k in dados}
    if faltando := sorted(esperadas - chaves, key=int):
        raise GabaritoInvalido(f"Faltam as questões: {', '.join(faltando)}.")
    if sobrando := sorted(chaves - esperadas):
        raise GabaritoInvalido(f"Questões que não existem na prova: {', '.join(sobrando)}.")

    gabarito: Gabarito = {}
    for chave, valor in dados.items():
        letra = str(valor).strip().upper()
        if letra not in layout.ALTERNATIVAS:
            raise GabaritoInvalido(f"Questão {chave.strip()}: resposta “{valor}” inválida (use A, B, C ou D).")
        gabarito[int(chave)] = letra
    return dict(sorted(gabarito.items()))


def gabarito_de_leitura(leitura: LeituraFolha) -> Gabarito:
    """Transforma a leitura da folha-mestre em gabarito; cada questão precisa de 1 marca."""
    problemas = [q.numero for q in leitura.questoes if q.status is not StatusQuestao.RESPONDIDA]
    if problemas:
        lista = ", ".join(map(str, problemas))
        raise GabaritoInvalido(
            f"A folha-mestre precisa de exatamente uma alternativa bem preenchida por questão. "
            f"Verifique as questões: {lista}.",
            problemas,
        )
    return {q.numero: q.letra for q in leitura.questoes}


def corrigir(oficial: Gabarito, aluno: LeituraFolha) -> Resultado:
    linhas = tuple(
        LinhaResultado(
            numero=q.numero,
            oficial=oficial[q.numero],
            aluno=q,
            correta=q.status is StatusQuestao.RESPONDIDA and q.letra == oficial[q.numero],
        )
        for q in aluno.questoes
    )
    return Resultado(linhas)
