from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class DBRun(Base):
  __tablename__ = 'runs'
  run_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  car_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('cars.car_id', ondelete='RESTRICT'), nullable=False)
  location_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('locations.location_id', ondelete='RESTRICT'), nullable=False)
  driver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('drivers.driver_id', ondelete='RESTRICT'), nullable=False)
  started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
  ended_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
  notes: Mapped[str | None] = mapped_column(Text, nullable=True)
  date_created: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())