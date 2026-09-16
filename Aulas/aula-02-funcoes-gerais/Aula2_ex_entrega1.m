clc
clear

a = imread('Images/lena128.bmp');
b = imread('Images/cameraman128.bmp');

nova = zeros(256,128);
nova = uint8(nova);

for i = 1:128
    for j = 1:128
        nova(i,j) = a(i,j);          
        nova(i+128,j) = b(i,j);      
    end
end

figure(1), imshow(nova);