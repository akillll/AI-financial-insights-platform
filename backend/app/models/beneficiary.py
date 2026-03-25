from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from datetime import datetime
from app.db.base import Base

class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))

    name = Column(String(255))
    relationship = Column(String(100), nullable=True)
    type = Column(String(50), nullable=True)
    percentage = Column(Float)
    dob = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)