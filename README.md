# Processamento de Imagem

Material de aula da disciplina de Processamento de Imagem. Contém scripts MATLAB das aulas práticas, exercícios de simulado e um trabalho final em Python.

## Estrutura

```
.
├── aulas/
│   ├── aula-01-introducao.m        # Operacoes basicas em pixels
│   ├── aula-02-funcoes-gerais/     # Funcoes: negativo, RGB, histograma, recorte
│   ├── aula-03-filtros/            # Filtros de ruido, convolucao, deteccao de bordas
│   ├── aula-04-steganografia/      # Esteganografia em imagens BMP
│   └── aula-05-manipulacao/        # Morfologia, DCT, Wavelet (DWT)
│
├── simulado/                       # Exercicios de simulado em MATLAB
│
└── trabalho-gabarito/              # Trabalho final: corretor de gabarito (Python/Streamlit)
```

## Aulas (MATLAB)

| Aula | Conteudo |
|------|----------|
| 1 | Leitura de imagem, manipulacao de pixels, binarizacao, niveis de cinza |
| 2 | Funcoes gerais: negativo, conversao RGB, equalizacao de histograma, recorte |
| 3 | Filtros de ruido (mediana, media), convolucao, deteccao de bordas |
| 4 | Esteganografia: ocultacao e extracao de mensagem em imagem BMP |
| 5 | Morfologia matematica, transformada DCT e Wavelet (DWT) |

## Trabalho Final — Corretor de Gabarito

Aplicacao web que le a foto de uma folha de respostas (8 questoes, alternativas A-D) e calcula a nota do aluno. Suporta fotos tortas e com sombra via marcadores ArUco. Lê Nome/CPF/RG por OCR.

Ver [`trabalho-gabarito/README.md`](trabalho-gabarito/README.md) para instrucoes de execucao.

## Requisitos

- **Aulas e Simulado:** MATLAB (qualquer versao recente com Image Processing Toolbox)
- **Trabalho final:** Python 3.12+ ou Docker (ver README do trabalho)
