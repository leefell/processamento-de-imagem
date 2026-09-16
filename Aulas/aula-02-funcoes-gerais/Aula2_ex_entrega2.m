clc 
clear

imgRGB = imread('Images/fotoIF.jpg');

imgR = imgRGB(:,:,1);
imgG = imgRGB(:,:,2);
imgB = imgRGB(:,:,3);

imgRedClara = imgR;
imgGreenClara = imgG; 
imgBlueClara = imgB;

[M, N, C] = size(imgRGB);

for i = 1:M
    for j = 1:N
        imgRedClara(i,j) = imgR(i,j) + 100;
        imgGreenClara(i,j) = imgG(i,j) + 100;
        imgBlueClara(i,j) = imgB(i,j) + 100;
    end
end

imgRGB1 = cat(3, imgRedClara, imgGreenClara, imgBlueClara);
imgRGBRAlterado = cat(3, imgRedClara, imgG, imgB);
imgRGBGAlterado = cat(3, imgR, imgGreenClara, imgB);
imgRGBBAlterado = cat(3, imgR, imgG, imgBlueClara);

figure(1), subplot(3,4,1), imshow(imgRGB), title('Imagem Original');
figure(1), subplot(3,4,2), imshow(imgR), title('Imagem R');
figure(1), subplot(3,4,3), imshow(imgG), title('Imagem G');
figure(1), subplot(3,4,4), imshow(imgB), title('Imagem B');

figure(1), subplot(3,4,5), imshow(imgRedClara), title('Imagem R Clara');
figure(1), subplot(3,4,6), imshow(imgGreenClara), title('Imagem G Clara');
figure(1), subplot(3,4,7), imshow(imgBlueClara), title('Imagem B Clara');

figure(1), subplot(3,4,8), imshow(imgRGB1), title('Imagem RGB Nova');
figure(1), subplot(3,4,9), imshow(imgRGBRAlterado), title('Imagem RGB R Alterado');
figure(1), subplot(3,4,10), imshow(imgRGBGAlterado), title('Imagem RGB G Alterado');
figure(1), subplot(3,4,11), imshow(imgRGBBAlterado), title('Imagem RGB B Alterado');