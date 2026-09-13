clear;
clc;

a = imread('Aula5/Images/Lena512.bmp');
b = dct2(a);

b(1,1) = b(1,1) * 0.0005;
b(1,2) = b(1,2) * 0.0005;
b(1,3) = b(1,3) * 0.0005;
b(1,4) = b(1,4) * 0.0005;

c = idct2(b);
corr2(a,c) % Correlação deu 95, então alterando apenas 4 pixels ja mudou

figure(1)
subplot(1,3,1);colormap("gray");imagesc(a);
subplot(1,3,2);colormap("gray");imagesc(b);
subplot(1,3,3);colormap("gray");imagesc(c);