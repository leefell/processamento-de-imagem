"""Avalia o pipeline em uma pasta de fotos com resposta esperada e gera uma tabela Markdown.

Cada foto `x.jpg` precisa de um `x.json` ao lado:
    {"respostas": {"1": "A", ..., "8": "EM_BRANCO"}, "nome": "...", "cpf": "...", "rg": "..."}
Valores de resposta: A–D, EM_BRANCO, ANULADA_MULTIPLA ou ANULADA_AMBIGUA. Campos de texto são opcionais.

Uso:  python scripts/avaliar.py amostras/sinteticas [--saida docs/resultados.md] [--sem-ocr]
"""

import argparse
import json
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from gabarito.alinhamento import ImagemInvalida, MarcadoresNaoEncontrados, carregar_imagem
from gabarito.leitura import ler_folha
from gabarito.modelos import StatusQuestao
from gabarito.ocr import LeitorOCR

EXTENSOES = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".pdf"}


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.upper().split())


def similaridade(esperado: str, obtido: str) -> float:
    return SequenceMatcher(None, _normalizar(esperado), _normalizar(obtido)).ratio()


def _valor_lido(questao) -> str:
    return questao.letra if questao.status is StatusQuestao.RESPONDIDA else questao.status.name


def avaliar(pasta: Path, com_ocr: bool) -> str:
    ocr = LeitorOCR() if com_ocr else None
    linhas_resp = ["| Foto | Respostas lidas certo | Erros de leitura |", "|---|---|---|"]
    linhas_ocr = ["| Foto | Campo | Esperado | Lido | Semelhança | Confiança |", "|---|---|---|---|---|---|"]
    total_ok = total = 0

    for foto in sorted(p for p in pasta.iterdir() if p.suffix.lower() in EXTENSOES):
        gabarito = foto.with_suffix(".json")
        if not gabarito.exists():
            continue
        esperado = json.loads(gabarito.read_text(encoding="utf-8"))
        try:
            leitura = ler_folha(carregar_imagem(foto), ocr=ocr)
        except (ImagemInvalida, MarcadoresNaoEncontrados) as erro:
            linhas_resp.append(f"| {foto.name} | 0/8 | {erro} |")
            total += 8
            continue

        erros = []
        for q in leitura.questoes:
            valor_esperado = esperado["respostas"].get(str(q.numero))
            if valor_esperado is not None and _valor_lido(q) != valor_esperado:
                erros.append(f"Q{q.numero}: esperado {valor_esperado}, lido {_valor_lido(q)}")
        certas = 8 - len(erros)
        total_ok, total = total_ok + certas, total + 8
        linhas_resp.append(f"| {foto.name} | {certas}/8 | {'; '.join(erros) or '—'} |")

        if com_ocr:
            if leitura.erro_ocr:
                linhas_ocr.append(f"| {foto.name} | — | — | {leitura.erro_ocr} | — | — |")
            elif leitura.identificacao:
                for campo in ("nome", "cpf", "rg"):
                    if campo in esperado:
                        lido = getattr(leitura.identificacao, campo)
                        sim = similaridade(esperado[campo], lido.texto)
                        linhas_ocr.append(
                            f"| {foto.name} | {campo} | {esperado[campo]} | {lido.texto or '(vazio)'} "
                            f"| {sim:.0%} | {lido.confianca:.2f} |"
                        )
        print(f"{foto.name}: {certas}/8", file=sys.stderr)

    partes = [
        f"## Avaliação: `{pasta.as_posix()}`",
        "",
        f"**Respostas lidas corretamente:** {total_ok}/{total}" + (f" ({total_ok / total:.0%})" if total else ""),
        "",
        *linhas_resp,
    ]
    if com_ocr:
        partes += ["", "### OCR de Nome, CPF e RG", "", *linhas_ocr]
    return "\n".join(partes) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pasta", type=Path)
    parser.add_argument("--saida", type=Path)
    parser.add_argument("--sem-ocr", action="store_true")
    args = parser.parse_args()

    relatorio = avaliar(args.pasta, com_ocr=not args.sem_ocr)
    if args.saida:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(relatorio, encoding="utf-8")
        print(f"Relatório salvo em {args.saida}", file=sys.stderr)
    else:
        print(relatorio)


if __name__ == "__main__":
    main()
