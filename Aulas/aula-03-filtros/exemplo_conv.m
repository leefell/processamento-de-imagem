clear
clc

img = imread("Images/imgRuido.png");
filtro = [1,1,1;1,1,1;1,1,1];
filtro = filtro/9;

imgSuavizada = conv2(filtro, img);
imgSuavizada = uint8(imgSuavizada);

figure(1),subplot(1,2,1),imshow(img);
figure(1),subplot(1,2,2),imshow(imgSuavizada);