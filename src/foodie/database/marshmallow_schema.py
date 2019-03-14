# pylint: disable=wildcard-import, too-few-public-methods, missing-docstring, unused-wildcard-import, unused-argument
import re
from src.foodie.database.schema import *
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from marshmallow_enum import EnumField


def titlecase(s):
    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                  lambda mo: mo.group(0)[0].upper() + mo.group(0)[1:].lower(),
                  s)


class NormalizedString(fields.String):
    def __init__(self, attribute, **kargs):
        self._attribute = attribute
        super(fields.String, self).__init__(**kargs)

    def serialize(self, attr, obj, accessor=None):
        stripped_string = obj.__getattribute__(self._attribute).strip()
        return titlecase(stripped_string)


class FBUserSchemaNoSubmissions(ModelSchema):
    class Meta:
        model = FBUser
        exclude = ('submitted_restaurants', 'submitted_menu_sections',
                   'submitted_items', 'submitted_item_images')


class RestaurantSchema(ModelSchema):
    normalized_name = NormalizedString('name')

    class Meta:
        model = Restaurant


class MenuSectionSchema(ModelSchema):
    normalized_name = NormalizedString('name')

    class Meta:
        include_fk = True
        model = MenuSection


class MenuItemSchema(ModelSchema):
    normalized_name = NormalizedString('name')

    class Meta:
        include_fk = True
        model = MenuItem


class ItemImageSchema(ModelSchema):
    approval_status = EnumField(ApprovalStatus)

    class Meta:
        include_fk = True
        model = ItemImage


class FBUserSchema(FBUserSchemaNoSubmissions):
    submitted_restaurants = fields.Nested(
        RestaurantSchema, many=True, exclude=('fbuser', 'submitter'))
    submitted_menu_sections = fields.Nested(
        MenuSectionSchema, many=True, exclude=('fbuser', 'submitter'))
    submitted_items = fields.Nested(
        MenuItemSchema, many=True, exclude=('fbuser', 'submitter'))
    submitted_item_images = fields.Nested(
        ItemImageSchema, many=True, exclude=('fbuser', 'submitter'))
