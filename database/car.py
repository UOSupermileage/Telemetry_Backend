from sqlalchemy import BigInteger, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class DBCar(Base):
  __tablename__ = 'cars'
  car_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  name: Mapped[str] = mapped_column(String(100), nullable=False)
  year_created: Mapped[int] = mapped_column(SmallInteger, nullable=False)
  team_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('teams.team_id', ondelete='RESTRICT'), nullable=False)