clc;
clear;

imgTerra = imread("images/placa2terra.bmp");
imgCinza = rgb2gray(imgTerra);

[M, N] = size(imgCinza);

for i = 1:M
    for j = 1:N
        if imgCinza(i, j) > 50
            imgCinza(i, j) = 255;
        end
    end
end

imgErode = imerode(imgCinza, strel('disk', 1));
imgLimpa = imdilate(imgErode, strel('square', 8));

figure(1)
imshow(imgLimpa);
title('Processed Image');