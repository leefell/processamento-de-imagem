"""Corretor de gabarito — interface Streamlit.

Rode com:  streamlit run app.py
"""

from html import escape
from pathlib import Path

import streamlit as st

from gabarito import interface_html as ui
from gabarito.alinhamento import ImagemInvalida, MarcadoresNaoEncontrados, carregar_imagem
from gabarito.correcao import GabaritoInvalido, corrigir, gabarito_de_json, gabarito_de_leitura
from gabarito.folha import folha_pdf_bytes
from gabarito.leitura import ler_folha
from gabarito.ocr import LeitorOCR
from gabarito.visualizacao import desenhar_grade

ERROS_DE_LEITURA = (ImagemInvalida, MarcadoresNaoEncontrados, GabaritoInvalido)
TIPOS_FOTO = ["jpg", "jpeg", "png", "heic", "heif", "pdf"]
MODO_FOTO, MODO_JSON = "Foto ou PDF da folha-mestre", "Arquivo JSON"

st.set_page_config(page_title="Corretor de gabarito", page_icon="📝", layout="centered")
st.html(f"<style>{(Path(__file__).parent / 'estilo.css').read_text(encoding='utf-8')}</style>")

estado = st.session_state
estado.setdefault("oficial", None)
estado.setdefault("origem_oficial", "")
estado.setdefault("versao_mestre", 0)
estado.setdefault("versao_aluno", 0)


# ---------- pipeline com cache (o Streamlit reexecuta o script a cada interação) ----------
@st.cache_resource(show_spinner=False)
def leitor_ocr() -> LeitorOCR:
    return LeitorOCR()


@st.cache_data(show_spinner=False, max_entries=20)
def ler_mestre(dados: bytes):
    return ler_folha(carregar_imagem(dados))


@st.cache_data(show_spinner=False, max_entries=20)
def ler_aluno(dados: bytes):
    return ler_folha(carregar_imagem(dados), ocr=leitor_ocr())


@st.cache_data(show_spinner=False)
def pdf_da_folha() -> bytes:
    return folha_pdf_bytes()


def passo(numero: int, titulo: str, ativo: bool = True) -> None:
    classe = "passo" if ativo else "passo inativo"
    st.html(f'<div class="{classe}"><span class="n">{numero}</span><span class="t">{titulo}</span></div>')


def mostrar_processamento(dados: bytes, leitura) -> None:
    with st.expander("Ver processamento"):
        grade, alinhada, original = st.tabs(["Grade detectada", "Folha alinhada", "Arquivo original"])
        grade.image(desenhar_grade(leitura), width="stretch")
        alinhada.image(leitura.alinhada, channels="BGR", width="stretch")
        original.image(carregar_imagem(dados), channels="BGR", width="stretch")


# ---------- cabeçalho ----------
st.html(
    '<header class="cabecalho"><h1>Corretor de gabarito</h1>'
    "<p>Envie a foto ou o PDF da folha de respostas e veja na hora quantas questões o aluno acertou.</p></header>"
)

# ---------- 1. gabarito oficial ----------
passo(1, "Gabarito oficial")
with st.container(key="grupo_oficial"):
    if estado.oficial is None:
        modo = st.segmented_control(
            "Como informar o gabarito", [MODO_FOTO, MODO_JSON], default=MODO_FOTO, label_visibility="collapsed"
        )
        modo = modo or MODO_FOTO
        if modo == MODO_FOTO:
            st.html('<p class="dica">Preencha uma folha com as respostas certas e envie a foto ou o PDF escaneado.</p>')
            arquivo = st.file_uploader(
                "Foto da folha-mestre",
                type=TIPOS_FOTO,
                key=f"mestre_foto_{estado.versao_mestre}",
                label_visibility="collapsed",
            )
        else:
            st.html('<p class="dica">Um arquivo como {"1": "A", "2": "C", …, "8": "D"}.</p>')
            arquivo = st.file_uploader(
                "Arquivo JSON", type=["json"], key=f"mestre_json_{estado.versao_mestre}", label_visibility="collapsed"
            )

        if arquivo is not None:
            dados = arquivo.getvalue()
            leitura_mestre = None
            try:
                if modo == MODO_FOTO:
                    with st.spinner("Lendo a folha-mestre…"):
                        leitura_mestre = ler_mestre(dados)
                    estado.oficial = gabarito_de_leitura(leitura_mestre)
                else:
                    estado.oficial = gabarito_de_json(dados)
                estado.origem_oficial = f"{modo}: {arquivo.name}"
                st.rerun()
            except ERROS_DE_LEITURA as erro:
                st.error(str(erro), icon=":material/error:")
                if leitura_mestre is not None:
                    mostrar_processamento(dados, leitura_mestre)
    else:
        st.html(ui.html_gabarito(estado.oficial))
        st.html(f'<p class="origem">{escape(estado.origem_oficial)}</p>')
        if st.button("Trocar gabarito", key="link_trocar_gabarito"):
            estado.oficial = None
            estado.versao_mestre += 1
            estado.versao_aluno += 1
            st.rerun()

# ---------- 2. folha do aluno ----------
tem_oficial = estado.oficial is not None
passo(2, "Folha do aluno", ativo=tem_oficial)
dados_aluno = None
with st.container(key="grupo_aluno"):
    if not tem_oficial:
        st.html('<p class="dica">Primeiro informe o gabarito oficial.</p>')
    else:
        st.html('<p class="dica">Foto ou PDF da folha inteira, com os quatro quadrados dos cantos visíveis.</p>')
        arquivo_aluno = st.file_uploader(
            "Foto da folha do aluno", type=TIPOS_FOTO, key=f"aluno_{estado.versao_aluno}", label_visibility="collapsed"
        )
        if arquivo_aluno is not None:
            dados_aluno = arquivo_aluno.getvalue()

# ---------- 3. resultado ----------
if dados_aluno is not None:
    passo(3, "Resultado")
    with st.container(key="grupo_resultado"):
        try:
            with st.spinner("Lendo a folha do aluno…"):
                leitura_aluno = ler_aluno(dados_aluno)
        except ERROS_DE_LEITURA as erro:
            st.error(str(erro), icon=":material/error:")
        else:
            resultado = corrigir(estado.oficial, leitura_aluno)
            st.html(ui.html_resultado(resultado, leitura_aluno.identificacao, leitura_aluno.erro_ocr))
            mostrar_processamento(dados_aluno, leitura_aluno)
            if st.button("Corrigir outra folha", type="primary", key="corrigir_outra"):
                estado.versao_aluno += 1
                st.rerun()

# ---------- rodapé ----------
st.html('<div style="height:2.5rem"></div>')
st.download_button(
    "Baixar folha para imprimir",
    data=pdf_da_folha(),
    file_name="folha_de_respostas.pdf",
    mime="application/pdf",
    icon=":material/print:",
    key="link_baixar_folha",
)
