FROM python:3.12-slim-bookworm

# Evita geração de bytecode .pyc e garante logs em tempo real no terminal
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Instala dependências do sistema operacional:
# - libglib2.0-0: suporte a bibliotecas de imagem / OpenCV headless
# - libgomp1: OpenMP runtime (essencial para o PyTorch CPU e processamento numérico)
# - fonts-dejavu-core: fontes DejaVu Sans usadas no desenho das folhas de respostas (gabarito/folha.py)
# - curl: utilizado no healthcheck do container
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    fonts-dejavu-core \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia e instala dependências Python em camada separada para aproveitar cache do Docker
COPY requirements.txt .

# Instala PyTorch em versão CPU (reduz a imagem em mais de 2GB evitando pacotes CUDA desnecessários)
# e em seguida instala as demais dependências do requirements.txt
RUN pip install --upgrade pip && \
    (pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu || pip install torch torchvision) && \
    pip install -r requirements.txt

# Pré-baixa os modelos do EasyOCR (idioma português) durante o build da imagem.
# Isso elimina o delay de 20-30s no primeiro uso e permite execução 100% offline.
RUN python -c "import easyocr; easyocr.Reader(['pt'], gpu=False)"

# Copia os arquivos do projeto para o container
COPY . /app

EXPOSE 8501

# Healthcheck usando o endpoint oficial de status do Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
