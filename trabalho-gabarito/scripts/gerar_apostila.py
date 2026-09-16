"""Junta os .md de docs/ numa apostila em PDF (docs/apostila.pdf).

Markdown → HTML (com capa, sumário, diagramas mermaid e figuras) → PDF pelo Microsoft Edge em modo headless.
Uso:  python scripts/gerar_apostila.py
"""

import base64
import datetime
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify
from pygments.formatters import HtmlFormatter

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
BUILD = RAIZ / "build"
SAIDA = DOCS / "apostila.pdf"

CAPITULOS = sorted(p.name for p in DOCS.glob("[0-9][0-9]-*.md"))
APENDICES = [
    ("apresentacao.md", "A", "Roteiro da apresentação"),
    ("resultados.md", "B", "Resultados"),
    ("resultados_sinteticas.md", "C", "Avaliação das amostras sintéticas"),
]

EDGE = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]

MERMAID = re.compile(r"```mermaid\n(.*?)```", re.S)
LINK_MD = re.compile(r'href="([^"#:]+\.md)(#[^"]*)?"')


def ancora(nome_arquivo: str) -> str:
    return "sec-" + Path(nome_arquivo).stem


def converter(nome: str, texto: str) -> tuple[str, str, list[tuple[str, str]]]:
    """Retorna (título do h1, html do corpo sem o h1, [(id, título) dos h2])."""
    prefixo = Path(nome).stem[:2] + "-"

    diagramas = []

    def guardar_mermaid(m):
        diagramas.append(m.group(1))
        return f'\n<div class="mermaid-slot" data-i="{len(diagramas) - 1}"></div>\n'

    texto = MERMAID.sub(guardar_mermaid, texto)
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "codehilite", "toc", "sane_lists", "attr_list"],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "hl"},
            "toc": {"slugify": lambda v, sep: prefixo + slugify(v, sep), "toc_depth": "1-2"},
        },
    )
    corpo = md.convert(texto)

    for i, codigo in enumerate(diagramas):
        dados = base64.b64encode(codigo.encode("utf-8")).decode()
        tamanho = "grande" if codigo.count("\n") > 12 else "pequeno"
        corpo = corpo.replace(
            f'<div class="mermaid-slot" data-i="{i}"></div>', f'<figure class="mermaid {tamanho}" data-src="{dados}"></figure>'
        )

    titulo, h2s = "", []
    for item in md.toc_tokens:
        titulo = titulo or item["name"]
        h2s += [(filho["id"], filho["name"]) for filho in item["children"]]
    corpo = re.sub(r"<h1[^>]*>.*?</h1>", "", corpo, count=1, flags=re.S)

    corpo = LINK_MD.sub(lambda m: f'href="#{ancora(m.group(1))}"', corpo)
    corpo = re.sub(r'<a href="\.\./[^"]*">(.*?)</a>', r"\1", corpo)
    corpo = re.sub(r'<a href="img/">(.*?)</a>', r"\1", corpo)
    corpo = corpo.replace('src="img/', f'src="{(DOCS / "img").as_uri()}/')
    def figura_com_legenda(m):
        legenda = re.sub(r"</em><em>(.*?)</em><em>", r"<strong>\1</strong>", m.group(2), flags=re.S)
        return f"<figure>{m.group(1)}<figcaption>{legenda}</figcaption></figure>"

    corpo = re.sub(r"<p>(<img [^>]+>)</p>\s*<p><em>((?:(?!</p>).)*?)</em></p>", figura_com_legenda, corpo, flags=re.S)
    corpo = re.sub(r"<p>(<img [^>]+>)</p>", r"<figure>\1</figure>", corpo)
    return html.unescape(titulo), corpo, [(i, html.unescape(t)) for i, t in h2s]


def dividir_titulo(titulo: str) -> tuple[str, str]:
    m = re.match(r"(\d+)\.\s*(.*)", titulo)
    return (m.group(1), m.group(2)) if m else ("", titulo)


def montar_html() -> str:
    secoes, sumario = [], []

    readme = (DOCS / "README.md").read_text(encoding="utf-8")
    readme = re.sub(r"## Ordem de leitura.*?(?=## Resumo)", "", readme, flags=re.S)
    _, corpo, _ = converter("00-introducao.md", readme)
    corpo = corpo.replace("<h2", "<h3").replace("</h2>", "</h3>")
    secoes.append(f'<section class="capitulo intro" id="sec-README"><header class="abertura"><p class="num">&nbsp;</p><h1>Antes de começar</h1></header>{corpo}</section>')
    sumario.append(("sec-README", "", "Antes de começar", []))

    for nome in CAPITULOS:
        titulo, corpo, h2s = converter(nome, (DOCS / nome).read_text(encoding="utf-8"))
        numero, nome_cap = dividir_titulo(titulo)
        secoes.append(
            f'<section class="capitulo" id="{ancora(nome)}"><header class="abertura">'
            f'<p class="num">Capítulo {numero}</p><h1>{html.escape(nome_cap)}</h1></header>{corpo}</section>'
        )
        sumario.append((ancora(nome), numero, nome_cap, h2s))

    for nome, letra, rotulo in APENDICES:
        caminho = DOCS / nome
        if not caminho.exists():
            continue
        _, corpo, _ = converter(nome, caminho.read_text(encoding="utf-8"))
        secoes.append(
            f'<section class="capitulo apendice" id="{ancora(nome)}"><header class="abertura">'
            f'<p class="num">Apêndice {letra}</p><h1>{rotulo}</h1></header>{corpo}</section>'
        )
        sumario.append((ancora(nome), letra, rotulo, []))

    itens = []
    for alvo, numero, titulo, h2s in sumario:
        subs = "".join(f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in h2s)
        itens.append(
            f'<li class="cap"><a href="#{alvo}"><span class="n">{numero}</span>{html.escape(titulo)}</a>'
            + (f"<ol>{subs}</ol>" if subs else "")
            + "</li>"
        )

    hoje = datetime.date.today()
    meses = "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()
    data = f"{meses[hoje.month - 1]} de {hoje.year}"

    estilo_codigo = HtmlFormatter(style="friendly").get_style_defs(".hl")
    estilo = (RAIZ / "scripts" / "apostila.css").read_text(encoding="utf-8")

    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Apostila · Corretor de gabarito</title>
<style>{estilo}\n{estilo_codigo}</style>
</head><body>
<section class="capa">
  <p class="disciplina">Tópicos em Tecnologia da Informação<br>Processamento de imagem</p>
  <div class="capa-grade" aria-hidden="true">{"".join('<i class="on"></i>' if (q, a) in {(0, 1), (1, 3), (2, 0), (3, 2), (4, 1), (5, 0), (6, 3), (7, 1)} else "<i></i>" for q in range(8) for a in range(4))}</div>
  <h1>Corretor de gabarito</h1>
  <p class="subtitulo">Apostila de estudo: da foto da folha de respostas até a nota, com a teoria de cada etapa e como ela foi aplicada no código.</p>
  <p class="data">{data}</p>
</section>
<nav class="sumario"><h1>Sumário</h1><ol>{"".join(itens)}</ol></nav>
{"".join(secoes)}
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
(async () => {{
  try {{
    mermaid.initialize({{ startOnLoad: false, theme: "neutral", fontFamily: "Segoe UI, sans-serif",
                          flowchart: {{ htmlLabels: true, useMaxWidth: true }} }});
    const figs = [...document.querySelectorAll("figure.mermaid")];
    for (let i = 0; i < figs.length; i++) {{
      const codigo = new TextDecoder().decode(Uint8Array.from(atob(figs[i].dataset.src), c => c.charCodeAt(0)));
      const {{ svg }} = await mermaid.render("diagrama" + i, codigo);
      figs[i].innerHTML = svg;
    }}
  }} catch (e) {{
    document.body.insertAdjacentHTML("afterbegin", "<p style='color:red'>Erro no mermaid: " + e + "</p>");
  }}
  document.body.dataset.pronto = "1";
}})();
</script>
</body></html>"""


def main() -> None:
    edge = next((p for p in EDGE if p.exists()), None) or (Path(shutil.which("msedge")) if shutil.which("msedge") else None)
    if edge is None:
        sys.exit("Microsoft Edge não encontrado: abra build/apostila.html no navegador e use Imprimir → Salvar como PDF.")

    BUILD.mkdir(exist_ok=True)
    pagina = BUILD / "apostila.html"
    pagina.write_text(montar_html(), encoding="utf-8")

    perfil = BUILD / "edge-perfil"
    comando = [
        str(edge),
        "--headless=new",
        "--disable-gpu",
        f"--user-data-dir={perfil}",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=30000",
        f"--print-to-pdf={SAIDA}",
        pagina.as_uri(),
    ]
    subprocess.run(comando, check=True, capture_output=True, timeout=180)
    print(f"Apostila salva em {SAIDA} ({SAIDA.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
