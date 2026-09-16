img = imread('Images/Lena512.bmp');
imgBw = im2bw(img);

%SE = [1 1 1; 1 1 1; 1 1 1];%3x3
SE = ones(3,3); % Elemento estruturante => matrix 3x3

imgErode = imerode(imgBw, SE);

subplot(2,3,2);imshow(img), title('Imagem Original');
subplot(2,3,4);imshow(imgBw), title('Imagem PB');
subplot(2,3,6);imshow(imgErode), title('Imagem Com Erosao');