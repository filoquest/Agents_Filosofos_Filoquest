import time
from motores_filosoficos import conversar_com_filosofo


def executar_bateria_de_testes():
    print("=" * 60)
    print(" INICIANDO BATERIA DE TESTES DE COGNIÇÃO E CLAREZA ".center(60, "="))
    print("=" * 60)

    # Simulação de um input típico de um aluno do ensino básico/secundário
    cenario_teste = (
        "Se um colega meu está a sofrer bullying, eu acho que o melhor é ignorar "
        "e não me meter. Se eu for ajudar, posso acabar por ser o próximo alvo e sofrer também."
    )

    historico_simulado = [{"role": "user", "content": cenario_teste}]
    filosofos = ["kant", "mill", "aristoteles"]

    print(f"\n[INPUT DO ALUNO]: '{cenario_teste}'\n")

    for filosofo in filosofos:
        print(f"[{filosofo.upper()}] A processar inferência...")
        inicio = time.time()

        try:
            # Chama o motor isolado
            resposta = conversar_com_filosofo(filosofo, historico_simulado)
            latencia = time.time() - inicio

            print(f"Tempo de Resposta: {latencia:.2f} segundos")
            print("-" * 40)
            print(resposta)
            print("-" * 60 + "\n")

        except Exception as e:
            print(f"[ERRO NO TESTE - {filosofo.upper()}]: {e}\n")


if __name__ == "__main__":
    executar_bateria_de_testes()