from src.foodie.database.schema import BASE
from src.foodie.database import database
from sqlalchemy import create_engine
from flask import jsonify


def test_schema_init():
    engine = create_engine("postgresql://admin:password@localhost/testdb")
    BASE.metadata.drop_all(engine)
    BASE.metadata.create_all(engine)


def test_schema_insert():
    database.insert_restaurant(name="Soeul Soul", longitude=5, latitude=3)
    database.insert_menu_section(restaurant_id=1, name="Main")
    for _ in range(20):
        database.insert_new_item(
            1,
            "Pork Bone Soup",
            "https://mykoreankitchen.com/wp-content/uploads/2007/01/2.-Pork-Neck-Bone-Soup-Gamjatang.jpg",
            section_name="Main")
