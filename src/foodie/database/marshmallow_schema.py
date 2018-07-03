from src.foodie.database.schema import *
from marshmallow_sqlalchemy import ModelSchema


class RestaurantSchema(ModelSchema):
    class Meta:
        model = Restaurant


class MenuSectionSchema(ModelSchema):
    class Meta:
        model = MenuSection


class MenuItemSchema(ModelSchema):
    class Meta:
        model = MenuItem


class ItemImageSchema(ModelSchema):
    class Meta:
        model = ItemImage