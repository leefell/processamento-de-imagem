clear all;
clc;

img = imread('images/lenaRGB.png');
imgGray = rgb2gray(img);

for i = 1:50
    for j = 1:100
        imgGray(i, j) = 127;
    end
end

[M, N] = size(imgGray);

% 2 niveis
imgGrayBin = imgGray;
for i = 1:M
    for j = 1:N
        if imgGrayBin(i, j) > 127
            imgGrayBin(i, j) = 255;
        else
            imgGrayBin(i, j) = 0;
        end
    end
end

% 4 niveis
imgGray4Bin = zeros(M, N, 'uint8');
for i = 1:M
    for j = 1:N
        if imgGray(i, j) <= 70
            imgGray4Bin(i, j) = 0;
        elseif imgGray(i, j) <= 140
            imgGray4Bin(i, j) = 100;
        elseif imgGray(i, j) <= 200
            imgGray4Bin(i, j) = 180;
        else
            imgGray4Bin(i, j) = 255;
        end
    end
end

% 8 niveis
imgGray8Bin = (imgGray / 32) * 32;

figure(1)
subplot(2,2,1), imshow(imgGray), title('Original')
subplot(2,2,2), imshow(imgGrayBin), title('Binarizada')
subplot(2,2,3), imshow(imgGray4Bin), title('4 Niveis de Cinza')
subplot(2,2,4), imshow(imgGray8Bin), title('8 Niveis de Cinza');