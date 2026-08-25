% ESTEGANOGRAFIA (Substituição de LSB)
% Conceito: Ocultar uma mensagem binária no bit menos significativo (LSB) dos pixels.
% A imagem contendo a mensagem deve ter valores apenas 0 (falso) ou 1 (verdadeiro).
% Se a mensagem for 0, garantimos que o LSB do pixel seja 0 (número par).
% Se a mensagem for 1, garantimos que o LSB do pixel seja 1 (número ímpar).
% Como a variação no pixel é de no máximo 1 unidade, a mudança visual é imperceptível.

% Regra prática de paridade:
% Mensagem = 0 -> Pixel deve ser PAR
% Mensagem = 1 -> Pixel deve ser ÍMPAR
%
% Se o pixel já estiver correto, mantém. 
% Se estiver errado, soma (ou subtrai) 1 no valor do pixel.

% Pra descobrir a mensagem tem que descobrir o LSB de cada pixel da imagem com a mensagem
% e assim compor a mensagem, pega o ultimo bit de cada numero e poe numa
% matriz na mesma posição 

% Fazer codigo de steganografia -> questão de prova
% colocar uma matriz com 9 números e vendo o lsb gerando a imagem -> questã
% o de prova

clear;
clc;

imagemOriginal = imread('lena128.bmp');
mensagemOculta = imread('mensagem.bmp');

[M, N] = size(imagemOriginal);
imgComMensagem = imagemOriginal;

for i = 1:M
    for j = 1:N
        imgMensagem(i, j) = bitset(imagemOriginal(i,j), 1 , mensagemOculta(i,j));
    end
end

% lsb(origem, lsb esquerda (ai vai
% do numero, 1 é o primeiro..), mensagem);

imwrite(imgMensagem, 'marcada.bmp');
subplot(2,2,1);imshow(imagemOriginal), title('Imagem Original');
subplot(2,2,2);imshow(mensagemOculta), title('Mensagem Oculta');
subplot(2,2,3);imshow(imgMensagem), title('Imagem com Mensagem');
