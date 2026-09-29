from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, String, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import Base


class DBRun(Base):
  __tablename__ = 'runs'
  __table_args__ = (
    CheckConstraint('ended_at IS NULL OR ended_at > started_at', name='runs_dates_check'),
    Index('ix_runs_car_id', 'car_id'),
    Index('ix_runs_location_id', 'location_id'),
    Index('ix_runs_driver_id', 'driver_id'),
  )
  run_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  name: Mapped[str] = mapped_column(String(100), nullable=False)
  car_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('cars.car_id', ondelete='RESTRICT'), nullable=False)
  location_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('locations.location_id', ondelete='RESTRICT'), nullable=False)
  driver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('drivers.driver_id', ondelete='RESTRICT'), nullable=False)
  started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
  ended_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
  notes: Mapped[str | None] = mapped_column(Text, nullable=True)
  date_created: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
  car = relationship('DBCar')
  driver = relationship('DBDriver')
  location = relationship('DBLocation')

  @property
  def car_name(self) -> str:
    return self.car.name

  @property
  def driver_name(self) -> str:
    return f'{self.driver.first_name} {self.driver.last_name}'

  @property
  def location_name(self) -> str:
    return self.location.name
