clear;
clc;

imgMsg = imread('marcadaAulaColorida.bmp');
imgMsgR = imgMsg(:, :, 1);
imgMsgG = imgMsg(:, :, 2);
imgMsgB = imgMsg(:, :, 3);
[M, N] = size(imgMsgR);

for i=1:M
    for j=1:N
        msg(i,j)=bitget(imgMsgR(i,j),1);
    end
end


msg = 255 * msg;
subplot(2,2,1);imshow(imgMsg), title('Imagem Com Mensagem Extraída');
subplot(2,2,2);imshow(msg), title('Mensagem Extraida');
