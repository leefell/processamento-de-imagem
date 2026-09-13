from itertools import combinations

from gabarito import layout
from gabarito.modelos import Rect


def test_rect_encolher_mantem_centro():
    r = Rect(100, 200, 80, 40)
    e = r.encolher(0.25)
    assert (e.x, e.y, e.w, e.h) == (120, 210, 40, 20)
    assert e.centro == r.centro


def test_rect_expandir_mantem_centro():
    r = Rect(100, 100, 80, 80)
    e = r.expandir(0.5)
    assert (e.x, e.y, e.w, e.h) == (60, 60, 160, 160)


def test_ha_uma_celula_por_questao_e_alternativa():
    celulas = [layout.celula(q, a) for q in layout.QUESTOES for a in layout.ALTERNATIVAS]
    assert len(celulas) == 8 * 4


def test_celulas_ficam_dentro_da_pagina():
    for q in layout.QUESTOES:
        for a in layout.ALTERNATIVAS:
            r = layout.celula(q, a)
            assert r.x >= 0 and r.y >= 0
            assert r.x + r.w <= layout.LARGURA and r.y + r.h <= layout.ALTURA


def test_celulas_nao_se_sobrepoem_nem_na_janela_de_busca():
    janelas = [
        layout.celula(q, a).expandir(layout.FOLGA_BUSCA)
        for q in layout.QUESTOES
        for a in layout.ALTERNATIVAS
    ]
    for r1, r2 in combinations(janelas, 2):
        assert not r1.intersecta(r2)


def test_marcadores_ocupam_os_quatro_cantos_em_sentido_horario():
    cantos = layout.CANTOS_EXTERNOS
    assert set(cantos) == {0, 1, 2, 3}
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = (cantos[i] for i in range(4))
    assert x0 < layout.LARGURA / 2 and y0 < layout.ALTURA / 2  # sup-esq
    assert x1 > layout.LARGURA / 2 and y1 < layout.ALTURA / 2  # sup-dir
    assert x2 > layout.LARGURA / 2 and y2 > layout.ALTURA / 2  # inf-dir
    assert x3 < layout.LARGURA / 2 and y3 > layout.ALTURA / 2  # inf-esq


def test_nada_encosta_na_zona_de_silencio_dos_marcadores():
    # ArUco precisa de uma borda branca em volta para ser detectado.
    zonas = [layout.marcador(i).expandir(0.25) for i in range(4)]
    elementos = [layout.CAMPO_NOME, layout.CAMPO_CPF, layout.CAMPO_RG, layout.MOLDURA_GRADE, layout.RODAPE]
    elementos += [layout.celula(q, a) for q in layout.QUESTOES for a in layout.ALTERNATIVAS]
    for zona in zonas:
        for elemento in elementos:
            assert not zona.intersecta(elemento), (zona, elemento)


def test_grade_fica_dentro_da_moldura():
    m = layout.MOLDURA_GRADE
    for q in layout.QUESTOES:
        for a in layout.ALTERNATIVAS:
            r = layout.celula(q, a).expandir(layout.FOLGA_BUSCA)
            assert m.x < r.x and r.x + r.w < m.x + m.w
            assert m.y < r.y and r.y + r.h < m.y + m.h


def test_campos_de_identificacao_nao_invadem_a_grade():
    topo_grade = min(layout.celula(1, a).y for a in layout.ALTERNATIVAS)
    for campo in (layout.CAMPO_NOME, layout.CAMPO_CPF, layout.CAMPO_RG):
        assert campo.y + campo.h < topo_grade
