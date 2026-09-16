clear;
clc;

imagemOriginal = imread("lenaRGB.png");
mensagemOriginal = imread("mensagem512.bmp");

imgR = imagemOriginal(:,:,1);
imgG = imagemOriginal(:,:,2);
imgB = imagemOriginal(:,:,3);

[m, n] = size(imgR);

imgR_marcado = imgR;

for i = 1:m
    for j = 1:n
        imgR_marcado(i,j) = bitset(imgR(i,j), 1, mensagemOriginal(i,j));
    end
end

imagemMarcada = cat(3, imgR_marcado, imgG, imgB);
imwrite(imagemMarcada, 'Resultados/marcadaAulaColorida.bmp');

% Lógica de extrair mensagem
imgMarcadaR = imagemMarcada(:,:,1);
mensagemExtraida = zeros(m,n);

for i = 1:m
    for j = 1:n
        mensagemExtraida(i,j) = bitget(imgMarcadaR(i,j), 1);
    end
end

mensagemExtraida = mensagemExtraida * 255;

figure(1);
subplot(2, 3, 1); imshow(imagemOriginal);  title('1. Imagem Original');
subplot(2, 3, 2); imshow(mensagemOriginal); title('2. Mensagem Original');
subplot(2, 3, 3); imshow(imagemMarcada);   title('3. Imagem com Mensagem Inserida');
subplot(2, 3, 4); imshow(imagemMarcada);   title('4. Imagem Marcada');
subplot(2, 3, 5); imshow(mensagemExtraida); title('5. Mensagem Extraída (Íntegra)');

% Lógica de adulteração da imagem
imagemAdulterada = imagemMarcada;

for i = 50:150
    for j = 50:150
        imagemAdulterada(i,j,:) = 0;
    end
end

imgAdulteradaR = imagemAdulterada(:,:,1);
mensagemAdulterada = zeros(m,n);

for i = 1:m
    for j = 1:n
        mensagemAdulterada(i,j) = bitget(imgAdulteradaR(i,j), 1);
    end
end

mensagemAdulterada = mensagemAdulterada * 255;

% Exibição do teste de adulteração
figure(2);
subplot(1, 2, 1);imshow(imagemAdulterada);title('Imagem Adulterada');
subplot(1, 2, 2);imshow(mensagemAdulterada);title('Mensagem Extraída (Adulterada)');