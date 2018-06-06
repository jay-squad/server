from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()


class Restaurant(BASE):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    website = Column(String, nullable=True)
    phone_number = Column(Integer, nullable=True)


class MenuItem(BASE):
    __tablename__ = 'menuitems'
    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False,
        primary_key=True,
        autoincrement=False)
    name = Column(String, nullable=False)
