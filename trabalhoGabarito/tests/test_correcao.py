import json

import numpy as np
import pytest

from gabarito import correcao
from gabarito.correcao import GabaritoInvalido
from gabarito.modelos import LeituraFolha, Questao, StatusQuestao

OFICIAL = {1: "A", 2: "B", 3: "C", 4: "D", 5: "A", 6: "B", 7: "C", 8: "D"}


def _leitura(respostas: dict[int, StatusQuestao | str]) -> LeituraFolha:
    questoes = []
    for n in range(1, 9):
        r = respostas.get(n, StatusQuestao.EM_BRANCO)
        if isinstance(r, str):
            questoes.append(Questao(n, StatusQuestao.RESPONDIDA, r, ()))
        else:
            questoes.append(Questao(n, r, None, ()))
    return LeituraFolha(tuple(questoes), np.zeros((1, 1, 3), np.uint8))


def test_gabarito_de_json_valido():
    texto = json.dumps({str(k): v for k, v in OFICIAL.items()})
    assert correcao.gabarito_de_json(texto) == OFICIAL
    assert correcao.gabarito_de_json(texto.encode("utf-8")) == OFICIAL


def test_gabarito_de_json_aceita_letra_minuscula_e_espacos():
    dados = {str(k): f" {v.lower()} " for k, v in OFICIAL.items()}
    assert correcao.gabarito_de_json(json.dumps(dados)) == OFICIAL


@pytest.mark.parametrize(
    "conteudo, trecho",
    [
        ("isso não é json", "JSON"),
        (json.dumps(["A", "B"]), "objeto"),
        (json.dumps({str(k): "A" for k in range(1, 8)}), "8"),
        (json.dumps({**{str(k): "A" for k in range(1, 9)}, "3": "E"}), "3"),
        (json.dumps({**{str(k): "A" for k in range(1, 9)}, "9": "A"}), "9"),
    ],
)
def test_gabarito_de_json_invalido_explica_o_problema(conteudo, trecho):
    with pytest.raises(GabaritoInvalido) as erro:
        correcao.gabarito_de_json(conteudo)
    assert trecho in str(erro.value)


def test_gabarito_de_leitura_com_todas_respondidas():
    assert correcao.gabarito_de_leitura(_leitura(OFICIAL)) == OFICIAL


def test_gabarito_de_leitura_rejeita_questoes_sem_marcacao_unica():
    respostas = {**OFICIAL, 3: StatusQuestao.EM_BRANCO, 7: StatusQuestao.ANULADA_MULTIPLA}
    with pytest.raises(GabaritoInvalido) as erro:
        correcao.gabarito_de_leitura(_leitura(respostas))
    assert erro.value.questoes == [3, 7]
    assert "3" in str(erro.value) and "7" in str(erro.value)


def test_corrigir_conta_certas_erradas_brancos_e_anuladas():
    aluno = _leitura(
        {
            1: "A",  # certa
            2: "B",  # certa
            3: "A",  # errada
            4: StatusQuestao.ANULADA_MULTIPLA,
            5: StatusQuestao.ANULADA_AMBIGUA,
            6: StatusQuestao.EM_BRANCO,
            7: "C",  # certa
            8: "C",  # errada
        }
    )

    resultado = correcao.corrigir(OFICIAL, aluno)

    assert (resultado.acertos, resultado.erradas, resultado.em_branco, resultado.anuladas) == (3, 2, 1, 2)
    assert resultado.total == 8
    assert [linha.correta for linha in resultado.linhas] == [True, True, False, False, False, False, True, False]
    assert resultado.linhas[3].oficial == "D"
