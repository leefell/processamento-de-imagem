clc;
clear;

imagemRuido = imread("images/imgRuido.png");

filtro = [1,1,1,1,1;
          1,1,1,1,1;
          1,1,1,1,1;
          1,1,1,1,1;
          1,1,1,1,1];

filtro = filtro / 25;

imgSuavizada = conv2(filtro, imagemRuido);
imgSuavizada = uint8(imgSuavizada);

figure(1),subplot(1,2,1),imshow(imagemRuido),title('Imagem Original');
figure(1),subplot(1,2,2),imshow(imgSuavizada),title('Imagem Suavizada');