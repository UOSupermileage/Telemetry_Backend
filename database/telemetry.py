from sqlalchemy import BigInteger, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class DBTelemetry(Base):
  __tablename__ = 'telemetry'
  run_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('runs.run_id', ondelete='CASCADE'), primary_key=True)
  tick: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  throttle: Mapped[float | None] = mapped_column(Float, nullable=True)
  speed: Mapped[float | None] = mapped_column(Float, nullable=True)
  current: Mapped[float | None] = mapped_column(Float, nullable=True)
  voltage: Mapped[float | None] = mapped_column(Float, nullable=True)