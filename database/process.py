import tracemalloc
from datetime import datetime, timezone
from time import perf_counter
from dataclasses import dataclass

from sqlalchemy import select, update, insert
from sqlalchemy.orm import sessionmaker

from models import Registros, engine

SessionLocal = sessionmaker(bind=engine)

@dataclass
class Result:
    registros: str | None = None
    tempo: str | None = None
    tempo_insercao: str | None = None
    memoria: str | None = None
    page: int | None = None
    next_cursor: int | None = None
    limit: int | None = None
    has_next: bool | None = None
    error: Exception | None = None


class DataIngestion:

    def gerar_dados(self,) -> Result:
        """
        Escreve os dados em batch e chunk, sem explodir a memória da aplicação.
        Escrever grandes volumes de dados se torna algo tão demorado que estratégias de Background Jobs ou Mensageria são importantes.
        """

        TOTAL_REGISTROS = 1_000_000
        CHUNK_SIZE = 10_000
        DATA_HORA = datetime.now(timezone.utc)
        TEMPO_INSERCAO = 0

        # Benchmark
        start = perf_counter()
        tracemalloc.start()

        for inicio in range(0, TOTAL_REGISTROS, CHUNK_SIZE):

            lote = [{
                "user_id": i,
                "event_type": "TEST",
                "processed": False,
                "created_at": DATA_HORA,
                "processed_at": None,
            }
                for i in range(inicio, inicio + CHUNK_SIZE)
            ]

            # Benchmark
            start_insert = perf_counter()

            with SessionLocal.begin() as session:
                session.execute(insert(Registros), lote)

            # Benchmark
            TEMPO_INSERCAO += perf_counter() - start_insert

        # Benchmark
        stop = perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        memory = peak / 1024 / 1024
        tracemalloc.stop()

        return Result(registros=f"{inicio + len(lote)}", tempo=f"{stop:.2f}", tempo_insercao=f"{TEMPO_INSERCAO:.2f}", memoria=f"{memory:.2f}")


    def resetar_dados(self) -> Result:
        """
        Escrita em todos os dados de uma única vez, sem trazer dados para a memória.
        Poderia ser feito em batch, não pela memória, porém porque locks, logs e rollbacks em grandes volumes de dados são custosos.
        O batching poderia ser feito usando uma subquery dentro do .where() com select() e limit().
        Escrever grandes volumes de dados se torna algo tão demorado que estratégias de Background Jobs ou Mensageria são importantes.
        """

        # Benchmark
        start = perf_counter()
        tracemalloc.start()

        with SessionLocal.begin() as session:
            query = update(Registros).values(processed=False, processed_at=None)
            session.execute(query)

        # Benchmark
        stop = perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        memory = peak / 1024 / 1024
        tracemalloc.stop()

        return Result(tempo=f"{stop:.2f}", memoria=f"{memory:.2f}")


class Pagination:
    """Comparação entre Offset e Keyset Pagination."""

    def offset(self, page: int, limit: int) -> Result:
        """
        Leitura realizando o conceito de offset pagination, utilizando .limit() para limitar os dados e .offset() para indicar o início.
        Memória controlada devido ao .limit(), impedindo explosões e grandes volumes de dados na memória da aplicação.
        Em grandes volumes de dados o tempo de processamento é maior utilizando .offset(), porque é necessário percorrer dados anteriores.
        """

        # Benchmark
        start = perf_counter()
        tracemalloc.start()

        with SessionLocal() as session:
            query = select(Registros).order_by(Registros.id).limit(limit + 1).offset((page - 1) * limit)
            data = list(session.scalars(query).all())
            
            has_next = len(data) > limit
            if has_next: data.pop()
            TOTAL_REGISTROS = len(data)

        # Benchmark
        stop = perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        memory = peak / 1024 / 1024
        tracemalloc.stop()

        return Result(registros=f"{TOTAL_REGISTROS}",
                      tempo=f"{stop:.2f} Seconds",
                      memoria=f"{memory:.2f} MB",
                      page=page,
                      limit=limit,
                      has_next=has_next,
                    )


    def keyset(self, cursor: int, limit: int) -> Result:
        """
        Leitura realizando o conceito de keyset pagination, utilizando .limit() para limitar os dados e `cursor/keyset` para indicar o início.
        Memória controlada devido ao .limit(), impedindo explosões e grandes volumes de dados na memória da aplicação.
        Em grandes volumes de dados o tempo de processamento é menor utilizando `cursor/keyset`, porque não é necessário percorrer dados anteriores.      
        """

        # Benchmark
        start = perf_counter()
        tracemalloc.start()

        with SessionLocal() as session:
            query = select(Registros).where(Registros.id > cursor).order_by(Registros.id).limit(limit + 1)
            data = list(session.scalars(query).all())

            has_next = len(data) > limit
            if has_next: data.pop()
            TOTAL_REGISTROS = len(data)

        # Benchmark
        stop = perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        memory = peak / 1024 / 1024
        tracemalloc.stop()

        return Result(registros=f"{TOTAL_REGISTROS}",
                      tempo=f"{stop:.2f}",
                      memoria=f"{memory:.2f}",
                      next_cursor=data[-1].id if data else None,
                      limit=limit,
                      has_next=has_next
                    )


class ProcessLotes:
    """Comparação entre processamentos batching utilizando offset e cursor/keyset."""

    def batch_offset(self) -> Result:
        """
        Leitura dos dados realizada através de batching e chunking.
        Memória da aplicação sempre estável, sem explosões, porém tempo de processamento maior para grandes volumes de dados devido ao .offset().
        Leitura de grandes volumes de dados se torna algo tão demorado que estratégias de Background Jobs ou Mensageria são importantes.        
        """

        CHUNK_SIZE = 1000
        OFFSET = 0
        PROCESS_DATA = 0

        start = perf_counter()
        tracemalloc.start()

        while True:

            with SessionLocal() as session:
                query = select(Registros).order_by(Registros.id).limit(CHUNK_SIZE).offset(OFFSET)
                data = session.execute(query).all()

                if not data:
                    break

                PROCESS_DATA += len(data)
                OFFSET += CHUNK_SIZE

        stop = perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        memory = peak / 1024 / 1024
        tracemalloc.stop()

        return Result(registros=f"{PROCESS_DATA}", tempo=f"{stop:.2f} Seconds", memoria=f"{memory:.2f} MB")


    def batch_keyset(self) -> Result:
        """
        Leitura de todos os dados realizada em batching e chunking.
        Tempo de procesamento extremamente menor, sem a necessidade de percorrer todos os dados anteriores.
        Memória estável devido ao processamento em chunking.
        Leitura de grandes volumes de dados se torna algo tão demorado que estratégias de Background Jobs ou Mensageria são importantes.
        """

        CHUNK_SIZE = 1000
        LAST_ID = 0
        PROCESS_DATA = 0

        # Benchmark
        start = perf_counter()
        tracemalloc.start()

        while True:
            with SessionLocal() as session:
                query = select(Registros).where(Registros.id > LAST_ID).order_by(Registros.id).limit(CHUNK_SIZE)
                data = session.scalars(query).all()

                if not data:
                    break

                LAST_ID = data[-1].id
                PROCESS_DATA += len(data)

        # Benchmark
        stop = perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        memory = peak / 1024 / 1024
        tracemalloc.stop()

        return Result(registros=f"{PROCESS_DATA}", tempo=f"{stop:.2f} Seconds", memoria=f"{memory:.2f} MB")


class RbarVsSetBased:
    """Comparação entre processamentos RBAR e Set Based atualizando os dados."""

    def row_by_agonizing_row(self) -> Result:
        """
        Escrita linha a linha dentro da aplicação, explodindo o tempo de processamento e memória da aplicação.
        Leitura trazendo todos os dados brutos para a memória, explodindo a memória da aplicação.
        Materializar grandes volumes de objetos ORM em memória se torna altamente custoso, explodindo a memória da aplicação.
        Poderia ser feito em batch, principalmente pela memória, e porque locks, logs e rollbacks em grandes volumes de dados são custosos.
        O batching poderia ser feito usando uma subquery dentro do .where() com .select() e .limit().
        """

        # Benchmark
        start = perf_counter()
        tracemalloc.start()

        with SessionLocal.begin() as session:
            query = select(Registros).where(Registros.processed.is_(False))
            data = session.scalars(query).all()

            for registro in data:
                registro.processed = True

        # Benchmark
        total_time = perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        memory = peak / 1024 / 1024
        tracemalloc.stop()

        return Result(tempo=f"{total_time:.2f} Seconds", memoria=f"{memory:.2f} MB")


    def set_based(self) -> Result:
        """
        Escrita realizada dentro do banco de dados, utilizando o conceito set-based e bulk operation, sem dados na memória da aplicação.
        A atualização !!não!! é feita em batch, tornando locks, logs e rollbacks custosos em grandes volumes de dados.
        A atualização poderia ser feita em batch usando uma subquery dentro do .where() com select() e limit().
        Atualizar grandes volumes de dados se torna algo tão demorado que estratégias de Background Jobs ou Mensageria são importantes.
        """

        # Benchmark
        start = perf_counter()
        tracemalloc.start()

        with SessionLocal.begin() as session:
            query = update(Registros).where(Registros.processed.is_(False)).values(processed=True)
            session.execute(query)

        # Benchmark
        final_time = perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        memoria = peak / 1024 / 1024
        tracemalloc.stop()

        return Result(tempo=f"{final_time:.2f} Seconds", memoria=f"{memoria:.2f} MB")

# OBS: Implementar SeekPagination
