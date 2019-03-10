# pylint: disable=wildcard-import, too-few-public-methods, missing-docstring, unused-wildcard-import, unused-argument
from src.foodie.database.schema import *
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from marshmallow_enum import EnumField


class NormalizedString(fields.String):
    def __init__(self, attribute, **kargs):
        self._attribute = attribute
        super(fields.String, self).__init__(**kargs)

    def serialize(self, attr, obj, accessor=None):
        return obj.__getattribute__(self._attribute).title()


class _FBUserSchema(ModelSchema):
    class Meta:
        model = FBUser


class RestaurantSchema(ModelSchema):
    normalized_name = NormalizedString('name')
    submitter = fields.Nested(
        _FBUserSchema,
        exclude=('submitted_item_images', 'submitted_items',
                 'submitted_menu_sections', 'submitted_restaurants'))
    approval_status = EnumField(ApprovalStatus)

    class Meta:
        model = Restaurant


class MenuSectionSchema(ModelSchema):
    normalized_name = NormalizedString('name')
    submitter = fields.Nested(
        _FBUserSchema,
        exclude=('submitted_item_images', 'submitted_items',
                 'submitted_menu_sections', 'submitted_restaurants'))
    approval_status = EnumField(ApprovalStatus)

    class Meta:
        include_fk = True
        model = MenuSection


class MenuItemSchema(ModelSchema):
    normalized_name = NormalizedString('name')
    submitter = fields.Nested(
        _FBUserSchema,
        exclude=('submitted_item_images', 'submitted_items',
                 'submitted_menu_sections', 'submitted_restaurants'))

    approval_status = EnumField(ApprovalStatus)

    class Meta:
        include_fk = True
        model = MenuItem


class ItemImageSchema(ModelSchema):
    submitter = fields.Nested(
        _FBUserSchema,
        exclude=('submitted_item_images', 'submitted_items',
                 'submitted_menu_sections', 'submitted_restaurants'))
    approval_status = EnumField(ApprovalStatus)

    class Meta:
        include_fk = True
        model = ItemImage


class FBUserSchema(_FBUserSchema):
    submitted_restaurants = fields.Nested(
        RestaurantSchema, many=True, exclude=('fbuser', 'submitter'))
    submitted_menu_sections = fields.Nested(
        MenuSectionSchema, many=True, exclude=('fbuser', 'submitter'))
    submitted_items = fields.Nested(
        MenuItemSchema, many=True, exclude=('fbuser', 'submitter'))
    submitted_item_images = fields.Nested(
        ItemImageSchema, many=True, exclude=('fbuser', 'submitter'))
