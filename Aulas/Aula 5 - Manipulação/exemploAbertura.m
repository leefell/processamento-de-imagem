clc;

img = imread('Aula5/Images/imgAbertura.png');
img = rgb2gray(img);
SE = ones(3,3);
ghb
imgErode = imerode(img, SE);
imgAbertura = imdilate(imgErode, SE);

subplot(2,2,1);imshow(img),title('Imagem Original');
subplot(2,2,3); imshow(imgErode), title('Imagem Erodida');
subplot(2,2,4); imshow(imgContorno), title('Imagem Abertura');