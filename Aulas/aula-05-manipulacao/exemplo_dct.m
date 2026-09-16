clc;
clear all;

a = imread("Images/Lena512.bmp");
b = dct2(a);
b1 = uint8(b);
c = idct2(b);
c = uint8(c);

figure(1)
subplot(1,3,1);colormap(gray);imshow(a);
subplot(1,3,2);colormap(gray);imshow(b1);
subplot(1,3,3);colormap(gray);imshow(c);