import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr

from motores_filosoficos import conversar_com_filosofo
from avaliador_cognitivo import analisar_turno_com_qwen

app = FastAPI(title="Motor Backend - FiloQuest")

# =====================================================================
# MODIFICAÇÃO DE CIBERSEGURANÇA: POLÍTICA ESTRITA DE CORS
# =====================================================================
# Modifique esta lista inserindo os domínios onde as IFs reais estarão publicadas.
# Isso impede que agentes externos abusem do consumo da sua cota computacional.
ORIGENS_PERMITIDAS = [
    "https://filoquest.uern.br",
    "https://educapes.capes.gov.br",
    "http://localhost:8080",      # Permitido para seus testes em localhost
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

class TurnoRequisicao(BaseModel):
    filosofo_atual: str
    mensagem_jogador: str
    historico: list

@app.post("/api/jogar_turno")
async def orquestrar_turno(req: TurnoRequisicao):
    try:
        resposta_ia = conversar_com_filosofo(req.filosofo_atual, req.historico)

        if "Erro na comunicação" in resposta_ia:
            raise HTTPException(status_code=502, detail=resposta_ia)

        avaliacao_estado = analisar_turno_com_qwen(req.mensagem_jogador, resposta_ia)

        return {
            "fala_filosofo": resposta_ia,
            "analise": avaliacao_estado
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print("\n[ERRO CRÍTICO NO BACKEND] O motor falhou. Rastreio:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")

# =====================================================================
# ADAPTAÇÃO COMPATÍVEL COM O GRADIO SPACES (HEALTH CHECK)
# =====================================================================
def interface_estatica():
    return "A infraestrutura do motor FiloQuest está operacional."

interface_fantasma = gr.Interface(
    fn=interface_estatica,
    inputs=None,
    outputs="text",
    title="FiloQuest Backend API",
    description="Interface operacional na nuvem. Tráfego externo aceito apenas via requisições HTTP POST controladas por CORS para o endpoint público: /api/jogar_turno."
)

app = gr.mount_gradio_app(app, interface_fantasma, path="/")