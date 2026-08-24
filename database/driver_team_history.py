from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class DBDriverTeamHistory(Base):
  __tablename__ = 'driver_team_history'
  history_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  driver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('drivers.driver_id', ondelete='CASCADE'), nullable=False)
  team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('teams.team_id', ondelete='RESTRICT'), nullable=False)
  started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
  ended_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)