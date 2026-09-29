from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import Base


class DBDriverTeamHistory(Base):
  __tablename__ = 'driver_team_history'
  __table_args__ = (
    CheckConstraint('ended_at IS NULL OR ended_at > started_at', name='driver_team_history_dates_check'),
    Index('ix_driver_team_history_team_id', 'team_id'),
  )
  history_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  driver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('drivers.driver_id', ondelete='CASCADE'), nullable=False)
  team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('teams.team_id', ondelete='RESTRICT'), nullable=False)
  started_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
  ended_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
  driver = relationship('DBDriver')
  team = relationship('DBTeam')

  @property
  def driver_name(self) -> str:
    return f'{self.driver.first_name} {self.driver.last_name}'

  @property
  def team_name(self) -> str:
    return self.team.team_name
