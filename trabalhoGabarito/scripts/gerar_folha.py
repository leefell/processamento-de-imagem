"""Gera a folha de respostas para imprimir.

Uso:  python scripts/gerar_folha.py [saida.pdf]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gabarito.folha import folha_pdf_bytes, renderizar_folha  # noqa: E402

saida = Path(sys.argv[1] if len(sys.argv) > 1 else "folha_de_respostas.pdf")
saida.write_bytes(folha_pdf_bytes())
renderizar_folha(2).save(saida.with_suffix(".png"))
print(f"Folha salva em {saida} e {saida.with_suffix('.png')}")
