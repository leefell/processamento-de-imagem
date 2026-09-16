clear;
clc;

% abrir imagem
marcadaRGB = imread("SimulacaoProva/images/marcadaRGB.bmp");

% separar as 3 bandas rgb da imagem
imgMsg = imread('marcadaRGB.bmp');
imgMsgR = imgMsg(:, :, 1);
imgMsgG = imgMsg(:, :, 2);
imgMsgB = imgMsg(:, :, 3);
[M, N] = size(imgMsgR);

mensagemR = zeros(M,N);
mensagemG = zeros(M,N);
mensagemB = zeros(M,N);

% extrair as mensagens inseridas em cada uma das bandas rgb
for i=1:M
    for j=1:N
        mensagemR(i,j)=bitget(imgMsgR(i,j),1);
        mensagemG(i,j)=bitget(imgMsgG(i,j),1);
        mensagemB(i,j)=bitget(imgMsgB(i,j),1);
    end
end

figure(1)
subplot(2,2,1);imshow(marcadaRGB), title('Imagem Com 3 Mensagens Escondidas')
subplot(2,2,2);imshow(mensagemR), title('Mensagem Escondida 1 na banda R')
subplot(2,2,3);imshow(mensagemG), title('Mensagem Escondida 2 na banda G')
subplot(2,2,4);imshow(mensagemB), title('Mensagem Escondida 3 na banda B');