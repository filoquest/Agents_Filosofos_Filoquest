import os
import json
import google.generativeai as genai
from google.generativeai.types import generation_types

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))


# =====================================================================
# AVALIADOR COGNITIVO - GEMINI JSON MODE
# =====================================================================
def analisar_turno_com_qwen(mensagem_jogador: str, resposta_filosofo: str) -> dict:
    """
    Usa o Gemini 1.5 Flash no modo JSON para avaliar a maturidade da justificativa.
    (Mantivemos o nome da função 'analisar_turno_com_qwen' para não quebrar o seu app.py,
    mas sob o capô, é o Gemini quem trabalha).
    """

    prompt_sistema = (
        "Você é um algoritmo de análise cognitiva atuando no jogo de escolhas éticas 'O Gabarito'. "
        "A sua função é avaliar o diálogo entre o Jogador e o Filósofo sobre o dilema escolar (passar cola/gabarito) e devolver estritamente um objeto JSON válido.\n\n"
        "Regras de transição do Estado:\n"
        "- avancar_fase: Se o aluno apresentou uma justificativa madura e argumentada, mesmo que não seja a moralmente perfeita.\n"
        "- game_over: Se o aluno foi incrivelmente imoral, incentivou crimes ou ignorou completamente a reflexão.\n"
        "- manter_fase: Se o argumento foi muito curto, superficial e ele precisa reformular sua resposta perante o filósofo.\n\n"
        "Devolva EXATAMENTE o seguinte formato JSON, sem crases de formatação Markdown e sem texto extra:\n"
        "{\n"
        '  "perfil_cognitivo": "crítico" | "dogmático" | "superficial",\n'
        '  "proximo_estado": "manter_fase" | "avancar_fase" | "game_over"\n'
        "}"
    )

    conteudo_analise = f"{prompt_sistema}\n\nJogador: {mensagem_jogador}\nFilósofo: {resposta_filosofo}"

    try:
        # Configura o Gemini para forçar a saída em JSON
        modelo_gemini_json = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )

        resposta = modelo_gemini_json.generate_content(conteudo_analise)
        texto_limpo = resposta.text.strip()

        # Garante que o retorno é um dicionário Python
        return json.loads(texto_limpo)

    except json.JSONDecodeError as je:
        print(f"Erro na desserialização do JSON do Gemini: {je} - Resposta bruta: {resposta.text}")
        return {"perfil_cognitivo": "indeterminado", "proximo_estado": "manter_fase"}
    except Exception as e:
        print(f"Erro na API do Gemini (Avaliador): {e}")
        return {"perfil_cognitivo": "indeterminado", "proximo_estado": "manter_fase"}