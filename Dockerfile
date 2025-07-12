# Estágio de construção (build)
FROM python:3.10-slim as builder

# Define o diretório de trabalho
WORKDIR /app

# Instala o Playwright e suas dependências
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev && \
    pip install --no-cache-dir --upgrade pip

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps

# Estágio final da API
FROM python:3.10-slim as api

WORKDIR /app

# Copia as dependências e o código da API
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY api.py .
COPY output/ /app/output

# Expõe a porta que a API vai usar
EXPOSE 8000

# Comando para iniciar a API
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# Estágio final do Worker
FROM python:3.10-slim as worker

WORKDIR /app

# Copia as dependências e o código do worker
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /root/.cache/ms-playwright/ /root/.cache/ms-playwright/
COPY scrapers/background_worker.py .
COPY output/ /app/output

# Comando para iniciar o worker
CMD ["python", "background_worker.py"]
