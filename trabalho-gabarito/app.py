"""Corretor de gabarito — interface Streamlit.

Rode com:  streamlit run app.py
"""

from html import escape
from pathlib import Path

import streamlit as st

from gabarito import interface_html as ui
from gabarito import layout
from gabarito.alinhamento import ImagemInvalida, MarcadoresNaoEncontrados, carregar_imagem
from gabarito.correcao import GabaritoInvalido, corrigir, gabarito_de_json, gabarito_de_leitura
from gabarito.folha import folha_pdf_bytes
from gabarito.leitura import ler_folha
from gabarito.marcacoes import LIMITE_MARCADO
from gabarito.ocr import LeitorOCR
from gabarito.sintetico import Marca, folha_preenchida
from gabarito.visualizacao import desenhar_grade

ERROS_DE_LEITURA = (ImagemInvalida, MarcadoresNaoEncontrados, GabaritoInvalido)
TIPOS_FOTO = ["jpg", "jpeg", "png", "heic", "heif", "pdf"]
MODO_MANUAL, MODO_FOTO, MODO_JSON = "Selecionar alternativas", "Foto ou PDF da folha-mestre", "Arquivo JSON"

st.set_page_config(page_title="Corretor de gabarito", page_icon="📝", layout="centered")
st.html(f"<style>{(Path(__file__).parent / 'estilo.css').read_text(encoding='utf-8')}</style>")

estado = st.session_state
estado.setdefault("oficial", None)
estado.setdefault("origem_oficial", "")
estado.setdefault("dados_mestre", None)
estado.setdefault("leitura_mestre", None)
estado.setdefault("previa_manual", None)
estado.setdefault("versao_mestre", 0)
estado.setdefault("versao_aluno", 0)
estado.setdefault("limite_marcado", round(LIMITE_MARCADO * 100))


@st.cache_resource(show_spinner=False)
def leitor_ocr() -> LeitorOCR:
    return LeitorOCR()


@st.cache_data(show_spinner=False, max_entries=20)
def ler_mestre(dados: bytes, limite_marcado: float):
    return ler_folha(carregar_imagem(dados), limite_marcado=limite_marcado)


@st.cache_data(show_spinner=False, max_entries=20)
def ler_aluno(dados: bytes, limite_marcado: float):
    return ler_folha(carregar_imagem(dados), ocr=leitor_ocr(), limite_marcado=limite_marcado)


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


st.html(
    '<header class="cabecalho"><h1>Corretor de gabarito</h1>'
    "<p>Envie a foto ou o PDF da folha de respostas e veja na hora quantas questões o aluno acertou.</p></header>"
)

with st.expander("Ajustes avançados"):
    estado.limite_marcado = st.slider(
        "Sensibilidade da marcação (% de tinta dentro do quadrado para contar como marcado)",
        min_value=15,
        max_value=90,
        value=estado.limite_marcado,
        step=1,
        help=(
            "Abaixo desse valor a questão fica em dúvida (e é anulada). Se marcações fracas "
            "(ex.: um X, em vez do quadrado todo pintado) estiverem sendo anuladas, diminua o "
            f"valor. Padrão do algoritmo: {round(LIMITE_MARCADO * 100)}%."
        ),
    )
    st.caption("Depois de mudar, envie a folha de novo (ou clique em **Trocar gabarito**) para reler com o novo valor.")

limite_marcado = estado.limite_marcado / 100

passo(1, "Gabarito oficial")
with st.container(key="grupo_oficial"):
    if estado.oficial is None:
        modo = st.segmented_control(
            "Como informar o gabarito",
            [MODO_MANUAL, MODO_FOTO, MODO_JSON],
            default=MODO_MANUAL,
            label_visibility="collapsed",
        )
        modo = modo or MODO_MANUAL
        if modo == MODO_MANUAL:
            st.html('<p class="dica">Marque a alternativa certa de cada questão.</p>')
            respostas: dict[int, str | None] = {}
            for inicio in (1, 4, 7):
                colunas = st.columns(3)
                for coluna, numero in zip(colunas, range(inicio, inicio + 3)):
                    if numero > 8:
                        continue
                    with coluna:
                        respostas[numero] = st.segmented_control(
                            f"Questão {numero}",
                            layout.ALTERNATIVAS,
                            key=f"manual_{numero}_{estado.versao_mestre}",
                        )
            faltando = [n for n, letra in respostas.items() if letra is None]
            if faltando:
                st.caption(f"Marque também as questões: {', '.join(map(str, faltando))}.")
            else:
                previa = folha_preenchida([Marca(n, letra) for n, letra in respostas.items()], escala=1)
                with st.expander("Pré-visualização do gabarito", expanded=True):
                    st.image(previa, width="stretch")
                if st.button("Usar essas respostas como gabarito", type="primary", key="confirmar_manual"):
                    estado.oficial = dict(sorted(respostas.items()))
                    estado.origem_oficial = "Selecionado manualmente"
                    estado.dados_mestre = None
                    estado.leitura_mestre = None
                    estado.previa_manual = previa
                    st.rerun()
        else:
            if modo == MODO_FOTO:
                st.html(
                    '<p class="dica">Preencha uma folha com as respostas certas e envie a foto ou o PDF escaneado.</p>'
                )
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
                            leitura_mestre = ler_mestre(dados, limite_marcado)
                        estado.oficial = gabarito_de_leitura(leitura_mestre)
                    else:
                        estado.oficial = gabarito_de_json(dados)
                    estado.origem_oficial = f"{modo}: {arquivo.name}"
                    estado.dados_mestre = dados if modo == MODO_FOTO else None
                    estado.leitura_mestre = leitura_mestre
                    estado.previa_manual = None
                    st.rerun()
                except ERROS_DE_LEITURA as erro:
                    st.error(str(erro), icon=":material/error:")
                    if leitura_mestre is not None:
                        mostrar_processamento(dados, leitura_mestre)
    else:
        st.html(ui.html_gabarito(estado.oficial))
        st.html(f'<p class="origem">{escape(estado.origem_oficial)}</p>')
        if estado.leitura_mestre is not None:
            mostrar_processamento(estado.dados_mestre, estado.leitura_mestre)
        elif estado.previa_manual is not None:
            with st.expander("Ver folha do gabarito"):
                st.image(estado.previa_manual, width="stretch")
        if st.button("Trocar gabarito", key="link_trocar_gabarito"):
            estado.oficial = None
            estado.dados_mestre = None
            estado.leitura_mestre = None
            estado.previa_manual = None
            estado.versao_mestre += 1
            estado.versao_aluno += 1
            st.rerun()

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

if dados_aluno is not None:
    passo(3, "Resultado")
    with st.container(key="grupo_resultado"):
        try:
            with st.spinner("Lendo a folha do aluno…"):
                leitura_aluno = ler_aluno(dados_aluno, limite_marcado)
        except ERROS_DE_LEITURA as erro:
            st.error(str(erro), icon=":material/error:")
        else:
            resultado = corrigir(estado.oficial, leitura_aluno)
            st.html(ui.html_resultado(resultado, leitura_aluno.identificacao, leitura_aluno.erro_ocr))
            mostrar_processamento(dados_aluno, leitura_aluno)
            if st.button("Corrigir outra folha", type="primary", key="corrigir_outra"):
                estado.versao_aluno += 1
                st.rerun()

st.html('<div style="height:2.5rem"></div>')
st.download_button(
    "Baixar folha para imprimir",
    data=pdf_da_folha(),
    file_name="folha_de_respostas.pdf",
    mime="application/pdf",
    icon=":material/print:",
    key="link_baixar_folha",
)
