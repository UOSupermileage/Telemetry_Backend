from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class DBLocation(Base):
  __tablename__ = 'locations'
  location_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  name: Mapped[str] = mapped_column(String(200), nullable=False)
  address: Mapped[str | None] = mapped_column(String(500), nullable=True)