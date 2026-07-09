import json
from huggingface_hub import InferenceClient

client = InferenceClient()

def analisar_turno_com_qwen(mensagem_jogador: str, resposta_filosofo: str) -> dict:
    """
    Consome o modelo Qwen para avaliar a interação e orquestrar a State Machine do jogo.
    """
    prompt_sistema = (
        "É um algoritmo de análise semântica num motor de jogo educativo. "
        "A tua função é avaliar o turno de diálogo e devolver estritamente um objeto JSON válido.\n"
        "Estrutura requerida:\n"
        "{\n"
        '  "perfil_cognitivo": "crítico" | "dogmático" | "superficial",\n'
        '  "proximo_estado": "manter_fase" | "avancar_fase" | "game_over"\n'
        "}"
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
        # Converte a string JSON devolvida pela inferência num dicionário nativo em Python
        return json.loads(resposta.choices[0].message.content)
    except Exception as e:
        # Mecanismo de fallback caso ocorra falha na inferência
        print(f"[Erro no Avaliador]: {e}")
        return {"perfil_cognitivo": "indeterminado", "proximo_estado": "manter_fase"}