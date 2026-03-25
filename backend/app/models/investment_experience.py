from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class InvestmentExperience(Base):
    __tablename__ = "investment_experience"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id"))

    asset_type = Column(String(100))
    years = Column(Integer)