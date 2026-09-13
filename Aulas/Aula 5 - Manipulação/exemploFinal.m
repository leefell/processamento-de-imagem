img = imread('Aula5/Images/imgDigitalRuido.png');

imgBW = im2bw(img);
img = imgBW;

SE = ones(3,3);

imgErode = imerode(img,SE);
imgAbertura = imdilate(imgErode,SE);
imgDilateFinal = imdilate(imgAbertura,SE);
imgFinal = imerode(imgDilateFinal,SE);

subplot(2,2,1); imshow(img), title('Imagem Original');
subplot(2,2,2); imshow(imgErode), title('Imagem Erosão');
subplot(2,2,3); imshow(imgAbertura), title('Imagem Abertura');
subplot(2,2,4); imshow(imgFinal), title('Imagem Fechamento');