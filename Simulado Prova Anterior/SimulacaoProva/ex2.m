clc;
clear;

img1 = imread("SimulacaoProva/images/placa1.bmp");
img2 = imread("SimulacaoProva/images/placa2.bmp");
img3 = imread("SimulacaoProva/images/placa3.bmp");
img4 = imread("SimulacaoProva/images/placa4.bmp");
img5 = imread("SimulacaoProva/images/placa5.bmp");

img1 = rgb2gray(img1);
img2 = rgb2gray(img2);
img3 = rgb2gray(img3);
img4 = rgb2gray(img4);
img5 = rgb2gray(img5);

img1Resized = imresize(img1, 0.15);
img2Resized = imresize(img2, 0.15);
img3Resized = imresize(img3, 0.15);
img4Resized = imresize(img4, 0.15);
img5Resized = imresize(img5, 0.15);

figure(1)
subplot(2, 3, 1), imshow(img1), title('Image 1');
subplot(2, 3, 2), imshow(img2), title('Image 2');
subplot(2, 3, 3), imshow(img3), title('Image 3');
subplot(2, 3, 4), imshow(img4), title('Image 4');
subplot(2, 3, 5), imshow(img5), title('Image 5');

figure(2)
subplot(2, 3, 1), imshow(img1Resized), title('Resized Image 1');
subplot(2, 3, 2), imshow(img2Resized), title('Resized Image 2');
subplot(2, 3, 3), imshow(img3Resized), title('Resized Image 3');
subplot(2, 3, 4), imshow(img4Resized), title('Resized Image 4');
subplot(2, 3, 5), imshow(img5Resized), title('Resized Image 5');

imwrite(img1Resized, 'ResizedImage1.bmp');
imwrite(img2Resized, 'ResizedImage2.bmp');
imwrite(img3Resized, 'ResizedImage3.bmp');
imwrite(img4Resized, 'ResizedImage4.bmp');
imwrite(img5Resized, 'ResizedImage5.bmp');