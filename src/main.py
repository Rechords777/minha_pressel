import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # Adiciona o diretório pai ao path

from app.main import app

# Este arquivo serve como ponto de entrada para o serviço de deploy
# Ele importa e expõe a aplicação FastAPI do módulo app.main

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
