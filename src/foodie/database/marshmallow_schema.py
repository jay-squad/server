# pylint: disable=wildcard-import, too-few-public-methods, missing-docstring, unused-wildcard-import, unused-argument
from src.foodie.database.schema import *
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields


class NormalizedString(fields.String):
    def __init__(self, attribute, **kargs):
        self._attribute = attribute
        super(fields.String, self).__init__(**kargs)

    def serialize(self, attr, obj, accessor=None):
        print(self.__dict__)
        return obj.__getattribute__(self._attribute).title()


class RestaurantSchema(ModelSchema):
    normalized_name = NormalizedString('name')

    class Meta:
        model = Restaurant


class MenuSectionSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = MenuSection


class MenuItemSchema(ModelSchema):
    normalized_name = NormalizedString('name')

    class Meta:
        include_fk = True
        model = MenuItem


class ItemImageSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = ItemImage
