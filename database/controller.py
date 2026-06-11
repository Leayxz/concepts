from fastapi import FastAPI, status, Query
from fastapi.responses import JSONResponse

from process import DataIngestion, RbarVsSetBased, ProcessLotes, Pagination

app = FastAPI()

service_data = DataIngestion()
service_rbar_setbased = RbarVsSetBased()
service_process_lotes = ProcessLotes()
service_pagination = Pagination()

@app.post("/intake/")
def intake():

    result = service_data.gerar_dados()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"registros":result.registros,
                                                                 "tempo": result.tempo,
                                                                 "tempo_insercao": result.tempo_insercao,
                                                                 "memoria": result.memoria})


@app.post("/reset/")
def reset():

    result = service_data.resetar_dados()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"tempo": result.tempo,
                                                                 "memoria": result.memoria})


@app.post("/setbased/")
def set_based():

    result = service_rbar_setbased.set_based()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"tempo": result.tempo,
                                                                 "memoria": result.memoria})


@app.post("/rbar/")
def rbar():

    result = service_rbar_setbased.row_by_agonizing_row()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"tempo": result.tempo,
                                                                 "memoria": result.memoria})


@app.get("/pagination/offset/")
def pagination_offset(page: int = Query(default=1, ge=1), limit: int = Query(default=50, ge=1, le=100)):

    result = service_pagination.offset(page, limit)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"data": [{"registros": result.registros,"tempo": result.tempo,"memoria": result.memoria}],
                                                                 "pagination": {"page": result.page, "limit": result.limit, "has_next": result.has_next}})


@app.get("/pagination/keyset/")
def pagination_keyset(cursor: int = Query(default=0, ge=0), limit: int = Query(default=50, ge=1, le=100)):

    result = service_pagination.keyset(cursor, limit)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"data": [{"registros": result.registros, "tempo": result.tempo, "memoria": result.memoria}],
                                                                 "pagination": {"next_cursor": result.next_cursor, "limit": result.limit, "has_next": result.has_next}})


@app.get("/batching/offset/")
def batching_offset():

    result = service_process_lotes.batch_offset()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"registros": result.registros,
                                                                 "tempo": result.tempo,
                                                                 "memoria": result.memoria})


@app.get("/batching/keyset/")
def batching_keyset():
    
    result = service_process_lotes.batch_keyset()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"registros": result.registros,
                                                                 "tempo": result.tempo,
                                                                 "memoria": result.memoria})
