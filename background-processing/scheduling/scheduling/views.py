from rest_framework.decorators import api_view
from rest_framework.response import Response

from scheduling.scheduler import execucao_thread, agendamento_persistido, execucao_async_ASGI, AGENDAMENTOS


@api_view(["GET"])
def get_agendamentos(request):
    return Response(status=200, data={"data": AGENDAMENTOS})


@api_view(["POST"])
def thread(request):
    result = execucao_thread()
    return Response(status=201, data={"message": result.message})


@api_view(["POST"])
def persistencia(request):
    result = agendamento_persistido()
    return Response({"message": result.message})


@api_view(["POST"])
async def async_scheduling(request):
    await execucao_async_ASGI()
    return Response(status=202, data={"message": "Estoura erro porque o DRF ainda não suporta totalmente async."})
