clear all;
clc;

img1 = imread('Aula5/Images/cameraman128.bmp');
imwrite(img1, 'Aula5/Images/cameraman128_70.jpg', quality = 10);
img3 = imread('Aula5/Images/cameraman128_70.jpg');

semelhanca1_3 = corr2(img1, img3);
figure(1)
subplot(1,2,1), imshow(img1), title("Imagem original");
subplot(1,2,2), imshow(img3), title("Imagem Comprimida");