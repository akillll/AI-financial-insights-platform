from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from app.db.base import Base

class Household(Base):
    __tablename__ = "households"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    annual_income = Column(Float, nullable=True)
    total_net_worth = Column(Float, nullable=True)
    tax_bracket = Column(String(50), nullable=True)
    liquid_net_worth  = Column(Float,       nullable=True)
    expense_range     = Column(String(100), nullable=True) 
    risk_tolerance    = Column(String(50),  nullable=True)
    time_horizon      = Column(String(100), nullable=True)

    members = relationship("Member", back_populates="household")
    accounts = relationship("Account", back_populates="household")
    bank_accounts = relationship("BankAccount", back_populates="household")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)