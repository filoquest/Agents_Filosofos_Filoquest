from motores_filosoficos import conversar_com_filosofo


def executar_loop_teste():
    print("--- Inicializando Engine do Jogo de Filosofia ---")

    # Simulando qual filósofo está ativo na fase atual (Estado do Jogo)
    filosofo_atual = "platao"

    # Memória da sessão do jogador na fase atual
    historico_sessao = []

    print(f"\n[Sistema]: Você entrou na sala de {filosofo_atual.upper()}. Diga algo para iniciar.")

    while True:
        entrada_usuario = input("\nVocê: ")
        if entrada_usuario.lower() in ["sair", "exit"]:
            break

        # 1. Adiciona a fala do jogador ao histórico
        historico_sessao.append({"role": "user", "content": entrada_usuario})

        # 2. Dispara a inferência para o agente filósofo correto
        print(f" Aguardando resposta de {filosofo_atual}...")
        resposta_ia = conversar_com_filosofo(filosofo_atual, historico_sessao)

        # 3. Exibe a resposta do filósofo e salva no histórico para manter o contexto
        print(f"\n[{filosofo_atual.upper()}]: {resposta_ia}")
        historico_sessao.append({"role": "assistant", "content": resposta_ia})

        # Aqui entraria o seu 'Agente Avaliador' (JSON) para decidir se muda
        # o 'filosofo_atual' para 'aristoteles' ou 'mill' baseado no perfil do aluno.


if __name__ == "__main__":
    executar_loop_teste()