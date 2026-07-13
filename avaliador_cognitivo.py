import json
from huggingface_hub import InferenceClient

client = InferenceClient()

def analisar_turno_com_qwen(mensagem_jogador: str, resposta_filosofo: str) -> dict:
    """
    Consome o modelo Qwen para avaliar a interação e orquestrar a State Machine do jogo.
    """
    prompt_sistema = (
        "Você é um algoritmo de análise cognitiva atuando no jogo educativo de escolhas éticas 'O Gabarito'. "
        "A sua função é avaliar o diálogo entre o Jogador e o Filósofo sobre o dilema escolar (passar cola/gabarito) e devolver estritamente um objeto JSON válido.\n\n"
        "Estrutura requerida:\n"
        "{\n"
        '  "perfil_cognitivo": "crítico" | "dogmático" | "superficial",\n'
        '  "proximo_estado": "manter_fase" | "avancar_fase" | "game_over"\n'
        "}\n\n"
        "Regras de transição do Estado:\n"
        "- avancar_fase: Se o aluno apresentou uma justificativa madura e argumentada, mesmo que não seja a moralmente perfeita.\n"
        "- game_over: Se o aluno foi incrivelmente imoral, incentivou crimes ou ignorou completamente a reflexão.\n"
        "- manter_fase: Se o argumento foi muito curto ('sim', 'não sei'), superficial e ele precisa reformular sua resposta perante o filósofo."
    )

    conteudo_analise = f"Jogador: {mensagem_jogador}\nFilósofo: {resposta_filosofo}"

    try:
        resposta = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": conteudo_analise}
            ],
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        return json.loads(resposta.choices[0].message.content)
    except Exception as e:
        print(f"[Erro no Avaliador]: {e}")
        return {"perfil_cognitivo": "indeterminado", "proximo_estado": "manter_fase"}