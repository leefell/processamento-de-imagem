"""Trechos de HTML do app (placar, réplica da folha, identificação). Estilos em estilo.css."""

from __future__ import annotations

from html import escape

from gabarito import layout
from gabarito.modelos import CampoOCR, EstadoCelula, Identificacao, LinhaResultado, Resultado, StatusQuestao
from gabarito.ocr import nivel_confianca


def _plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


def resumo(resultado: Resultado) -> str:
    partes = [
        (resultado.acertos, "certa", "certas"),
        (resultado.erradas, "errada", "erradas"),
        (resultado.em_branco, "em branco", "em branco"),
        (resultado.anuladas, "anulada", "anuladas"),
    ]
    return ", ".join(_plural(n, s, p) for n, s, p in partes if n)


def _veredito(linha: LinhaResultado) -> tuple[str, str]:
    """(classe CSS, conteúdo HTML) da linha."""
    status = linha.aluno.status
    if status is StatusQuestao.ANULADA_MULTIPLA:
        return "anulada", "Anulada<small>Marcou mais de uma</small>"
    if status is StatusQuestao.ANULADA_AMBIGUA:
        return "anulada", "Anulada<small>Marcação incompleta</small>"
    if status is StatusQuestao.EM_BRANCO:
        return "branco", "Em branco"
    return ("certa", "Certa") if linha.correta else ("errada", "Errada")


def _bolhas(linha: LinhaResultado) -> str:
    estados = {c.alternativa: c.estado for c in linha.aluno.celulas}
    if not estados and linha.aluno.letra:
        estados = {linha.aluno.letra: EstadoCelula.MARCADO}
    bolhas = []
    for alternativa in layout.ALTERNATIVAS:
        classes = ["bolha"]
        estado = estados.get(alternativa, EstadoCelula.VAZIO)
        if estado is EstadoCelula.MARCADO:
            classes.append("aluno")
        elif estado is EstadoCelula.DUVIDA:
            classes.append("duvida")
        if alternativa == linha.oficial:
            classes.append("oficial")
        titulo = "Resposta oficial" if alternativa == linha.oficial else ""
        bolhas.append(f'<span class="{" ".join(classes)}" title="{titulo}">{alternativa}</span>')
    return "".join(bolhas)


def _campo(rotulo: str, campo: CampoOCR) -> str:
    nivel = nivel_confianca(campo)
    if nivel == "vazio":
        valor, selo = '<span class="vazio">Não lido</span>', ""
    else:
        valor = escape(campo.texto)
        selo = f'<span class="conf conf-{"media" if nivel == "média" else nivel}">confiança {nivel}</span>'
    return f"<div class=\"campo\"><dt>{rotulo}</dt><dd>{valor}{selo}</dd></div>"


def html_identificacao(identificacao: Identificacao | None, erro_ocr: str | None) -> str:
    if erro_ocr:
        return f'<p class="aviso">{escape(erro_ocr)}</p>'
    if identificacao is None:
        return ""
    campos = _campo("Nome", identificacao.nome) + _campo("CPF", identificacao.cpf) + _campo("RG", identificacao.rg)
    return f'<dl class="ident">{campos}</dl>'


def html_resultado(resultado: Resultado, identificacao: Identificacao | None, erro_ocr: str | None) -> str:
    linhas = []
    for linha in resultado.linhas:
        classe, texto = _veredito(linha)
        linhas.append(
            f'<li class="linha {classe}">'
            f'<span class="num">{linha.numero}</span>'
            f'<span class="bolhas">{_bolhas(linha)}</span>'
            f'<span class="veredito">{texto}</span>'
            f"</li>"
        )
    return (
        '<section class="resultado">'
        '<div class="placar">'
        f'<span class="placar-num">{resultado.acertos}</span>'
        f'<span class="placar-de">de {resultado.total}</span>'
        "</div>"
        f'<p class="placar-resumo">{resumo(resultado)}</p>'
        f"{html_identificacao(identificacao, erro_ocr)}"
        '<div class="legenda"><span class="bolha oficial">·</span> resposta oficial'
        '<span class="bolha aluno">·</span> marcada pelo aluno</div>'
        f'<ol class="folha">{"".join(linhas)}</ol>'
        "</section>"
    )


def html_gabarito(gabarito: dict[int, str]) -> str:
    pilulas = "".join(f'<span class="pilula"><b>{n}</b>{letra}</span>' for n, letra in sorted(gabarito.items()))
    return f'<div class="pilulas">{pilulas}</div>'
