clc;

img = imread('Aula5/Images/if.jpg');
img = rgb2gray(img);

SE = ones(7,7);

imgErode = imerode(img, SE);
imgContorno = img - imgErode;

subplot(1,3,1);imshow(img),title('Imagem Original');
subplot(1,3,2); imshow(imgErode), title('Imagem Erodida');
subplot(1,3,3); imshow(imgContorno), title('Contorno da Imagem');