import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn

# Supondo que você tenha os arquivos com as lógicas separadas
from motores_filosoficos import consultar_filosofo
from avaliador_cognitivo import analisar_maturidade

app = FastAPI(title="Motor Agente FiloQuest API")

# --- CONFIGURAÇÃO DE SEGURANÇA (CORS) ---
# Permite que o seu Twine acesse a API.
# Adicione a URL do seu jogo publicado quando ele estiver pronto.
ORIGENS_PERMITIDAS = [
    "https://filoquest.uern.br",
    "https://educapes.capes.gov.br",
    "https://filoquest.uern.br/O_Gabarito_Jogo.html",
    "*"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- MODELOS DE DADOS (Pydantic) ---
# Define exatamente o formato que o Twine deve enviar
class TurnoRequest(BaseModel):
    filosofo_atual: str
    mensagem_jogador: str
    historico: List[Dict[str, str]] = []


# --- ROTA PRINCIPAL DA API ---
@app.post("/api/jogar_turno")
async def processar_turno(request: TurnoRequest):
    try:
        # 1. Aciona o LLM (ex: Llama 3) para incorporar o filósofo escolhido
        resposta_filosofo = consultar_filosofo(
            request.filosofo_atual,
            request.mensagem_jogador,
            request.historico
        )

        # 2. Aciona o LLM Avaliador (ex: Qwen) para dar a nota cognitiva
        analise_cognitiva = analisar_maturidade(
            request.mensagem_jogador,
            request.historico
        )

        # 3. Empacota tudo e devolve para o Twine
        return {
            "fala_filosofo": resposta_filosofo,
            "analise": {
                "perfil_cognitivo": analise_cognitiva.get("perfil", "indeterminado"),
                "proximo_estado": analise_cognitiva.get("estado", "manter_fase")
            }
        }

    except Exception as e:
        print(f"Erro no servidor: {str(e)}")
        return {
            "fala_filosofo": "Houve uma perturbação na linha de raciocínio. Os filósofos não puderam responder.",
            "analise": {
                "perfil_cognitivo": "indeterminado",
                "proximo_estado": "manter_fase"
            }
        }


# Rota simples apenas para verificar se a API está "acordada"
@app.get("/")
def read_root():
    return {"status": "A academia filosófica está online."}


# O Render precisa disso para iniciar o servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)