clear;
clc;

imagem = imread('Images/Lena512.bmp');

[cA1, cH1, cV1, cD1] = dwt2(imagem, 'haar');
[cA2, cH2, cV2, cD2] = dwt2(cA1, 'haar');

cA1_rec = idwt2(cA2, cH2, cV2, cD2, 'haar');
imagemVolta = idwt2(cA1_rec, cH1, cV1, cD1, 'haar');
imagemVolta = uint8(imagemVolta);

figure(1);
subplot(3,4,1), colormap("gray"), imagesc(imagem), title('Img Original');
subplot(3,4,2), colormap("gray"), imagesc(imagemVolta), title('Img Reconstruida');

subplot(3,4,5), colormap("gray"), imagesc(cA1), title('cA1');
subplot(3,4,6), colormap("gray"), imagesc(cH1), title('cH1');
subplot(3,4,7), colormap("gray"), imagesc(cV1), title('cV1');
subplot(3,4,8), colormap("gray"), imagesc(cD1), title('cD1');

subplot(3,4,9), colormap("gray"), imagesc(cA2), title('cA2');
subplot(3,4,10), colormap("gray"), imagesc(cH2), title('cH2');
subplot(3,4,11), colormap("gray"), imagesc(cV2), title('cV2');
subplot(3,4,12), colormap("gray"), imagesc(cD2), title('cD2');

figure(2);
imshow(imagemVolta);
title('Imagem Reconstruida');
