from datetime import datetime
from time import sleep

from scheduler import AGENDAMENTOS

def scheduler_process():
    """
    Diferente dos cenários anteriores, um processo dedicado não espera por uma única tarefa.
    O processo verifica periodicamente o que foi agendado, encaminhando para ser executado por outro processo.
    Temos uma separação clara entre quem persiste, quem verifica e quem executa a tarefa.   
    Processos dedicados não compartilham memória, em sistemas reais a comunicação é feita por bancos de dados ou caches.
    Em grandes volumes de dados o ideal seria utilizar conceitos como set-based e chunking para ler e processar esses dados.
    """

    print(f"Processo iniciado com sucesso...")

    while True:

        for agendamento in AGENDAMENTOS.copy():

            if datetime.now() >= agendamento["executar_em"]:
                print(f"Processo separado encontrou um agendamento.")
                print(f"Encaminhando tarefa para execução...")
                AGENDAMENTOS.remove(agendamento)

        sleep(1)

scheduler_process()
