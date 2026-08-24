from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class DBDriver(Base):
  __tablename__ = 'drivers'
  driver_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  first_name: Mapped[str] = mapped_column(String(100), nullable=False)
  last_name: Mapped[str] = mapped_column(String(100), nullable=False)