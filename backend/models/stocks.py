from core.database import Base
from datetime import datetime as PyDateTime
from typing import Optional
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Stocks(Base):
    __tablename__ = "stocks"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    market: Mapped[str] = mapped_column(String, nullable=False)
    sector: Mapped[str] = mapped_column(String, nullable=False)
    industry: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[Optional[PyDateTime]] = mapped_column(DateTime(timezone=True), default=PyDateTime.now)
    updated_at: Mapped[Optional[PyDateTime]] = mapped_column(DateTime(timezone=True), default=PyDateTime.now, onupdate=PyDateTime.now)