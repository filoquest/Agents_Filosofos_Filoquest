import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import uvicorn

# Importando os nomes reais das funções conforme os seus arquivos
from motores_filosoficos import conversar_com_filosofo
from avaliador_cognitivo import analisar_turno_com_qwen

app = FastAPI(title="Motor Agente FiloQuest API")

# --- CONFIGURAÇÃO DE SEGURANÇA (CORS) ---
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
class TurnoRequest(BaseModel):
    filosofo_atual: str
    mensagem_jogador: str
    historico: List[Dict[str, str]] = []

# --- ROTA PRINCIPAL DA API ---
@app.post("/api/jogar_turno")
async def processar_turno(request: TurnoRequest):
    try:
        # 1. Aciona o LLM (ex: Llama 3) usando o nome real da função
        # O Twine já envia a mensagem do jogador embutida no histórico
        resposta_filosofo = conversar_com_filosofo(
            request.filosofo_atual,
            request.historico
        )

        # 2. Aciona o LLM Avaliador (ex: Qwen) usando o nome real da função
        analise_cognitiva = analisar_turno_com_qwen(
            request.mensagem_jogador,
            resposta_filosofo
        )

        # 3. Empacota tudo e devolve para o Twine (Buscando as chaves corretas do Qwen)
        return {
            "fala_filosofo": resposta_filosofo,
            "analise": {
                "perfil_cognitivo": analise_cognitiva.get("perfil_cognitivo", "indeterminado"),
                "proximo_estado": analise_cognitiva.get("proximo_estado", "manter_fase")
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

# Rota simples para verificar o status da API no navegador
@app.get("/")
def read_root():
    return {"status": "A academia filosófica está online."}

# O Render precisa disso para iniciar o servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)