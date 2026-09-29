from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import Base


class DBCar(Base):
  __tablename__ = 'cars'
  __table_args__ = (
    CheckConstraint('year_created >= 1886', name='cars_year_created_check'),
    Index('ix_cars_team_id', 'team_id'),
  )
  car_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  name: Mapped[str] = mapped_column(String(100), nullable=False)
  year_created: Mapped[int] = mapped_column(SmallInteger, nullable=False)
  team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('teams.team_id', ondelete='RESTRICT'), nullable=False)
  team = relationship('DBTeam')

  @property
  def team_name(self) -> str:
    return self.team.team_name
