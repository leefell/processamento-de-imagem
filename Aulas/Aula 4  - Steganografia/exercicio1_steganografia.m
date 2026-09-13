clear;
clc;

imagemOriginalLena = imread('lenaRGB.png');
imgR = imagemOriginalLena(:, :, 1);
imgG = imagemOriginalLena(:, :, 2);
imgB = imagemOriginalLena(:, :, 3);

mensagemOculta = imread('mensagem512.bmp');

[M, N] = size(imgR);
imgComMensagem = imgR;

for i = 1:M
    for j = 1:N
        imgComMensagem(i, j) = bitset(imgR(i,j), 1 , mensagemOculta(i,j));
    end
end

imgJunto = cat(3, mensagemOculta, imgG, imgB);
imwrite(imgJunto, 'marcadaAulaColorida.bmp');
subplot(2,2,1);imshow(imagemOriginalLena), title('Imagem Original');
subplot(2,2,2);imshow(mensagemOculta), title('Mensagem Original');
subplot(2,2,3);imshow(imgJunto), title('Imagem com Mensagem Inserida');

