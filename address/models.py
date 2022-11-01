from sqlalchemy import Column, Integer, String, FLOAT
from address.database import Base


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    zipcode = Column(Integer)
    longitude = Column(FLOAT)
    latitude = Column(FLOAT)
