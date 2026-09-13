imagem = imread('Aula5/Images/Lena512.bmp');
[cA, cH, cV, cD] = dwt2(imagem, 'haar');

% cA -> All, cH -> Horizontal, cV -> Vertical, cD -> Diagonal

figure(1) 
subplot(3,2,1), colormap("gray"), imagesc(imagem), title('Img Original');
subplot(3,2,3), colormap("gray"), imagesc(cA), title('cA');
subplot(3,2,4), colormap("gray"), imagesc(cH), title('cH');
subplot(3,2,5), colormap("gray"), imagesc(cV), title('cV');
subplot(3,2,6), colormap("gray"), imagesc(cD), title('cD');

imagemVolta = idwt2(cA, cH, cV, cD, 'haar');
imagemVolta = uint8(imagemVolta);
figure(2), imshow(imagemVolta);