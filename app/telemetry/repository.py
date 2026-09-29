from sqlalchemy import BigInteger, CheckConstraint, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.connection import Base


class DBTelemetry(Base):
  __tablename__ = 'telemetry'
  __table_args__ = (
    CheckConstraint('tick >= 0', name='telemetry_tick_check'),
    CheckConstraint('throttle IS NULL OR throttle >= 0', name='telemetry_throttle_check'),
    CheckConstraint('speed IS NULL OR speed >= 0', name='telemetry_speed_check'),
    CheckConstraint('current IS NULL OR current >= 0', name='telemetry_current_check'),
    CheckConstraint('voltage IS NULL OR voltage >= 0', name='telemetry_voltage_check'),
  )
  run_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('runs.run_id', ondelete='CASCADE'), primary_key=True)
  tick: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  throttle: Mapped[float | None] = mapped_column(Float, nullable=True)
  speed: Mapped[float | None] = mapped_column(Float, nullable=True)
  current: Mapped[float | None] = mapped_column(Float, nullable=True)
  voltage: Mapped[float | None] = mapped_column(Float, nullable=True)
