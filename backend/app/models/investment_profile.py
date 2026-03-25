from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from app.db.base import Base

class InvestmentProfile(Base):
    __tablename__ = "investment_profiles"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))

    risk_tolerance = Column(String(100), nullable=True)
    time_horizon = Column(String(100), nullable=True)
    objective = Column(String(255), nullable=True)
    liquidity_needs = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)