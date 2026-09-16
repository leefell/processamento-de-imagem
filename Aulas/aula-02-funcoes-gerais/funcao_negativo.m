clear all;
clc; 

a = imread('Images/Lena512.bmp');
b = imcomplement(a);

figure(1), subplot(1,2,1), title('Imagem Original'), imshow(a);
figure(1), subplot(1,2,2), title('Imagem Negativo'), imshow(b);

imwrite(b, 'lenaNegativo.bmp');