import os
import json
import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def analisar_turno_com_qwen(mensagem_jogador: str, resposta_filosofo: str) -> dict:
    prompt_sistema = (
        "Você é um algoritmo de análise cognitiva atuando no jogo de escolhas éticas 'O Gabarito'. "
        "A sua função é avaliar o diálogo entre o Jogador e o Filósofo sobre o dilema escolar (passar cola/gabarito) e devolver estritamente um objeto JSON válido.\n\n"
        "Regras de transição do Estado:\n"
        "- avancar_fase: Se o aluno apresentou uma justificativa madura e argumentada, mesmo que não seja a moralmente perfeita.\n"
        "- game_over: Se o aluno foi incrivelmente imoral, incentivou crimes ou ignorou completamente a reflexão.\n"
        "- manter_fase: Se o argumento foi muito curto, superficial e ele precisa reformular a sua resposta perante o filósofo.\n\n"
        "Devolva EXATAMENTE o seguinte formato JSON, sem crases e sem texto extra:\n"
        "{\n"
        '  "perfil_cognitivo": "crítico" | "dogmático" | "superficial",\n'
        '  "proximo_estado": "manter_fase" | "avancar_fase" | "game_over"\n'
        "}"
    )

    conteudo_analise = f"{prompt_sistema}\n\nJogador: {mensagem_jogador}\nFilósofo: {resposta_filosofo}"

    try:
        modelo_avaliador = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        resposta = modelo_avaliador.generate_content(conteudo_analise)
        texto_limpo = resposta.text.strip()
        return json.loads(texto_limpo)

    except Exception as e:
        print(f"Erro na API do Gemini (Avaliador): {e}")
        return {"perfil_cognitivo": "indeterminado", "proximo_estado": "manter_fase"}