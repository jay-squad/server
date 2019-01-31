import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, ForeignKeyConstraint
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
    phone_number = Column(String, nullable=True)
    cuisine_type = Column(String, nullable=True)


class MenuSection(BASE):
    __tablename__ = 'menusections'
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
        autoincrement=False)
    name = Column(String, nullable=False, primary_key=True)


class MenuItem(BASE):
    __tablename__ = 'menuitems'
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
        autoincrement=False)
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=True)


class MenuSectionAssignment(BASE):
    __tablename__ = 'menusectionassignemnts'
    restaurant_id = Column(Integer, primary_key=True, nullable=False)
    section_name = Column(String, primary_key=True, nullable=False)
    menu_item_id = Column(Integer, primary_key=True, nullable=False)
    __table_args__ = (ForeignKeyConstraint(
        [menu_item_id, restaurant_id], [MenuItem.id, MenuItem.restaurant_id],
        ondelete='CASCADE'),
                      ForeignKeyConstraint(
                          [section_name, restaurant_id],
                          [MenuSection.name, MenuSection.restaurant_id],
                          ondelete='CASCADE'))


class ItemImage(BASE):
    __tablename__ = 'itemimages'
    link = Column(String, primary_key=True, nullable=False)
    menu_item_id = Column(Integer, primary_key=True, nullable=False)
    restaurant_id = Column(Integer, primary_key=True, nullable=False)
    __table_args__ = (ForeignKeyConstraint(
        (menu_item_id, restaurant_id), (MenuItem.id, MenuItem.restaurant_id),
        ondelete='CASCADE'), )


class FBUser(BASE):
    __tablename__ = 'fbusers'
    id = Column(String, nullable=False, primary_key=True)
    created = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        onupdate=datetime.datetime.utcnow,
    )
    name = Column(String, nullable=False)
    profile_url = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
