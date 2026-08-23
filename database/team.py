from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class DBTeam(Base):
  __tablename__ = 'teams'
  team_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  team_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)