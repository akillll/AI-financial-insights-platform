from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from app.db.base import Base

class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id"))

    first_name = Column(String(100))
    last_name = Column(String(100))
    relationship_type = Column(String(50), nullable=True)
    dob = Column(Date, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)

    occupation = Column(String(255), nullable=True)
    employer = Column(String(255), nullable=True)
    marital_status = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)   
    state = Column(String(100), nullable=True) 
    country = Column(String(100), nullable=True)

    household = relationship("Household", back_populates="members")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)