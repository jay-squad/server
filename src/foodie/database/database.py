import os
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from src.foodie.database.schema import Restaurant, MenuSection, MenuItem, MenuSectionAssignment, ItemImage

import src.foodie.settings.settings  # pylint: disable=unused-import

engine = create_engine(os.environ['DATABASE_URL'])
session_factory = sessionmaker(bind=engine, autocommit=True)()


def _add_and_commit(model):
    session = scoped_session(session_factory)()
    session.add(model)
    return model


def insert_restaurant(**kargs):
    assert "id" not in kargs
    return _add_and_commit(Restaurant(**kargs))


def insert_menu_section(**kargs):
    return _add_and_commit(MenuSection(**kargs))


def insert_menu_item(**kargs):
    assert "id" not in kargs
    return _add_and_commit(MenuItem(**kargs))


def insert_menu_section_assignment(**kargs):
    return _add_and_commit(MenuSectionAssignment(**kargs))


def insert_item_image(**kargs):
    return _add_and_commit(ItemImage(**kargs))


def insert_new_item(restaurant_id,
                    item_name,
                    item_image,
                    description=None,
                    price=None,
                    section_name=None):
    session = scoped_session(session_factory)()
    menu_item = MenuItem(
        restaurant_id=restaurant_id,
        name=item_name,
        price=price,
        description=description)
    session.add(menu_item)
    session.flush()
    session.add(
        ItemImage(
            restaurant_id=restaurant_id,
            menu_item_id=menu_item.id,
            link=item_image))
    if section_name is not None:
        session.add(
            MenuSectionAssignment(
                restaurant_id=restaurant_id,
                menu_item_id=menu_item.id,
                section_name=section_name))
    return menu_item


def get_restaurant_by_id(restaurant_id):
    session = scoped_session(session_factory)()
    return session.query(Restaurant)\
        .filter(Restaurant.id == restaurant_id).one()


def get_restaurant_by_name(restaurant_name):
    session = scoped_session(session_factory)()
    return session.query(Restaurant)\
        .filter(or_(Restaurant.name.ilike('%%%s%%' % restaurant_name), Restaurant.cuisine_type.ilike('%%%s%%' % restaurant_name))).all()


def get_menu_item_by_id(restaurant_id, menu_item_id):
    session = scoped_session(session_factory)()
    return session.query(MenuItem)\
    .filter(MenuItem.restaurant_id == restaurant_id)\
    .filter(MenuItem.id == menu_item_id).one()


def get_menu_item_by_name(menu_item_name):
    session = scoped_session(session_factory)()
    return session.query(MenuItem, ItemImage)\
    .filter(MenuItem.name.ilike('%%%s%%' % menu_item_name))\
        .join(ItemImage).all()


def get_menu_section(restaurant_id, section_name):
    session = scoped_session(session_factory)()
    return session.query(MenuItem, ItemImage) \
        .join(ItemImage) \
        .join(MenuSectionAssignment)\
        .filter(MenuItem.restaurant_id == restaurant_id)\
        .filter(MenuSectionAssignment.section_name == section_name).all()


def get_sectionless_items(restaurant_id):
    session = scoped_session(session_factory)()
    return session.query(MenuItem, ItemImage) \
        .join(ItemImage)\
        .outerjoin(MenuSectionAssignment)\
        .filter(MenuItem.restaurant_id == restaurant_id)\
        .filter(MenuSectionAssignment.section_name is None).all()


def get_restaurant_menu_items(restaurant_id):
    session = scoped_session(session_factory)()
    menu_sections = session.query(MenuSection).filter(
        MenuSection.restaurant_id == restaurant_id).all()

    return [(menu_section, get_menu_section(restaurant_id, menu_section.name))
            for menu_section in menu_sections
            ] + [(None, get_sectionless_items(restaurant_id))]
