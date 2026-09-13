clear all;
clc; 

imgEscura = imread('/MATLAB Drive/Aula2/Escuro.bmp');

imgEq = histeq(imgEscura);

figure(1), imshow(imgEscura), title('Imagem Escura');
figure(2), imshow(imgEq), title('Imagem Escura Equalizada');
figure(3), imhist(imgEscura), title('Histograma da Imagem Original'); % mostrar histograma da imagem
figure(4), imhist(imgEq), title('Histograma da Imagem Equalizada');

%salvar em arquivo
imwrite(imgEq, 'AulaimagemEqualizadaAula.bmp');