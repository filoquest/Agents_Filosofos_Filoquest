import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from google import genai

# Importando as lógicas dos seus arquivos
from motores_filosoficos import conversar_com_filosofo, PERSONAS_FILOSOFICAS
from avaliador_cognitivo import analisar_turno_com_qwen

app = FastAPI(title="Motor Agente FiloQuest API")

# Inicializa o cliente do Gemini para a função de escolha automática
client = genai.Client()

# Configuração de CORS
ORIGENS_PERMITIDAS = ["https://filoquest.uern.br", "https://educapes.capes.gov.br", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENS_PERMITIDAS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TurnoRequest(BaseModel):
    filosofo_atual: str
    mensagem_jogador: str
    historico: List[Dict[str, str]] = []


def selecionar_filosofo_automatico(mensagem_aluno: str) -> str:
    """
    IA Inteligente: Avalia a resposta do aluno e escolhe o filósofo que vai
    gerar o melhor embate ou contra-ponto ético para desafiar o pensamento dele.
    """
    prompt = (
        "Você é o orquestrador do jogo educativo 'O Gabarito'. Um aluno deu a seguinte justificativa "
        "para ter agido (ou não) em uma trapaça escolar com gabaritos:\n"
        f"'{mensagem_aluno}'\n\n"
        "Com base nisso, escolha qual filósofo seria o melhor debatedor para confrontar ou aprofundar "
        "o pensamento desse aluno:\n"
        "- 'kant' (Se o aluno foi muito egoísta, utilitarista ou focou nas consequências)\n"
        "- 'mill' (Se o aluno agiu por regras cegas, medo puro ou desconsiderou a felicidade geral)\n"
        "- 'aristoteles' (Se o aluno focou em amizade distorcida ou falta de virtude de caráter)\n\n"
        "Responda APENAS com a palavra chave em letras minúsculas: kant, mill ou aristoteles."
    )
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        escolha = response.text.strip().lower()
        if escolha in ['kant', 'mill', 'aristoteles']:
            return escolha
    except Exception as e:
        print(f"Erro na escolha automática: {e}")
    return "kant"  # Fallback de segurança


@app.post("/api/jogar_turno")
async def processar_turno(request: TurnoRequest):
    try:
        filosofo_escolhido = request.filosofo_atual

        # Se veio "auto" do Twine, a IA faz o julgamento e decide quem vai falar
        if filosofo_escolhido == "auto":
            filosofo_escolhido = selecionar_filosofo_automatico(request.mensagem_jogador)

        # 1. Pega o nome de exibição correto do filósofo (ex: "Immanuel Kant")
        nome_exibicao = PERSONAS_FILOSOFICAS[filosofo_escolhido]["nome"]

        # 2. Aciona o filósofo escolhido
        resposta_filosofo = conversar_com_filosofo(
            filosofo_escolhido,
            request.historico
        )

        # 3. Aciona o Avaliador Cognitivo
        analise_cognitiva = analisar_turno_com_qwen(
            request.mensagem_jogador,
            resposta_filosofo
        )

        # Devolvemos também o 'filosofo_nome' para o Twine atualizar a interface
        return {
            "fala_filosofo": resposta_filosofo,
            "filosofo_nome": nome_exibicao,
            "analise": {
                "perfil_cognitivo": analise_cognitiva.get("perfil_cognitivo", "indeterminado"),
                "proximo_estado": analise_cognitiva.get("proximo_estado", "manter_fase")
            }
        }

    except Exception as e:
        print(f"Erro no servidor: {str(e)}")
        return {
            "fala_filosofo": "Houve uma perturbação na linha de raciocínio. Os filósofos se retiraram.",
            "filosofo_nome": "Immanuel Kant",
            "analise": {"perfil_cognitivo": "indeterminado", "proximo_estado": "manter_fase"}
        }


@app.get("/")
def read_root():
    return {"status": "A academia filosófica está online."}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)