clear all;
clc; 

imgIF = imread('/MATLAB Drive/Aula2/if.jpg');

imgIFG = rgb2gray(imgIF);

imgMenor = imresize(imgIFG, 0.5); % redimensiona o tamanho da imagem

figure(1),imshow(imgIF), title('Imagem Colorida');
figure(2),imshow(imgIFG), title('Imagem Cinza');
figure(3),imshow(imgMenor), title('Imagem Cinza Redimensionada');

% usando a funcao subplot
% subplot(1 -> linha, 3 -> coluna, 1 -> posicao da imagem)

figure(4), subplot(1, 3, 1), imshow(imgIF), title('Imagem Colorida');
figure(4), subplot(1, 3, 2), imshow(imgIFG), title('Imagem Cinza');
figure(4), subplot(1, 3, 3), imshow(imgMenor), title('Imagem Cinza Redimensionada');

figure(5), subplot(1,2,1), colormap(gray), imagesc(imgMenor);
figure(5), subplot(1,2,2), imagesc(imgIF);
% colormap(gray)