clear all;
clc; 

a = imread('Aula2/Images/Lena512.bmp');
b = imnoise(a, 'gaussian');
c = imnoise(a, 'gaussian', 0, 0.003);
d = imnoise(a, 'salt & pepper');
e = imnoise(a, 'salt & pepper', 0.005);
% subplot(1 -> linha, 3 -> coluna, 1 -> posicao da imagem)

figure(1), subplot(3,3,2), imshow(a), title('Imagem original');
figure(1), subplot(3,3,4), imshow(b), title('Imagem Gaussian');
figure(1), subplot(3,3,6), imshow(c), title('Imagem Guassian Variancia 0.003');
figure(1), subplot(3,3,7), imshow(d), title('Imagem Salt & Pepper');
figure(1), subplot(3,3,9), imshow(e), title('Imagem Salt & Pepper Variancia 0.005');