# Roteiro da apresentação

**Antes de começar**
- `streamlit run app.py` já aberto no navegador (e o OCR "aquecido": corrija uma folha qualquer uma vez,
  porque o primeiro carregamento do modelo leva alguns segundos).
- Fotos reais em `amostras/reais/` e, como reserva, as sintéticas em `amostras/sinteticas/`.

## 1. A folha (1 min)
- Mostre a folha impressa: os **4 marcadores ArUco** nos cantos e a instrução "preencha todo o quadrado".
- Explique: cada marcador tem um número, então o programa sabe qual canto é qual, mesmo com a folha girada.

## 2. Gabarito oficial (1 min)
- Selecione as 8 respostas certas direto na tela (modo padrão) e mostre a pré-visualização da folha antes de
  confirmar; aponte as pílulas com o resultado.
- Mencione as alternativas por foto/PDF da folha-mestre e por arquivo JSON.

## 3. Aluno normal (2 min)
- Envie a foto e mostre o placar e a réplica da folha (contorno = oficial, preenchida = aluno).
- Abra **Ver processamento**:
  1. *Foto original*: torta, com fundo.
  2. *Folha alinhada*: homografia a partir dos 4 cantos.
  3. *Grade detectada*: % de tinta por quadrado (verde = marcado, laranja = dúvida, cinza = vazio).

## 4. Casos de anulação (1 min)
- Marcação dupla → "Anulada, marcou mais de uma".
- X ou meio preenchido → "Anulada, marcação incompleta" (entre 15% e 50% de tinta).
- Se sobrar tempo: abra **Ajustes avançados** e mostre o slider de sensibilidade mudando um X de "dúvida" para
  "marcado" ao vivo — bom gancho para falar de limiarização/Otsu.

## 5. Robustez (1 min)
- Foto girada ou de cabeça para baixo, com sombra → mesma nota.
- PDF escaneado → mesma leitura.
- Quadrados impressos com tamanhos diferentes → o programa procura o quadrado real perto da posição esperada.

## 6. Nome, CPF e RG (1 min)
- Letra de forma vs cursiva: compare o texto lido e o selo de confiança.

## 7. O que deu certo e o que não deu (2 min)
- Use a tabela de [resultados.md](resultados.md).

Para estudar cada etapa em detalhe, veja a [documentação completa](README.md). As perguntas mais prováveis estão em
[13-perguntas-e-respostas.md](13-perguntas-e-respostas.md).

## Técnicas de processamento de imagem usadas
| Etapa | Técnica |
|---|---|
| Localizar a folha | Marcadores ArUco (OpenCV) |
| Endireitar | Homografia + `warpPerspective` |
| Remover sombra | Dilatação morfológica para estimar o fundo + divisão |
| Separar tinta do papel | Menor canal RGB + limiarização de Otsu |
| Achar cada quadrado | Contornos (`findContours`) na janela de busca |
| Decidir marcação | Proporção de pixels de tinta na região interna |
| Ler nome | OCR com rede neural (EasyOCR) |
