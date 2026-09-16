clc;
clear;

img = imread("SimulacaoProva/images/moeda1.bmp");
imgGray = rgb2gray(img);

SE = ones(7,7);
imgErode = imerode(imgGray, SE);

imgContorno = imgGray - imgErode;

imgContorno(imgContorno < 100) = 0;

[M, N] = size(imgGray);
qtdMoedas = 0;

for i = 1:M
    for j = 1:N
        if imgContorno(i,j) > 0
            qtdMoedas = qtdMoedas + 1;
        end
    end
end

qtdMoedas = round(qtdMoedas / 640);

imshow(imgContorno);
fprintf('Quantidade de moedas detectadas: %d\n', qtdMoedas);