"""Experimentos didáticos: "desliga" uma parte do algoritmo e roda os testes para ver o que quebra.

Nada é alterado nos arquivos: a mudança vale só durante esta execução.

Uso:
    python scripts/experimentos.py                 # lista os experimentos
    python scripts/experimentos.py sem_refinamento # roda um experimento
"""

import sys
from pathlib import Path

import cv2

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pytest

import gabarito.marcacoes as m


def sem_refinamento():
    """Não procura o quadrado real: usa sempre a posição do layout."""
    m.localizar_quadrado = lambda mascara, esperado: esperado


def sem_margem_interna():
    """Mede o preenchimento no quadrado inteiro, incluindo a borda impressa."""
    m.MARGEM_INTERNA = 0.0


def limite_vazio_30():
    """Sobe o limite de 'vazio' de 15% para 30%: um X passa a contar como em branco."""
    m.LIMITE_VAZIO = 0.30


def sem_dilatacao():
    """Estima o fundo só com desfoque (sem dilatação): a própria tinta entra no 'fundo'."""
    m.KERNEL_FUNDO = 1


def sem_trava_do_limiar():
    """Usa o limiar de Otsu sem prendê-lo entre 100 e 200."""
    m.LIMIAR_MIN, m.LIMIAR_MAX = 0, 255


def otsu_direto():
    """Não compensa a sombra: aplica o Otsu direto no canal mínimo."""
    original = m.etapas_mascara

    def sem_compensacao(folha):
        e = original(folha)
        limiar, mascara = cv2.threshold(e.canal, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return m.EtapasMascara(e.canal, e.fundo, e.canal, limiar, limiar, mascara)

    m.etapas_mascara = sem_compensacao


EXPERIMENTOS = {f.__name__: f for f in (sem_refinamento, sem_margem_interna, limite_vazio_30, sem_dilatacao, sem_trava_do_limiar, otsu_direto)}


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in EXPERIMENTOS:
        print(__doc__)
        for nome, funcao in EXPERIMENTOS.items():
            print(f"  {nome:22} {funcao.__doc__}")
        sys.exit(0 if len(sys.argv) == 1 else 2)

    funcao = EXPERIMENTOS[sys.argv[1]]
    print(f"Experimento: {funcao.__doc__}\n")
    funcao()
    codigo = pytest.main(["-q", "-p", "no:cacheprovider", str(RAIZ / "tests"), "-rf", "--tb=no"])
    print("\nAlgum teste falhou: essa parte do algoritmo é necessária." if codigo else "\nNenhum teste falhou.")


if __name__ == "__main__":
    main()
