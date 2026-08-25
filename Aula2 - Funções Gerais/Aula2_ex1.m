clear all;
clc; 

imgLena = imread('/MATLAB Drive/Aula2/lena128.bmp');
imgCamera = imread('/MATLAB Drive/Aula2/cameraman128.bmp');
novaimagem = imgLena;

[M,N] = size(imgLena); 

for i = 1:M
    for j = 1:N
        novaimagem(i, N + j) = imgCamera(i, j);
    end
end

figure(1), imshow(novaimagem); title('Imagem ao lado');