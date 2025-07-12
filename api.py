import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Define o caminho para o arquivo de dados
RESULTS_FILE = os.path.join('output', 'results.json')

# Cria a instância da aplicação FastAPI
app = FastAPI(
    title="API de Resultados de Cassino",
    description="Fornece resultados em tempo real de jogos de cassino online.",
    version="1.0.0"
)

@app.get("/resultados/bacbo", tags=["Resultados"])
async def obter_resultados_bacbo():
    """
    Endpoint para obter os últimos resultados de Bac Bo.
    
    Os dados são atualizados em segundo plano por um script worker.
    """
    if not os.path.exists(RESULTS_FILE):
        raise HTTPException(
            status_code=404, 
            detail="Arquivo de resultados não encontrado. O worker pode não ter sido executado ainda."
        )
    
    try:
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        # Usar JSONResponse para garantir a correta formatação do content-type
        return JSONResponse(content=dados)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao ler o arquivo de resultados: {e}"
        )

# Endpoint raiz para um simples "Olá, Mundo"
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Bem-vindo à API de Resultados de Cassinos. Acesse /docs para a documentação."}