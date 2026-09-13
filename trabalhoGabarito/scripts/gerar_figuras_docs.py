"""Gera as figuras de docs/img/ mostrando cada etapa do pipeline sobre uma foto de exemplo.

Uso:  python scripts/gerar_figuras_docs.py
Também imprime os números citados na documentação (limiar de Otsu, homografia, preenchimentos).
"""

import sys
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from gabarito import layout, marcacoes  # noqa: E402
from gabarito.alinhamento import alinhar  # noqa: E402
from gabarito.folha import DICIONARIO_ARUCO, renderizar_folha  # noqa: E402
from gabarito.leitura import ler_folha  # noqa: E402
from gabarito.sintetico import AZUL_CANETA, Marca, folha_preenchida, fotografar  # noqa: E402
from gabarito.visualizacao import desenhar_grade  # noqa: E402

DESTINO = RAIZ / "docs" / "img"

MARCAS = [
    Marca(1, "A"),
    Marca(2, "C", cor=AZUL_CANETA),
    Marca(3, "D"),
    Marca(4, "B"),
    Marca(4, "D"),
    Marca(5, "A", tipo="x"),
    Marca(7, "B", cor=AZUL_CANETA),
    Marca(8, "C", tipo="parcial"),
]


def salvar(nome: str, img: np.ndarray, largura: int | None = None) -> None:
    if largura and img.shape[1] > largura:
        img = cv2.resize(img, None, fx=largura / img.shape[1], fy=largura / img.shape[1], interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(DESTINO / nome), img)
    print(f"  {nome}")


def recorte(img: np.ndarray, x0: int, y0: int, x1: int, y1: int) -> np.ndarray:
    return img[y0:y1, x0:x1].copy()


def rotulo(img: np.ndarray, texto: str) -> np.ndarray:
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img.copy()
    faixa = np.full((44, img.shape[1], 3), 255, np.uint8)
    cv2.putText(faixa, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2, cv2.LINE_AA)
    return np.vstack([faixa, img])


def lado_a_lado(*imgs: np.ndarray, espaco: int = 16) -> np.ndarray:
    altura = max(i.shape[0] for i in imgs)
    partes = []
    for i in imgs:
        i = cv2.cvtColor(i, cv2.COLOR_GRAY2BGR) if i.ndim == 2 else i
        pad = np.full((altura - i.shape[0], i.shape[1], 3), 255, np.uint8)
        partes += [np.vstack([i, pad]), np.full((altura, espaco, 3), 255, np.uint8)]
    return np.hstack(partes[:-1])


def histograma(normalizada: np.ndarray, limiar_otsu: float, limiar: float) -> np.ndarray:
    hist = cv2.calcHist([normalizada], [0], None, [256], [0, 256]).ravel()
    hist = np.log1p(hist)  # escala log: o papel tem muito mais pixels que a tinta
    w, h, m = 768, 360, 40
    img = np.full((h + 2 * m, w + 2 * m, 3), 255, np.uint8)
    for v in range(256):
        altura = int(hist[v] / hist.max() * h)
        x = m + v * 3
        cor = (60, 60, 60) if v < limiar else (190, 190, 190)
        cv2.rectangle(img, (x, m + h - altura), (x + 2, m + h), cor, -1)
    for valor, cor, texto, dy in ((limiar_otsu, (0, 113, 227)[::-1], f"Otsu = {limiar_otsu:.0f}", 0),):
        x = int(m + valor * 3)
        cv2.line(img, (x, m - 10), (x, m + h), cor, 2)
        cv2.putText(img, texto, (x + 6, m + 12 + dy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor, 2, cv2.LINE_AA)
    cv2.putText(img, "eixo vertical em escala logaritmica", (m + 5, m - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 120), 1, cv2.LINE_AA)
    cv2.putText(img, "tinta (escuro)", (m + 5, m + h + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (60, 60, 60), 1, cv2.LINE_AA)
    cv2.putText(img, "papel (claro)", (m + w - 140, m + h + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 120, 120), 1, cv2.LINE_AA)
    return img


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    print("Figuras:")

    # 1. folha impressa
    salvar("01_folha_impressa.png", cv2.cvtColor(np.array(renderizar_folha(1)), cv2.COLOR_RGB2BGR), 620)

    # 2. foto simulada
    folha = folha_preenchida(MARCAS, nome="JOAO PEDRO", cpf="123.456.789-09", rg="12.345.678-9", fatores_quadrados=(0.9, 1.1), seed=3)
    foto = fotografar(folha, rotacao=-12, perspectiva=0.06, sombra=0.55, desfoque=0.8, ruido=0.02, seed=7)
    salvar("02_foto.jpg", foto, 900)

    # 3. marcadores detectados + cantos externos
    cinza = cv2.cvtColor(foto, cv2.COLOR_BGR2GRAY)
    detector = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(DICIONARIO_ARUCO), cv2.aruco.DetectorParameters())
    cantos, ids, _ = detector.detectMarkers(cinza)
    marcada = foto.copy()
    cv2.aruco.drawDetectedMarkers(marcada, cantos, ids, borderColor=(0, 200, 0))
    origem = {}
    for c, i in zip(cantos, ids.ravel()):
        ponto = c.reshape(4, 2)[i]
        origem[int(i)] = ponto
        cv2.circle(marcada, tuple(int(v) for v in ponto), 28, (0, 0, 255), 8)
        cv2.putText(marcada, f"ID {i}", (int(ponto[0]) + 30, int(ponto[1]) + 60), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (0, 0, 255), 6)
    salvar("03_marcadores_detectados.jpg", marcada, 900)

    # 4. folha alinhada
    alinhada = alinhar(foto)
    salvar("04_folha_alinhada.png", alinhada, 620)

    # 5. segmentação da tinta
    e = marcacoes.etapas_mascara(alinhada)
    salvar("05_canal_minimo.png", e.canal, 620)
    salvar("06_fundo_estimado.png", e.fundo, 620)
    salvar("07_normalizada.png", e.normalizada, 620)
    salvar("08_mascara_tinta.png", e.mascara, 620)

    # 9. sem compensação de sombra (Otsu direto no canal), numa foto com sombra bem mais forte
    foto_sombra = fotografar(folha, rotacao=-12, perspectiva=0.06, sombra=0.75, seed=7)
    e_sombra = marcacoes.etapas_mascara(alinhar(foto_sombra))
    _, sem_compensar = cv2.threshold(e_sombra.canal, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    reduzir = lambda im: cv2.resize(im, None, fx=0.4, fy=0.4, interpolation=cv2.INTER_AREA)  # noqa: E731
    comparacao = lado_a_lado(
        rotulo(reduzir(e_sombra.canal), "Canal (sombra forte)"),
        rotulo(reduzir(sem_compensar), "Otsu direto"),
        rotulo(reduzir(e_sombra.mascara), "Com compensacao"),
    )
    print(f"  (sombra forte: {np.count_nonzero(sem_compensar) / sem_compensar.size:.0%} da folha vira 'tinta' sem compensar, "
          f"{np.count_nonzero(e_sombra.mascara) / e_sombra.mascara.size:.0%} com compensação)")
    salvar("09_comparacao_sombra.png", comparacao)

    # 10. histograma
    salvar("10_histograma_otsu.png", histograma(e.normalizada, e.limiar_otsu, e.limiar))

    # 11. canais de cor numa marca azul e numa preta
    x0, y0, x1, y1 = 440, 590, 1040, 890  # questões 1–2
    crop = recorte(alinhada, x0, y0, x1, y1)
    b, g, r = cv2.split(crop)
    esc = 0.5
    pequeno = lambda im: cv2.resize(im, None, fx=esc, fy=esc, interpolation=cv2.INTER_AREA)  # noqa: E731
    salvar(
        "11_canais_de_cor.png",
        np.vstack(
            [
                lado_a_lado(rotulo(pequeno(crop), "Colorida"), rotulo(pequeno(r), "Canal R")),
                np.full((16, 2 * int(crop.shape[1] * esc) + 16, 3), 255, np.uint8),
                lado_a_lado(rotulo(pequeno(b), "Canal B"), rotulo(pequeno(e.canal[y0:y1, x0:x1]), "Minimo (B,G,R)")),
            ]
        ),
    )

    # 12. janela de busca, quadrado encontrado e região interna (questão 5, alternativa A = X)
    mascara_bgr = cv2.cvtColor(e.mascara, cv2.COLOR_GRAY2BGR)
    desenho = cv2.addWeighted(mascara_bgr, 0.35, np.full_like(mascara_bgr, 255), 0.65, 0)
    desenho[e.mascara > 0] = (40, 40, 40)
    for alternativa in layout.ALTERNATIVAS:
        esperado = layout.celula(5, alternativa)
        janela = esperado.expandir(layout.FOLGA_BUSCA)
        achado = marcacoes.localizar_quadrado(e.mascara, esperado)
        interno = achado.encolher(marcacoes.MARGEM_INTERNA)
        cv2.rectangle(desenho, (janela.x, janela.y), (janela.x + janela.w, janela.y + janela.h), (200, 160, 0), 2)
        cv2.rectangle(desenho, (esperado.x, esperado.y), (esperado.x + esperado.w, esperado.y + esperado.h), (255, 0, 180), 1)
        cv2.rectangle(desenho, (achado.x, achado.y), (achado.x + achado.w, achado.y + achado.h), (0, 180, 0), 2)
        cv2.rectangle(desenho, (interno.x, interno.y), (interno.x + interno.w, interno.y + interno.h), (0, 140, 255), 2)
        p = marcacoes.medir_preenchimento(e.mascara, achado)
        cv2.putText(desenho, f"{p:.0%}", (achado.x + 10, janela.y + janela.h + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    c5 = layout.celula(5, "A").expandir(0.6)
    salvar("12_janela_de_busca.png", recorte(desenho, c5.x - 10, c5.y - 10, layout.celula(5, "D").x + 120, c5.y + c5.h + 40), 900)

    # 13. grade detectada
    leitura = ler_folha(foto)
    salvar("13_grade_detectada.png", cv2.cvtColor(desenhar_grade(leitura), cv2.COLOR_RGB2BGR), 620)

    # números para a documentação
    destino = np.float32([layout.CANTOS_EXTERNOS[i] for i in range(4)])
    h = cv2.getPerspectiveTransform(np.float32([origem[i] for i in range(4)]), destino)
    print("\nNúmeros:")
    print(f"  foto: {foto.shape[1]}x{foto.shape[0]} px")
    print(f"  cantos externos na foto: { {i: tuple(round(float(v), 1) for v in origem[i]) for i in range(4)} }")
    print(f"  homografia (foto -> folha padrão):\n{np.array2string(h, precision=4, suppress_small=True)}")
    print(f"  h31 = {h[2, 0]:.2e}   h32 = {h[2, 1]:.2e}")
    for i in range(4):
        x, y = origem[i]
        p = h @ np.array([x, y, 1.0])
        print(f"  canto {i}: ({x:.0f}, {y:.0f}) -> w={p[2]:.4f} -> ({p[0] / p[2]:.1f}, {p[1] / p[2]:.1f})")
    print(f"  limiar Otsu: {e.limiar_otsu:.1f}  usado: {e.limiar:.1f}")
    for q in leitura.questoes:
        print(f"  Q{q.numero}: {q.status.name:18} {q.letra or '-'}  " + "  ".join(f"{c.alternativa}={c.preenchimento:.0%}" for c in q.celulas))


if __name__ == "__main__":
    main()
