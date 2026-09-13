"""Da foto da folha até a folha padrão (reta, no tamanho do layout)."""

from __future__ import annotations

import io
from pathlib import Path

import cv2
import numpy as np
import pypdfium2 as pdfium
from PIL import Image, ImageOps, UnidentifiedImageError
from pillow_heif import register_heif_opener

from gabarito import layout
from gabarito.folha import DICIONARIO_ARUCO

register_heif_opener()

# Fotos muito grandes são reduzidas só para detectar os marcadores (mais rápido e,
# em geral, mais confiável); a homografia usa as coordenadas na resolução original.
LADO_MAX_DETECCAO = 2000
SUPERAMOSTRAGEM = 2

# Resolução usada para transformar a página do PDF em imagem. 200 DPI dá uma folha A4
# de ~1650 × 2340 px: acima da folha padrão (150 DPI), sem ficar pesado.
DPI_PDF = 200


class ImagemInvalida(ValueError):
    pass


class MarcadoresNaoEncontrados(ValueError):
    def __init__(self, faltando: list[int]):
        self.faltando = faltando
        cantos = " e ".join(layout.NOMES_CANTOS[i] for i in faltando)
        plural = "os cantos" if len(faltando) > 1 else "o canto"
        super().__init__(f"Não encontrei {plural} {cantos} da folha. Enquadre a folha inteira na foto.")


def _eh_pdf(origem: bytes | str | Path) -> bool:
    if isinstance(origem, bytes):
        return origem.lstrip()[:5] == b"%PDF-"
    return Path(origem).suffix.lower() == ".pdf"


def _renderizar_pdf(origem: bytes | str | Path) -> Image.Image:
    """Primeira página do PDF como imagem, a DPI_PDF pontos por polegada."""
    try:
        documento = pdfium.PdfDocument(origem if isinstance(origem, bytes) else Path(origem))
    except pdfium.PdfiumError as erro:
        raise ImagemInvalida("Não consegui abrir o PDF (arquivo corrompido ou protegido por senha).") from erro
    try:
        if len(documento) == 0:
            raise ImagemInvalida("O PDF não tem nenhuma página.")
        # O PDF mede em pontos (1/72 pol.): escala = DPI desejado / 72.
        return documento[0].render(scale=DPI_PDF / 72).to_pil().convert("RGB")
    finally:
        documento.close()


def carregar_imagem(origem: bytes | str | Path) -> np.ndarray:
    """Abre JPG/PNG/HEIC (respeitando a orientação EXIF) ou a 1ª página de um PDF. Retorna BGR."""
    if _eh_pdf(origem):
        return cv2.cvtColor(np.array(_renderizar_pdf(origem)), cv2.COLOR_RGB2BGR)
    try:
        fonte = io.BytesIO(origem) if isinstance(origem, bytes) else origem
        with Image.open(fonte) as img:
            img = ImageOps.exif_transpose(img).convert("RGB")
            return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    except (UnidentifiedImageError, OSError) as erro:
        raise ImagemInvalida("Não consegui abrir o arquivo como imagem (use JPG, PNG, HEIC ou PDF).") from erro


def _detector() -> cv2.aruco.ArucoDetector:
    parametros = cv2.aruco.DetectorParameters()
    parametros.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    dicionario = cv2.aruco.getPredefinedDictionary(DICIONARIO_ARUCO)
    return cv2.aruco.ArucoDetector(dicionario, parametros)


def _detectar_cantos(cinza: np.ndarray, fator: float) -> dict[int, np.ndarray]:
    img = cinza if fator == 1 else cv2.resize(cinza, None, fx=fator, fy=fator, interpolation=cv2.INTER_AREA)
    cantos, ids, _ = _detector().detectMarkers(img)
    if ids is None:
        return {}
    encontrados = {}
    for id_marcador, c in zip(ids.ravel().tolist(), cantos):
        if id_marcador in layout.CANTOS_EXTERNOS and id_marcador not in encontrados:
            # canto externo do marcador i é o seu canto de índice i (ver layout.py)
            encontrados[id_marcador] = c.reshape(4, 2)[id_marcador] / fator
    return encontrados


def alinhar(imagem_bgr: np.ndarray) -> np.ndarray:
    """Localiza os 4 marcadores e devolve a folha no tamanho padrão do layout."""
    cinza = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2GRAY)
    maior_lado = max(cinza.shape)
    fator = min(1.0, LADO_MAX_DETECCAO / maior_lado)

    encontrados = _detectar_cantos(cinza, fator)
    if len(encontrados) < 4 and fator < 1:
        encontrados = _detectar_cantos(cinza, 1.0) | encontrados

    faltando = [i for i in sorted(layout.CANTOS_EXTERNOS) if i not in encontrados]
    if faltando:
        raise MarcadoresNaoEncontrados(faltando)

    # warpPerspective não suporta INTER_AREA: gera a folha com o dobro do tamanho
    # (interpolação linear) e reduz com INTER_AREA, evitando serrilhar linhas finas.
    origem = np.float32([encontrados[i] for i in range(4)])
    destino = np.float32([layout.CANTOS_EXTERNOS[i] for i in range(4)]) * SUPERAMOSTRAGEM
    homografia = cv2.getPerspectiveTransform(origem, destino)
    grande = cv2.warpPerspective(
        imagem_bgr,
        homografia,
        (layout.LARGURA * SUPERAMOSTRAGEM, layout.ALTURA * SUPERAMOSTRAGEM),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return cv2.resize(grande, (layout.LARGURA, layout.ALTURA), interpolation=cv2.INTER_AREA)
