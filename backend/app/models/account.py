from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))

    account_number = Column(String(100), nullable=True)
    account_type = Column(String(100), nullable=True)
    custodian = Column(String(255), nullable=True)
    account_value = Column(Float,       nullable=True)
    ownership = Column(String(100), nullable=True)
    ownership_percentage = Column(Float,       nullable=True)
    decision_making = Column(String(100), nullable=True)
    source_of_funds = Column(String(255), nullable=True)

    household = relationship("Household", back_populates="accounts")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)