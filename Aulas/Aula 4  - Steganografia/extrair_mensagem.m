clear;
clc;

imagemMarcada = imread('marcada.bmp');

[M, N] = size(imagemMarcada);
mensagem = zeros(M, N);

for i = 1:M
    for j = 1:N
        mensagem(i, j) = bitget(imagemMarcada(i,j), 1);
    end
end

subplot(2,2,1);imshow(imagemMarcada), title('Imagem Com Mensagem Extraída');
subplot(2,2,2);imshow(mensagem), title('Mensagem Extraida');
