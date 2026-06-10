from huggingface_hub import InferenceClient

# O cliente puxa automaticamente o token que você configurou no comando 'login'
client = InferenceClient()

# 1. Definindo a Persona do Agente (System Prompt)
prompt_sistema = (
    "Você é o filósofo Sócrates. Responda ao usuário utilizando estritamente o método da maiêutica: "
    "nunca dê respostas diretas. Em vez disso, faça perguntas filosóficas que levem o interlocutor "
    "a questionar as próprias certezas. Mantenha o tom intelectual, formal e irônico."
)

# 2. Simulação de um input do jogador
mensagem_do_jogador = "Eu acho que a verdade é relativa e cada um tem a sua."

print("Enviando requisição ao modelo...")

# Usando um modelo open-source de ponta (Llama 3.1) hospedado no HF
resposta = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": mensagem_do_jogador}
    ],
    max_tokens=200,
    temperature=0.7
)

# 3. Exibindo o retorno do filósofo
print("\n[SÓCRATES]:", resposta.choices[0].message.content)