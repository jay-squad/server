from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.foodie.database.schema import Restaurant, MenuSection, MenuItem, MenuSectionAssignment, ItemImage

engine = create_engine("postgresql://admin:password@localhost/testdb")
sess = Session(engine)


def insert_restaurant(**kargs):
    assert "id" not in kargs
    sess.add(Restaurant(**kargs))
    sess.commit()


def insert_menu_section(**kargs):
    sess.add(MenuSection(**kargs))
    sess.commit()


def insert_menu_item(**kargs):
    assert "id" not in kargs
    sess.add(MenuItem(**kargs))
    sess.commit()


def insert_menu_section_assignment(**kargs):
    sess.add(MenuSectionAssignment(**kargs))
    sess.commit()


def insert_item_image(**kargs):
    sess.add(ItemImage(**kargs))
    sess.commit()


def insert_new_item(restaurant_id, item_name, item_image, section_name=None):
    menu_item = MenuItem(restaurant_id=restaurant_id, name=item_name)
    sess.add(menu_item)
    sess.flush()
    sess.add(
        ItemImage(
            restaurant_id=restaurant_id,
            menu_item_id=menu_item.id,
            link=item_image))
    if section_name is not None:
        sess.add(
            MenuSectionAssignment(
                restaurant_id=restaurant_id,
                menu_item_id=menu_item.id,
                section_name=section_name))
    sess.commit()


def get_menu_section(restaurant_id, section_name):
    return sess.query(MenuItem, ItemImage) \
        .filter(MenuItem.restaurant_id == restaurant_id) \
        .filter(ItemImage.restaurant_id == restaurant_id) \
        .filter(ItemImage.menu_item_id == MenuItem.id) \
        .filter(MenuSectionAssignment.menu_item_id == MenuItem.id) \
        .filter(MenuSectionAssignment.restaurant_id == restaurant_id) \
        .filter(MenuSectionAssignment.section_name == section_name).all()


def get_restaurant_menu_items(restaurant_id):
    menu_sections = sess.query(MenuSection).filter(
        MenuSection.restaurant_id == restaurant_id).all()
    return [(menu_section, get_menu_section(restaurant_id, menu_section.name))
            for menu_section in menu_sections]
