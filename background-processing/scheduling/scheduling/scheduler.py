import asyncio
from threading import Thread
from time import sleep
from datetime import datetime, timedelta
from dataclasses import dataclass

AGENDAMENTOS = []

@dataclass
class Result:
    message: str | None = None


def calcular_agendamento():
    agora = datetime.now()
    executar_em = agora + timedelta(seconds=10)
    tempo_espera = (executar_em - agora).total_seconds()
    return tempo_espera, executar_em


def espera_bloqueante():
    """
    Se executado em main thread, impede o processamento de outras REQs.
    """
    print(f"Espera bloqueante iniciada...")
    tempo_espera, _ = calcular_agendamento()
    sleep(tempo_espera)
    print(f">>> Momento de execução <<<")


async def espera_async_ASGI():
    """
    Se executado em main thread, permite o processamento de outras REQs.
    """
    print(f"Espera async iniciada...")
    tempo_espera, _ = calcular_agendamento()
    await asyncio.sleep(tempo_espera)
    print(f">>> Momento da execução <<<")


def execucao_thread():
    """
    Criação de thread dedicada para execução de tarefas curtas ou bloqueantes, principalmente em aplicações WSGI.
    Espera continua sendo bloqueante, porém em thread dedicada, permitindo que a aplicação responda imediatamente.
    Em threads, sucessos ou falhas devem ser persistidos e logados para que o sistema possa consultar ou tratar.    
    Mesmo com `daemon=false` seria um problema, porque se o servidor como um todo morrer, a tarefa é perdida.
    """

    print(f"Criando thread para executar tarefa curta agendada...")
    Thread(target=espera_bloqueante, daemon=True).start()
    print(f"Thread iniciada com sucesso.\n")
    return Result(message=f"Agendamento criado com sucesso. Executando tarefa bloqueante em thread.")


async def execucao_async_ASGI():
    """
    Em ASGI, o `asyncio.sleep()` permite realizar outras operações enquanto aguarda, porém ainda existe espera para responder o client.
    Se quisermos um cenário sem espera em ASGI, podemos enviar tarefas curtas para o Event Loop com `asyncio.create_task()`, permitindo responder imediatamente.
    O DRF ainda não possui suporte assíncrono completo, portanto o comportamento abaixo ainda não é totalmente válido.
    O Django ASGI permite `await sync_to_async()`, liberando o Event Loop para tarefas curtas, porém ainda existe espera.
    Esperas longas (horas ou dias) ainda devem ser persistidas, encaminhadas e executadas por outros processos, não devem viver em memória.
    """

    print(f"Executando tarefa curta em Event Loop...")
    asyncio.create_task(espera_async_ASGI())
    print(f"Tarefa curta enviada para o Event Loop. Resposta imediata ao client.")
    return Result(message=f"Execução async realizada com sucesso.")


def agendamento_persistido() -> Result:
    """
    Esperas longas (horas ou dias) ou críticas devem ser persistidas, depois encaminhadas e executadas por outros processos, não devem viver em memória.
    Nesse cenário, o client é liberado imediatamente após a persistência, sendo esse o único tempo de espera relevante, ou processamentos anteriores.
    Em aplicações ASGI podemos utilizar async/await referente à espera da persistência em banco de dados devido ao IO.
    Em Django podemos utilizar `await sync_to_async()` referente à espera da persistência em banco de dados devido ao IO.
    """

    _, executar_em = calcular_agendamento()

    AGENDAMENTOS.append({"descricao": "Executar daqui 10 segundos por um processo dedicado.",
                         "executar_em": executar_em})
    
    return Result(message=f"Agendamento persistido. Aguardando processo dedicado enviar para execução...")
