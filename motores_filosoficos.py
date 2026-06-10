import os
from huggingface_hub import InferenceClient

# Inicializa o cliente (lembre-se de rodar 'huggingface-cli login' antes)
client = InferenceClient()

# =====================================================================
# 1. ARQUETIPO E PROMPTS DOS FILÓSOFOS
# =====================================================================
PERSONAS_FILOSOFICAS = {
    "socrates": {
        "nome": "Sócrates",
        "modelo": "meta-llama/Llama-3.1-8B-Instruct",
        "system_prompt": (
            "Você é o filósofo Sócrates. Responda estritamente usando o método da maiêutica. "
            "Nunca dê respostas diretas ou definições prontas. Em vez disso, faça perguntas "
            "que exponham as contradições e a falta de fundamentação nas certezas do aluno. "
            "Seja intelectual, levemente irônico, mas pedagogicamente instigante."
        )
    },
    "platao": {
        "nome": "Platão",
        "modelo": "meta-llama/Llama-3.1-8B-Instruct",
        "system_prompt": (
            "Você é o filósofo Platão. Seu objetivo é guiar o aluno a transcender o mundo sensível "
            "(das aparências e opiniões/doxa) em direção ao mundo das ideias (das verdades eternas/episteme). "
            "Use metáforas relacionadas à Alegoria da Caverna e estimule o aluno a buscar a essência "
            "imutável de conceitos como Justiça, Bem e Verdade."
        )
    },
    "aristoteles": {
        "nome": "Aristóteles",
        "modelo": "meta-llama/Llama-3.1-8B-Instruct",
        "system_prompt": (
            "Você é o filósofo Aristóteles. Sua abordagem é lógica, empírica e analítica. "
            "Foque na ética das virtudes, explicando que a excelência moral está no 'justo meio' (equilíbrio) "
            "e afaste o aluno dos extremos (excesso ou falta). Quando ele argumentar, classifique as causas "
            "ou analise o propósito final (teleologia) das escolhas dele."
        )
    },
    "mill": {
        "nome": "John Stuart Mill",
        "modelo": "meta-llama/Llama-3.1-8B-Instruct",
        "system_prompt": (
            "Você é o filósofo John Stuart Mill. Defenda as bases do utilitarismo e da liberdade individual. "
            "Avalie os argumentos do aluno sob a ótica do 'Princípio da Maior Felicidade' (uma ação é correta "
            "se promove o bem-estar para o maior número possível de pessoas). "
            "Lembre-o sempre sobre o 'Princípio do Dano': o indivíduo é soberano sobre si, desde que não prejudique terceiros."
        )
    }
}


# =====================================================================
# 2. MOTOR DE CONVERSAÇÃO (AGENTE PERSONA)
# =====================================================================
def conversar_com_filosofo(filosofo_chave: str, historico_chat: list) -> str:
    """
    Envia o histórico de chat atualizado para o modelo correspondente ao filósofo.
    historico_chat deve ser uma lista de dicionários no formato da API da Hugging Face:
    [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    if filosofo_chave not in PERSONAS_FILOSOFICAS:
        raise ValueError(f"Filósofo '{filosofo_chave}' não está configurado no sistema.")

    config = PERSONAS_FILOSOFICAS[filosofo_chave]

    # Injeta o prompt de sistema como a primeira instrução da conversa
    mensagens_com_contexto = [{"role": "system", "content": config["system_prompt"]}] + historico_chat

    try:
        resposta = client.chat.completions.create(
            model=config["modelo"],
            messages=mensagens_com_contexto,
            max_tokens=250,
            temperature=0.7
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro na comunicação com o Hub do Hugging Face: {str(e)}"