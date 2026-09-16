clc
clear

imagem = imread('Images/imgRuido.png');

[M, N] = size(imagem);
c = imagem;
c = double(c);

% Forma de programar o filtro sem usar a função pronta
for i = 2 : M - 1
    for j = 2: N - 1
        c(i, j) = [((1 * (c(i-1, j-1))) + (1 * (c(i-1, j))) + + (1 * (c(i-1, j + 1))) ...
                + (1 * (c(i, j - 1))) + (1 * (c(i, j))) + (1 * (c(i, j+1))) ...
                + (1 * (c(i+1, j-1))) + (1 * (c(i+1, j))) + (1 * (c(i-1, j+1))))/9];
    end
end

c = uint8(c);

figure(1),subplot(1,2,1),imshow(imagem);
figure(1),subplot(1,2,2),imshow(c);

imwrite(c, 'ifmedia.bmp');
