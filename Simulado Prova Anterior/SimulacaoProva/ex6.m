clc;
clear;

lenaRGB = imread("SimulacaoProva/images/lenaRGB.png");

imgR = lenaRGB(:, :, 1);
imgG = lenaRGB(:, :, 2);
imgB = lenaRGB(:, :, 3);

msg1 = imread("SimulacaoProva/mensagens/msgEscondida1.png");
msg2 = imread("SimulacaoProva/mensagens/msgEscondida2.png");
msg3 = imread("SimulacaoProva/mensagens/msgEscondida3.png");

imgRMsg = imgR;
imgGMsg = imgG;
imgBMsg = imgB;

[M, N] = size(imgR);

for i = 1:M
    for j = 1:N
        imgRMsg(i, j) = bitset(imgRMsg(i,j), 1, msg1(i,j));
        imgGMsg(i, j) = bitset(imgGMsg(i,j), 1, msg2(i,j));
        imgBMsg(i, j) = bitset(imgBMsg(i,j), 1, msg3(i,j));
    end
end


imgComMsgR = cat(3, imgRMsg, imgG, imgB);
imgComMsgG = cat(3, imgR, imgGMsg, imgB);
imgComMsgB = cat(3, imgR, imgG, imgBMsg);

marcadaRGB = cat(3, imgRMsg, imgGMsg, imgBMsg);

imwrite(marcadaRGB, 'marcadaRGB.bmp');

figure;
subplot(3, 3, 2), imshow(lenaRGB), title('Original Image');
subplot(3, 3, 4), imshow(imgComMsgR), title('Banda R com mensagem escondida');
subplot(3, 3, 5), imshow(imgComMsgG), title('Banda G com mensagem escondida');
subplot(3, 3, 6), imshow(imgComMsgB), title('Banda B com mensagem escondida');
subplot(3, 3, 8), imshow(marcadaRGB), title('Imagem RGB com 3 mensagens escondidas');
