from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import BigInteger, String, Boolean, DateTime, create_engine


class Base(DeclarativeBase):
    pass


class Registros(Base):
    __tablename__ = "registros"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    event_type: Mapped[str] = mapped_column(String(50))
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


engine = create_engine("sqlite:///sqlite.db", echo=False)
Base.metadata.create_all(engine)
