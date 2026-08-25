[filename, pathname] = uigetfile('Selecione a Imagem');
[img] = imread(filename);
img = rgb2gray(img);

imgSobel = edge(img, 'sobel');
imgCanny = edge(img, 'canny', 0.1);
imgRoberts = edge(img, 'roberts');
imgPrewitt = edge(img, 'prewitt');

imwrite(imgSobel, 'ImagemSobel.bmp');
imwrite(imgCanny, 'ImagemCanny.bmp');
imwrite(imgRoberts, 'ImagemRoberts.bmp');
imwrite(imgPrewitt, 'ImagemPrewitt.bmp');

figure(1),subplot(3,3,1), imshow(img), title('Imagem Original');
figure(1),subplot(3,3,2), imshow(imgSobel), title('Sobel Edge Detection');
figure(1),subplot(3,3,3), imshow(imgCanny), title('Canny Edge Detection');
figure(1),subplot(3,3,4), imshow(imgRoberts), title('Roberts Edge Detection');
figure(1),subplot(3,3,5), imshow(imgPrewitt), title('Prewitt Edge Detection');