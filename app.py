import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr

# Importação dos nossos módulos lógicos locais
from motores_filosoficos import conversar_com_filosofo
from avaliador_cognitivo import analisar_turno_com_qwen

# Instanciação do Motor Principal
app = FastAPI(title="Motor Backend - FiloQuest")

# Configuração de CORS (Cross-Origin Resource Sharing)
# Permite que o Twine (que roda no navegador do cliente) comunique com esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Estrutura de Tipagem Forte do Payload
class TurnoRequisicao(BaseModel):
    filosofo_atual: str
    mensagem_jogador: str
    historico: list


# Rota Principal de Jogo (Onde o Twine faz o POST)
@app.post("/api/jogar_turno")
async def orquestrar_turno(req: TurnoRequisicao):
    try:
        # 1. Inferência da Persona Filosófica (Llama 3.1)
        resposta_ia = conversar_com_filosofo(req.filosofo_atual, req.historico)

        if "Erro na comunicação" in resposta_ia:
            raise HTTPException(status_code=502, detail=resposta_ia)

        # 2. Análise Cognitiva e Máquina de Estados (Qwen 2.5)
        avaliacao_estado = analisar_turno_com_qwen(req.mensagem_jogador, resposta_ia)

        # 3. Retorno do Pacote Unificado para o Frontend (Twine)
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
# ADAPTAÇÃO PARA O HUGGING FACE GRADIO SPACE (CAMADA GRATUITA)
# =====================================================================

def interface_estatica():
    return "A infraestrutura do motor FiloQuest está operacional."


# 1. Criamos uma interface visual inerte apenas para o "health check" da plataforma Hugging Face
interface_fantasma = gr.Interface(
    fn=interface_estatica,
    inputs=None,
    outputs="text",
    title="FiloQuest Backend API",
    description="Esta interface serve estritamente para manter o serviço ativo na nuvem. O tráfego do jogo ocorre através de requisições HTTP POST invisíveis para o endpoint estrito: /api/jogar_turno."
)

# 2. Acoplamos (mount) a nossa verdadeira API (FastAPI) na raiz da interface do Gradio
app = gr.mount_gradio_app(app, interface_fantasma, path="/")