from sqlalchemy import Boolean, Column, Integer, String
from database import Base

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, index=True)
    itemname = Column(String(50), unique=True)
    quantity = Column(Integer)