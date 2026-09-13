# Resultados — o que deu certo e o que não deu

## 1. Fotos sintéticas (automáticas)

Gerado por `python scripts/avaliar.py amostras/sinteticas`. O detalhe está em [resultados_sinteticas.md](resultados_sinteticas.md).

- **Respostas:** 48/48 lidas corretamente (5 fotos com rotação de até 180°, perspectiva, sombra, desfoque,
  ruído e quadrados impressos entre 85% e 115% do tamanho, mais 1 PDF).
- **Suíte de testes:** 88 testes automatizados passando (`pytest`) + 1 smoke test do OCR real (`pytest -m ocr`),
  com 10 cenários de foto sintética, 3 variações de tamanho de impressão e PDF.
- **OCR:** 15/15 campos lidos 100% iguais ao esperado.

> ⚠️ **Limite desta avaliação:** nas fotos sintéticas, Nome/CPF/RG são escritos com **fontes de computador**
> (Arial e Segoe Script). A "cursiva" sintética é muito mais regular que a letra de mão real, então o resultado de OCR
> acima **não** mede letra manuscrita. Isso só aparece com fotos reais (seção 2).

## 2. Fotos reais (preencher antes da apresentação)

1. Imprima `amostras/folha_de_respostas.pdf` (ou baixe pelo app) e preencha ~8–10 folhas à mão:
   - uma **folha-mestre** bem preenchida;
   - alunos com nome em **letra de forma** e em **cursiva**;
   - casos ruins de propósito: marcação dupla, X, traço, meio preenchido, caneta azul fraca, folha amassada.
2. Fotografe com o celular (ou escaneie em PDF) e copie para `amostras/reais/`.
3. Para cada foto `x.jpg`, crie `x.json` com o esperado, por exemplo:
   ```json
   {"respostas": {"1": "A", "2": "ANULADA_MULTIPLA", "3": "EM_BRANCO", "4": "C", "5": "D", "6": "B", "7": "ANULADA_AMBIGUA", "8": "A"},
    "nome": "Maria Eduarda Lima", "cpf": "987.654.321-00", "rg": "98.765.432-1"}
   ```
4. Rode `python scripts/avaliar.py amostras/reais --saida docs/resultados_reais.md` e resuma aqui.

| Situação | Resultado nas fotos reais | Deu certo? |
|---|---|---|
| Marcação bem preenchida (preta/azul) | | |
| Marcação dupla → anulada | | |
| X / traço / meio preenchido → anulada ou em branco | | |
| Foto torta, girada ou com sombra | | |
| Nome em letra de forma | | |
| Nome em cursiva | | |
| CPF / RG manuscritos | | |

## 3. Limitações conhecidas (esperadas)

- **Cursiva:** o EasyOCR foi treinado principalmente com texto impresso. Em letra de mão cursiva real é esperado
  que erre bastante ou devolva confiança baixa (o app mostra "confiança baixa").
- **Marcador cortado ou coberto:** sem os 4 cantos a folha não é alinhada, e o app pede outra foto.
- **Marca muito leve** (lápis, caneta falhando) pode ficar abaixo de 15% e ser lida como em branco.
  Os limites ficam em `gabarito/marcacoes.py` (`LIMITE_VAZIO`, `LIMITE_MARCADO`).
- **Um X ou traço fino** pode passar abaixo de 15% e contar como em branco em vez de anulada.
