from src.foodie.database.schema import BASE
from src.foodie.database import database
from sqlalchemy import create_engine


def test_schema_init():
    BASE.metadata.drop_all(database.ENGINE)
    BASE.metadata.create_all(database.ENGINE)


def test_schema_insert():
    BASE.metadata.drop_all(database.ENGINE)
    BASE.metadata.create_all(database.ENGINE)
    database.insert_restaurant(
        name="Soeul Soul",
        longitude=5,
        latitude=3,
        submitter_id=10211608685952749)
    database.insert_menu_section(
        restaurant_id=1,
        name="Main",
        submitter_id=10211608685952749,
    )
    for _ in range(1):
        database.insert_new_item(
            1,
            "Pork Bone Soup",
            "https://mykoreankitchen.com/wp-content/uploads/2007/01/2.-Pork-Neck-Bone-Soup-Gamjatang.jpg",
            submitter_id=10211608685952749,
            section_name="Main")
