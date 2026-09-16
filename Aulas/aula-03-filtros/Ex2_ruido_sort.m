clc
clear

imagem = imread('Images/imgRuido.png');

[M, N] = size(imagem);
c = imagem;
c = double(c);

% Usando sort
for i = 2 : M - 1
    for j = 2: N - 1
        filtroc(i, j) = [((c(i-1, j-1)) + (c(i-1, j)) + + (c(i-1, j + 1)) ...
            + (c(i, j - 1)) + (c(i, j)) + (c(i, j+1)) ...
            + (c(i+1, j-1))) + (c(i+1, j)) + (c(i-1, j+1))];
        vetc = reshape(filtroc, 1,9);
        vetco = sort(vetc);
        c(i,j) = vetco(5);
    end
end

c = uint8(c);

figure(1),subplot(1,2,1),imshow(imagem);
figure(1),subplot(1,2,2),imshow(c);

imwrite(c, 'ifmedia.bmp');
