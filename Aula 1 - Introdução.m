1) Abrir uma imagem 
Fazer um quadrado preto na imagem de tamanho 35 largura X 55 altura;
clear all; 
clc; 

img = imread('Lena512.bmp');

imgquad = img;

% Esse exerício é pra aprender a trabalhar com pixel
% Fazer um quadrado preto na imaem de tamanho 35 largura X
% 55 altura;
for i = 1:55
    for j = 1:35
        imgquad(i, j) = 0;
    end
end

figure(1),imshow(img);
figure(2),imshow(imgquad);

2) Deixar a imagem mais clara;
   Deixar a imagem mais escura;
clear all; 
clc; 

img = imread('Lena512.bmp');

imgclara = img;
imgescura = img;

for i = 1:512
    for j = 1:512
        imgclara(i, j) = img(i,j) + 50;
        imgescura(i, j) = img(i,j) - 50;
    end
end

figure(1),imshow(imgclara);
figure(2),imshow(imgescura);

3) Binarizar a imagem
clear all; 
clc; 

img = imread('Lena512.bmp');

imgpretaebranca = img;

[M, N] = size(img)

for i = 1:M
    for j = 1:N
        if imgpretaebranca(i, j) > 127
            imgpretaebranca(i, j) = 255;
        else
            imgpretaebranca(i, j) = 0;
        end
    end
end

figure(1),imshow(imgpretaebranca);

4) Deixar a imagem com 4 níveis de cinza;

clear all; 
clc; 

img = imread('Lena512.bmp');
[M, N] = size(img)
img4 = zeros(M, N); %cria uma matriz toda zerada para manipular os zeros
img4 = uint8(img4);


for i = 1:M
    for j = 1:N
        if img(i, j) <= 70
            img4(i,j) = 0;
        elseif img(i,j) <= 140
            img4(i,j) = 100;
        elseif img(i,j) <= 200
            img4(i,j) = 180;
        else
            img4(i,j) = 255;
        end
    end
end

imshow(img);
figure(2),imshow(img4);

5) Deixar a imagem com 8 níveis de cinza;
% Alternativo 8 tons cinzas

img = imread('Lena512.bmp')

img8 = img/32
img8 = img8*32;

figure(1),imshow(img);
figure(2),imshow(img8);

6) Inserir a imagem IF30.bmp no canto da imagem Lena512.bmp;
clear all; 
clc; 

fundo = imread('Lena512.bmp');
logo = imread('if30.bmp');
[M, N] = size(logo)
novaimagem = fundo;

for i = 1:M
    for j = 1:N
        novaimagem(i,j) = logo(i,j);
    end
end

figure(1), imshow(novaimagem); title('Imagem com logo');
figure(2), imshow(logo); title('Logo');
figure(3), imshow(fundo); title('Imagem de fundo');
