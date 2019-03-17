import datetime

from flask import g
from src.foodie.database.db import db
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
import enum

BASE = declarative_base()


class Record:
    created_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        nullable=False,
        onupdate=datetime.datetime.utcnow,
    )


class ApprovalStatus(enum.Enum):
    pending = 0
    approved = 1
    rejected = 2


class AmendmentType(enum.Enum):
    amendment = 0
    report = 1


class FBUser(Record, BASE):
    __tablename__ = 'fbusers'
    id = db.Column(db.String, nullable=False, primary_key=True)
    name = db.Column(db.String, nullable=False)
    profile_url = db.Column(db.String, nullable=False)
    access_token = db.Column(db.String, nullable=False)
    amazon_code = db.Column(db.String, nullable=True)
    points = db.Column(db.Integer, nullable=False, default=0)
    last_reward_points = db.Column(db.Integer, nullable=False, default=0)
    submitted_restaurants = relationship('Restaurant', lazy='select')
    submitted_menu_sections = relationship('MenuSection', lazy='select')
    submitted_items = relationship('MenuItem', lazy='select')
    submitted_item_images = relationship('ItemImage', lazy='select')


class UserSubmitted:
    request_uuid = db.Column(
        db.String, default=(lambda _: g.request_uuid), nullable=False)

    @declared_attr
    def submitter_id(cls):
        return db.Column(db.String, db.ForeignKey("fbusers.id"), nullable=True)


class Restaurant(UserSubmitted, Record, BASE):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.String, nullable=True)
    website = db.Column(db.String, nullable=True)
    phone_number = db.Column(db.String, nullable=True)
    cuisine_type = db.Column(db.String, nullable=True)
    approval_status = db.Column(
        db.Enum(ApprovalStatus),
        default=
        (lambda _: ApprovalStatus.approved if g.is_admin else ApprovalStatus.pending
         ),
        nullable=False)


class MenuSection(UserSubmitted, Record, BASE):
    __tablename__ = 'menusections'
    restaurant_id = db.Column(
        db.Integer,
        db.ForeignKey("restaurants.id", ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
        autoincrement=False)
    name = db.Column(db.String, nullable=False, primary_key=True)


class MenuItem(UserSubmitted, Record, BASE):
    __tablename__ = 'menuitems'
    restaurant_id = db.Column(
        db.Integer,
        db.ForeignKey("restaurants.id", ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
        autoincrement=False)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    price = db.Column(db.Float, nullable=True)


class MenuSectionAssignment(UserSubmitted, Record, BASE):
    __tablename__ = 'menusectionassignemnts'
    restaurant_id = db.Column(db.Integer, primary_key=True, nullable=False)
    section_name = db.Column(db.String, primary_key=True, nullable=False)
    menu_item_id = db.Column(db.Integer, primary_key=True, nullable=False)
    __table_args__ = (db.ForeignKeyConstraint(
        [menu_item_id, restaurant_id], [MenuItem.id, MenuItem.restaurant_id],
        ondelete='CASCADE'),
                      db.ForeignKeyConstraint(
                          [section_name, restaurant_id],
                          [MenuSection.name, MenuSection.restaurant_id],
                          ondelete='CASCADE'))


class ItemImage(UserSubmitted, Record, BASE):
    __tablename__ = 'itemimages'
    link = db.Column(db.String, primary_key=True, nullable=False)
    restaurant_id = db.Column(db.Integer, primary_key=True, nullable=False)
    menu_item_id = db.Column(db.Integer, primary_key=True, nullable=False)
    approval_status = db.Column(
        db.Enum(ApprovalStatus),
        default=
        (lambda _: ApprovalStatus.approved if g.is_admin else ApprovalStatus.pending
         ),
        nullable=False)
    __table_args__ = (db.ForeignKeyConstraint(
        (menu_item_id, restaurant_id), (MenuItem.id, MenuItem.restaurant_id),
        ondelete='CASCADE'), )


class Amendment(UserSubmitted, Record, BASE):
    __tablename__ = 'amendments'
    id = db.Column(
        db.Integer, primary_key=True, autoincrement=True, nullable=False)
    reason = db.Column(db.String, nullable=False)
    identifier = db.Column(db.String, nullable=False)
    specifics = db.Column(db.String, nullable=True)
    amendment_type = db.Column(
        db.Enum(AmendmentType),
        nullable=False,
        default=AmendmentType.amendment)
