from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from .db import Base

# Пользователь для авторизации
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "user" или "admin"

# Катер
class Vessel(Base):
    __tablename__ = "vessels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String)
    displacement = Column(Float)
    build_date = Column(Date)
    voyages = relationship("Voyage", back_populates="vessel")

# Рейс катера
class Voyage(Base):
    __tablename__ = "voyages"
    id = Column(Integer, primary_key=True, index=True)
    vessel_id = Column(Integer, ForeignKey("vessels.id"))
    depart_date = Column(Date)
    return_date = Column(Date)
    vessel = relationship("Vessel", back_populates="voyages")
    crew_members = relationship("CrewMember", back_populates="voyage")
    visits = relationship("Visit", back_populates="voyage")

# Экипаж рейса
class CrewMember(Base):
    __tablename__ = "crew_members"
    id = Column(Integer, primary_key=True, index=True)
    voyage_id = Column(Integer, ForeignKey("voyages.id"))
    name = Column(String, nullable=False)
    position = Column(String)
    address = Column(String)
    voyage = relationship("Voyage", back_populates="crew_members")

# Банка
class Bank(Base):
    __tablename__ = "banks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    visits = relationship("Visit", back_populates="bank")

# Визит катера на банку
class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True, index=True)
    voyage_id = Column(Integer, ForeignKey("voyages.id"))
    bank_id = Column(Integer, ForeignKey("banks.id"))
    arrival_date = Column(Date)
    departure_date = Column(Date)
    quality = Column(String)  # "отличное", "хорошее", "плохое"
    catches = relationship("Catch", back_populates="visit")
    voyage = relationship("Voyage", back_populates="visits")
    bank = relationship("Bank", back_populates="visits")

# Улов по сортам рыбы
class Catch(Base):
    __tablename__ = "catches"
    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"))
    species = Column(String)
    weight = Column(Float)
    visit = relationship("Visit", back_populates="catches")

