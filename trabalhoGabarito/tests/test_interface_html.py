import re

import numpy as np

from gabarito import interface_html as ui
from gabarito.correcao import corrigir
from gabarito.modelos import Celula, CampoOCR, EstadoCelula, Identificacao, LeituraFolha, Questao, Rect, StatusQuestao

OFICIAL = {1: "A", 2: "B", 3: "C", 4: "D", 5: "A", 6: "B", 7: "C", 8: "D"}
V, D, M = EstadoCelula.VAZIO, EstadoCelula.DUVIDA, EstadoCelula.MARCADO


def _questao(n, estados):
    from gabarito.marcacoes import status_questao

    celulas = tuple(Celula(n, a, 0.0, e, Rect(0, 0, 1, 1)) for a, e in zip("ABCD", estados))
    status, letra = status_questao(list(estados))
    return Questao(n, status, letra, celulas)


def _resultado():
    questoes = (
        _questao(1, [M, V, V, V]),  # certa
        _questao(2, [M, V, V, V]),  # errada (oficial B)
        _questao(3, [V, V, M, V]),  # certa
        _questao(4, [M, V, V, M]),  # anulada múltipla
        _questao(5, [D, V, V, V]),  # anulada ambígua
        _questao(6, [V, V, V, V]),  # em branco
        _questao(7, [V, V, M, V]),  # certa
        _questao(8, [V, V, V, M]),  # certa
    )
    return corrigir(OFICIAL, LeituraFolha(questoes, np.zeros((1, 1, 3), np.uint8)))


def test_placar_mostra_acertos_de_total():
    html = ui.html_resultado(_resultado(), None, None)
    assert re.search(r">\s*4\s*<", html)
    assert "de 8" in html


def test_resumo_so_lista_categorias_presentes_com_plural():
    assert ui.resumo(_resultado()) == "4 certas, 1 errada, 1 em branco, 2 anuladas"


def test_uma_linha_por_questao_com_classe_do_veredito():
    html = ui.html_resultado(_resultado(), None, None)
    classes = re.findall(r'<li class="linha (\w+)"', html)
    assert classes == ["certa", "errada", "certa", "anulada", "anulada", "branco", "certa", "certa"]


def test_veredito_explica_anulacao():
    html = ui.html_resultado(_resultado(), None, None)
    assert "Marcou mais de uma" in html
    assert "Marcação incompleta" in html


def test_bolha_oficial_e_bolha_do_aluno_sao_marcadas():
    html = ui.html_resultado(_resultado(), None, None)
    linha2 = re.search(r'<li class="linha errada".*?</li>', html, re.S).group(0)
    assert re.search(r'class="bolha[^"]*\baluno\b[^"]*"[^>]*>A<', linha2)
    assert re.search(r'class="bolha[^"]*\boficial\b[^"]*"[^>]*>B<', linha2)


def test_identificacao_escapa_html_e_mostra_confianca():
    ident = Identificacao(CampoOCR("<b>Ana</b>", 0.9), CampoOCR("", 0.0), CampoOCR("12", 0.2))
    html = ui.html_resultado(_resultado(), ident, None)
    assert "&lt;b&gt;Ana&lt;/b&gt;" in html and "<b>Ana</b>" not in html
    assert "Não lido" in html
    assert "confiança baixa" in html


def test_aviso_quando_ocr_falhou():
    html = ui.html_resultado(_resultado(), None, "Não foi possível ler Nome/CPF/RG: sem modelo")
    assert "sem modelo" in html


def test_pilulas_do_gabarito():
    html = ui.html_gabarito(OFICIAL)
    assert len(re.findall(r'class="pilula"', html)) == 8
    assert "<b>4</b>" in html and ">D<" in html
