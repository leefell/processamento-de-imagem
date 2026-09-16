"""Gera fotos sintéticas (com resposta esperada em .json) em amostras/sinteticas/.

Servem para testar o app sem imprimir nada e para alimentar scripts/avaliar.py.
Uso:  python scripts/gerar_amostras.py
"""

import json
import sys
from pathlib import Path

import cv2

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from gabarito.sintetico import AZUL_CANETA, FONTE_CURSIVA, FONTE_FORMA, Marca, folha_preenchida, fotografar

DESTINO = RAIZ / "amostras" / "sinteticas"

OFICIAL = {1: "B", 2: "D", 3: "A", 4: "C", 5: "C", 6: "A", 7: "D", 8: "B"}


def respostas(letras: dict[int, str]) -> list[Marca]:
    """Marcações bem preenchidas com caneta azul."""
    return [Marca(q, a, cor=AZUL_CANETA) for q, a in letras.items()]


AMOSTRAS = {
    "00_mestre": (
        [Marca(q, a) for q, a in OFICIAL.items()],
        {str(q): a for q, a in OFICIAL.items()},
        dict(),
        dict(rotacao=3, perspectiva=0.03, seed=1),
    ),
    "01_aluno_nota_8_letra_de_forma": (
        respostas(OFICIAL),
        {str(q): a for q, a in OFICIAL.items()},
        dict(nome="JOAO PEDRO SANTOS", cpf="123.456.789-09", rg="12.345.678-9"),
        dict(rotacao=-4, perspectiva=0.04, sombra=0.25, seed=2),
    ),
    "02_aluno_cursiva_com_erros": (
        respostas({1: "B", 2: "A", 3: "A", 4: "C", 5: "D", 6: "A", 7: "D"}),
        {"1": "B", "2": "A", "3": "A", "4": "C", "5": "D", "6": "A", "7": "D", "8": "EM_BRANCO"},
        dict(nome="Maria Eduarda Lima", cpf="987.654.321-00", rg="98.765.432-1", fonte_texto=FONTE_CURSIVA),
        dict(rotacao=8, perspectiva=0.05, desfoque=0.8, seed=3),
    ),
    "03_aluno_anuladas": (
        respostas({1: "B", 2: "D", 3: "A", 5: "C", 6: "A", 8: "B"})
        + [Marca(4, "A"), Marca(4, "C"), Marca(7, "D", tipo="x")],
        {"1": "B", "2": "D", "3": "A", "4": "ANULADA_MULTIPLA", "5": "C", "6": "A", "7": "ANULADA_AMBIGUA", "8": "B"},
        dict(nome="CARLOS ALBERTO", cpf="111.222.333-44", rg="11.222.333-4"),
        dict(rotacao=-15, perspectiva=0.06, sombra=0.45, ruido=0.03, seed=4),
    ),
    "04_aluno_de_cabeca_para_baixo_impressao_torta": (
        respostas({1: "A", 2: "D", 3: "B", 4: "C", 5: "C", 6: "B", 7: "D", 8: "B"}),
        {"1": "A", "2": "D", "3": "B", "4": "C", "5": "C", "6": "B", "7": "D", "8": "B"},
        dict(nome="ANA BEATRIZ", cpf="555.666.777-88", rg="55.666.777-8", fatores_quadrados=(0.85, 1.15), fonte_texto=FONTE_FORMA),
        dict(rotacao=178, perspectiva=0.05, seed=5),
    ),
}


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome, (marcas, esperado, kw_folha, kw_foto) in AMOSTRAS.items():
        foto = fotografar(folha_preenchida(marcas, **kw_folha), **kw_foto)
        cv2.imwrite(str(DESTINO / f"{nome}.jpg"), foto, [cv2.IMWRITE_JPEG_QUALITY, 90])
        info = {"respostas": esperado}
        for campo in ("nome", "cpf", "rg"):
            if campo in kw_folha:
                info[campo] = kw_folha[campo]
        (DESTINO / f"{nome}.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"ok  {nome}.jpg")
    respostas_pdf = {1: "B", 2: "D", 3: "A", 4: "C", 5: "A", 6: "A", 7: "D", 8: "B"}
    folha_pdf = folha_preenchida(respostas(respostas_pdf), nome="LUCAS MOREIRA", cpf="222.333.444-55", rg="22.333.444-5")
    folha_pdf.save(DESTINO / "05_aluno_escaneado.pdf", "PDF", resolution=300)
    info = {"respostas": {str(q): a for q, a in respostas_pdf.items()}, "nome": "LUCAS MOREIRA", "cpf": "222.333.444-55", "rg": "22.333.444-5"}
    (DESTINO / "05_aluno_escaneado.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ok  05_aluno_escaneado.pdf")

    oficial = {str(q): a for q, a in OFICIAL.items()}
    (DESTINO / "gabarito_oficial.json").write_text(json.dumps(oficial, indent=2), encoding="utf-8")
    print(f"ok  gabarito_oficial.json\nAmostras em {DESTINO}")


if __name__ == "__main__":
    main()
