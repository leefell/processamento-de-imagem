clc;
clear;

img = imread("SimulacaoProva/images/marcadaTrabalho25.bmp");

[M, N] = size(img);

msg = zeros(M, N, 'uint8');

for i=1:M
    for j=1:N
        msg(i,j)=bitget(img(i,j),2);
    end
end

msg = 255 * msg;
subplot(2,2,1);imshow(img), title('Imagem Original');
subplot(2,2,2);imshow(msg), title('Mensagem Extraída');