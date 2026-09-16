clear;
clc;

% importa
imagemOriginal = imread("lenaRGB.png");
mensagem1 = imread("Mensagem1RGB.bmp");
mensagem2 = imread("Mensagem2RGB.bmp");
mensagem3 = imread("Mensagem3RGB.bmp");

% divide as bandas
imgR = imagemOriginal(:,:,1);
imgG = imagemOriginal(:,:,2);
imgB = imagemOriginal(:,:,3);

[m, n] = size(imgR);

imgR_marcado = imgR;
imgG_marcado = imgG;
imgB_marcado = imgB;

for i = 1:m
    for j = 1:n
        imgR_marcado(i,j) = bitset(imgR(i,j), 1, mensagem1(i,j)); 
        imgG_marcado(i,j) = bitset(imgG(i,j), 1, mensagem2(i,j)); 
        imgB_marcado(i,j) = bitset(imgB(i,j), 1, mensagem3(i,j)); 
    end
end

imagemMarcada = cat(3, imgR_marcado, imgG_marcado, imgB_marcado);
imwrite(imagemMarcada, 'Resultados/marcadaRGB.bmp');

imgMarcadaR = imagemMarcada(:,:,1);
imgMarcadaG = imagemMarcada(:,:,2);
imgMarcadaB = imagemMarcada(:,:,3);

mensagemExtraida1 = zeros(m, n);
mensagemExtraida2 = zeros(m, n);
mensagemExtraida3 = zeros(m, n);

for i = 1:m
    for j = 1:n
        mensagemExtraida1(i,j) = bitget(imgMarcadaR(i,j), 1);
        mensagemExtraida2(i,j) = bitget(imgMarcadaG(i,j), 1);
        mensagemExtraida3(i,j) = bitget(imgMarcadaB(i,j), 1);
    end
end

mensagemExtraida1 = mensagemExtraida1 * 255;
mensagemExtraida2 = mensagemExtraida2 * 255;
mensagemExtraida3 = mensagemExtraida3 * 255;

% adulterando
imagemAdulterada = imagemMarcada;

for i = 50:150
    for j = 50:150
        imagemAdulterada(i,j,:) = 0; % quadrado preto em todos as bandas
    end
end

imgAdulteradaR = imagemAdulterada(:,:,1);
imgAdulteradaG = imagemAdulterada(:,:,2);
imgAdulteradaB = imagemAdulterada(:,:,3);

msgAdulterada1 = zeros(m, n);
msgAdulterada2 = zeros(m, n);
msgAdulterada3 = zeros(m, n);

for i = 1:m
    for j = 1:n
        msgAdulterada1(i,j) = bitget(imgAdulteradaR(i,j), 1);
        msgAdulterada2(i,j) = bitget(imgAdulteradaG(i,j), 1);
        msgAdulterada3(i,j) = bitget(imgAdulteradaB(i,j), 1);
    end
end

msgAdulterada1 = msgAdulterada1 * 255;
msgAdulterada2 = msgAdulterada2 * 255;
msgAdulterada3 = msgAdulterada3 * 255;

% imagem original e as 3 mensagens originais
figure(1);
subplot(2, 2, 1); imshow(imagemOriginal);title('Imagem Original');
subplot(2, 2, 2); imshow(mensagem1);title('Mensagem 1 Original (R)');
subplot(2, 2, 3); imshow(mensagem2);title('Mensagem 2 Original (G)');
subplot(2, 2, 4); imshow(mensagem3);title('Mensagem 3 Original (B)');

% imagem com as 3 mensagens inseridas e as mensagens extraídas
figure(2);
subplot(2, 2, 1); imshow(imagemMarcada);title('Imagem Marcada (3 Bandas)');
subplot(2, 2, 2); imshow(mensagemExtraida1);title('Mensagem 1 Extraída (R)');
subplot(2, 2, 3); imshow(mensagemExtraida2);title('Mensagem 2 Extraída (G)');
subplot(2, 2, 4); imshow(mensagemExtraida3);title('Mensagem 3 Extraída (B)');

% adulteração e impacto nas 3 mensagens
figure(3);
subplot(2, 2, 1);imshow(imagemAdulterada);title('Imagem Adulterada');
subplot(2, 2, 2);imshow(msgAdulterada1);title('Msg 1 Extraída (Adulterada)');
subplot(2, 2, 3);imshow(msgAdulterada2);title('Msg 2 Extraída (Adulterada)');
subplot(2, 2, 4);imshow(msgAdulterada3);title('Msg 3 Extraída (Adulterada)');
