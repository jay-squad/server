import datetime

from flask import g
from sqlalchemy import Column, Boolean, Integer, String, Float, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base()


class Record:
    created_at = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        onupdate=datetime.datetime.utcnow,
    )


class FBUser(Record, BASE):
    __tablename__ = 'fbusers'
    id = Column(String, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    profile_url = Column(String, nullable=False)
    access_token = Column(String, nullable=False)


class UserSubmitted:
    submitter_id = ForeignKey("restaurants.id", nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)


class Restaurant(UserSubmitted, Record, BASE):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    website = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    cuisine_type = Column(String, nullable=True)


class MenuSection(UserSubmitted, Record, BASE):
    __tablename__ = 'menusections'
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id", ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
        autoincrement=False)
    name = Column(String, nullable=False, primary_key=True)


class MenuItem(UserSubmitted, Record, BASE):
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


class MenuSectionAssignment(UserSubmitted, Record, BASE):
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


class ItemImage(UserSubmitted, Record, BASE):
    __tablename__ = 'itemimages'
    link = Column(String, primary_key=True, nullable=False)
    menu_item_id = Column(Integer, primary_key=True, nullable=False)
    restaurant_id = Column(Integer, primary_key=True, nullable=False)
    __table_args__ = (ForeignKeyConstraint(
        (menu_item_id, restaurant_id), (MenuItem.id, MenuItem.restaurant_id),
        ondelete='CASCADE'), )
