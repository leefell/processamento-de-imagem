clc 
clear

imgRGB = imread('Images/fotoIF.jpg');

% separa 
imgR = imgRGB(:,:,1);
imgG = imgRGB(:,:,2);
imgB = imgRGB(:,:,3);

% junta
imgRGB1 = cat(3, imgR, imgG, imgB);

figure(1), subplot(2,2,1), imshow(imgRGB);
figure(1), subplot(2,2,2), imshow(imgR);
figure(1), subplot(2,2,3), imshow(imgG);
figure(1), subplot(2,2,4), imshow(imgB);

figure(2), title('Imagem RGB Nova'), imshow(imgRGB1);