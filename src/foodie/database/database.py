import os
import datetime
from src.foodie.database.db import db
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker, noload, joinedload
from src.foodie.database.schema import Restaurant, MenuSection, MenuItem, MenuSectionAssignment, ItemImage, FBUser, ApprovalStatus

import src.foodie.settings.settings  # pylint: disable=unused-import


def _add_and_commit(model):
    db.session.add(model)
    db.session.commit()
    return model


def insert_restaurant(**kargs):
    assert "id" not in kargs
    return _add_and_commit(Restaurant(**kargs))


def insert_menu_section(**kargs):
    return _add_and_commit(MenuSection(**kargs))


def insert_menu_item(**kargs):
    return _add_and_commit(MenuItem(**kargs))


def insert_menu_section_assignment(**kargs):
    return _add_and_commit(MenuSectionAssignment(**kargs))


def insert_item_image(**kargs):
    return _add_and_commit(ItemImage(**kargs))


def insert_new_item(restaurant_id,
                    item_name,
                    item_image,
                    submitter_id,
                    description=None,
                    price=None,
                    section_name=None):
    menu_item = db.session.query(MenuItem) \
    .filter(MenuItem.restaurant_id == restaurant_id) \
    .filter(MenuItem.name == item_name) \
    .one_or_none()

    if not menu_item:
        menu_item = MenuItem(
            restaurant_id=restaurant_id,
            name=item_name,
            submitter_id=submitter_id,
            price=price,
            description=description)
        db.session.add(menu_item)
        db.session.flush()
        if section_name is not None:
            if not db.session.query(MenuSection).get(
                (restaurant_id, section_name)):
                db.session.add(
                    MenuSection(
                        restaurant_id=restaurant_id, name=section_name))
                db.session.flush()
            db.session.add(
                MenuSectionAssignment(
                    restaurant_id=restaurant_id,
                    submitter_id=submitter_id,
                    menu_item_id=menu_item.id,
                    section_name=section_name))
    existing_image = db.session.query(ItemImage).get(
        (item_image, restaurant_id, menu_item.id))
    if existing_image:
        if existing_image.approval_status == ApprovalStatus.rejected:
            existing_image.approval_status = ApprovalStatus.pending
        else:
            raise InvalidUsage(
                "Resubmission of approved or pending image should not be possible!"
            )
    else:
        db.session.add(
            ItemImage(
                restaurant_id=restaurant_id,
                submitter_id=submitter_id,
                menu_item_id=menu_item.id,
                description=description,
                link=item_image))
    db.session.commit()
    return menu_item


def get_restaurant_by_id(restaurant_id):
    return db.session.query(Restaurant).get_or_404(restaurant_id)


def get_restaurant_by_name(restaurant_name):
    return db.session.query(Restaurant)\
        .filter(or_(Restaurant.name.ilike('%%%s%%' % restaurant_name),
                    Restaurant.cuisine_type.ilike('%%%s%%' % restaurant_name))).all()


def get_menu_item_by_id(restaurant_id, menu_item_id):
    return db.session.query(MenuItem)\
    .filter(MenuItem.restaurant_id == restaurant_id)\
    .filter(MenuItem.id == menu_item_id).one()


def get_menu_item_by_name(menu_item_name):
    return db.session.query(MenuItem, ItemImage, Restaurant)\
    .join(ItemImage)\
    .filter(Menuitem.id == ItemImage.menu_item_id) \
    .join(Restaurant)\
    .filter(MenuItem.restaurant_id == Restaurant.id) \
    .filter(MenuItem.name.ilike('%%%s%%' % menu_item_name))\
        .all()


def get_menu_item_by_names(menu_item_names):
    name_filters = [
        MenuItem.name.ilike('%%%s%%' % menu_item_name)
        for menu_item_name in menu_item_names
    ]
    return db.session.query(MenuItem, ItemImage, Restaurant)\
    .join(ItemImage)\
    .filter(MenuItem.id == ItemImage.menu_item_id) \
    .join(Restaurant)\
    .filter(MenuItem.restaurant_id == Restaurant.id) \
    .filter(or_(*name_filters))\
     .all()


def get_menu_section_contents(restaurant_id, section_name):
    return db.session.query(MenuItem, ItemImage) \
        .join(ItemImage) \
        .join(MenuSectionAssignment)\
        .filter(MenuItem.restaurant_id == restaurant_id)\
        .filter(MenuSectionAssignment.section_name == section_name).all()


def get_sectionless_items(restaurant_id):
    return db.session.query(MenuItem, ItemImage) \
        .join(ItemImage)\
        .outerjoin(MenuSectionAssignment)\
        .filter(MenuItem.restaurant_id == restaurant_id)\
        .filter(MenuSectionAssignment.section_name == None).all()


def get_restaurant_menu_items(restaurant_id):
    menu_sections = db.session.query(MenuSection).filter(
        MenuSection.restaurant_id == restaurant_id).all()

    return [(menu_section,
             get_menu_section_contents(restaurant_id, menu_section.name))
            for menu_section in menu_sections
            ] + [(None, get_sectionless_items(restaurant_id))]


def get_all_pending_restaurants():
    return db.session.query(Restaurant, FBUser) \
        .join(FBUser) \
        .filter(Restaurant.submitter_id == FBUser.id) \
        .filter(Restaurant.approval_status == ApprovalStatus.pending) \
        .options(noload('*'))\
        .all()


def get_all_pending_images():
    return db.session.query(MenuItem, ItemImage, FBUser) \
        .join(ItemImage) \
        .join(FBUser) \
        .filter(MenuItem.id == ItemImage.menu_item_id) \
        .filter(ItemImage.submitter_id == FBUser.id) \
        .filter(ItemImage.approval_status == ApprovalStatus.pending) \
        .options(noload('*'))\
        .options(joinedload('section'))\
        .all()


def get_recently_updated_images(updated_since):
    ordered_images = db.session.query(MenuItem, ItemImage, FBUser) \
        .join(ItemImage) \
        .join(FBUser) \
        .filter(MenuItem.id == ItemImage.menu_item_id) \
        .filter(ItemImage.submitter_id == FBUser.id) \
        .options(noload('*'))\
        .options(joinedload('section'))\
        .order_by(ItemImage.updated_at.desc())
    if updated_since:
        return ordered_images.filter(
            ItemImage.updated_at > updated_since).all()
    else:
        return ordered_images.all()


def get_fb_user_by_id(fb_user_id):
    return db.session.query(FBUser).get_or_404(fb_user_id)


def find_user_by_email(email):
    return db.session.query(User).filter(User.email == email).all()
