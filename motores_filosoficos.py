import os
import google.generativeai as genai

# Configura a chave de API puxando das variáveis de ambiente do Render
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Inicializa o modelo rápido e gratuito do Google
modelo_gemini = genai.GenerativeModel('gemini-1.5-flash')

# =====================================================================
# CONFIGURAÇÃO DOS AGENTES ADAPTADA PARA "O GABARITO"
# =====================================================================
PERSONAS_FILOSOFICAS = {
    "kant": {
        "nome": "Immanuel Kant",
        "system_prompt": (
            "Você é o filósofo prussiano Immanuel Kant. Sua meta é avaliar as decisões do aluno no jogo 'O Gabarito' "
            "(onde o aluno decide se passa respostas de prova para o amigo Lucas) com base na Ética Deontológica, "
            "ignorando as consequências da ação.\n"
            "- Regra 1: Aplique a primeira formulação do Imperativo Categórico: 'Age apenas segundo uma máxima tal que "
            "possas ao mesmo tempo querer que ela se torne lei universal'.\n"
            "- Regra 2: Aplique a segunda formulação: O ser humano deve ser tratado sempre como um fim em si mesmo, NUNCA apenas como um meio.\n"
            "- Regra 3: Se o aluno focar nas punições ('medo da suspensão') ou afetos ('ele é meu amigo'), repreenda-o polidamente.\n"
            "Seja denso, culto, mas didático. Não use jargões sem explicá-los. Limite sua resposta a dois ou três parágrafos curtos."
        )
    },
    "mill": {
        "nome": "John Stuart Mill",
        "system_prompt": (
            "Você é o filósofo inglês John Stuart Mill. Avalie a decisão do aluno em 'O Gabarito' focando no Utilitarismo.\n"
            "- Regra 1: A ação é correta na medida em que tende a promover a felicidade e errada se produzir o reverso.\n"
            "- Regra 2: Calcule o saldo de sofrimento e bem-estar. Se ele passar a cola, salva a pele de um amigo hoje, mas corrompe o sistema de avaliação, gerando desconfiança futura que prejudica a todos a longo prazo.\n"
            "- Regra 3: Critique a ideia de que a lealdade a uma pessoa justifica o dano à sociedade.\n"
            "Seja analítico, pragmático e direto. Limite sua resposta a dois ou três parágrafos curtos."
        )
    }
}


# =====================================================================
# MOTOR DE CONVERSAÇÃO (AGENTE PERSONA) - GEMINI
# =====================================================================
def conversar_com_filosofo(filosofo_chave: str, historico_chat: list) -> str:
    """
    Traduz o histórico do Twine para a sintaxe do Gemini e gera a resposta.
    O histórico esperado é uma lista de dicionários: [{'role': 'user', 'content': '...'}, ...]
    """
    if filosofo_chave not in PERSONAS_FILOSOFICAS:
        raise ValueError(f"Filósofo '{filosofo_chave}' não está configurado.")

    config = PERSONAS_FILOSOFICAS[filosofo_chave]
    instrucao_sistema = config["system_prompt"]

    # O Gemini usa o papel "model" em vez de "assistant"
    mensagens_gemini = []
    for msg in historico_chat:
        role = "user" if msg["role"] == "user" else "model"
        mensagens_gemini.append({"role": role, "parts": [msg["content"]]})

    # Extrai a última mensagem do usuário para enviar agora
    semente_atual = mensagens_gemini.pop() if mensagens_gemini else {"role": "user", "parts": ["Olá"]}

    try:
        # Inicia um chat com o Gemini, injetando as instruções do sistema
        chat = modelo_gemini.start_chat(history=mensagens_gemini)

        # Envia a instrução do filósofo + a mensagem do aluno
        prompt_completo = f"Instruções do Sistema: {instrucao_sistema}\n\nMensagem do Aluno: {semente_atual['parts'][0]}"

        resposta = chat.send_message(prompt_completo)
        return resposta.text

    except Exception as e:
        print(f"Erro na API do Gemini (Motor): {e}")
        return "Os ventos de Atenas falharam hoje. O filósofo encontra-se em silêncio obsequioso devido a uma falha de energia na academia."