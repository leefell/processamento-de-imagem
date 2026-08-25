filtro1 = [-1 0 1; -2 0 2; -1 0 1];
filtro2 = [1 2 1; 0 0 0; -1 -2 -1];

img = imread('Aula1/Lena512.bmp');
imgF1 = conv2(filtro1, img);
imgF1 = uint8(imgF1);
imgF2 = conv2(filtro2, img);
imgF2 = uint8(imgF2);

figure(1), subplot(2,2,1), colormap(gray), imagesc(img), title('Imagem 1');
figure(1), subplot(2,2,3), colormap(gray), imagesc(imgF1), title('Imagem 2');
figure(1), subplot(2,2,4), colormap(gray), imagesc(imgF2), title('Imagem 3');

imwrite(imgF1, 'Aula3/Images_Out/imagemLenaBorrada.jpg');