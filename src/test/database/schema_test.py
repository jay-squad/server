from src.foodie.database.schema import BASE
from src.foodie.database import database
from sqlalchemy import create_engine


def test_schema_init():
    engine = create_engine("postgresql://admin:password@localhost/testdb")
    BASE.metadata.drop_all(engine)
    BASE.metadata.create_all(engine)


def test_schema_insert():
    engine = create_engine("postgresql://admin:password@localhost/testdb")
    database.insert_restaurant(name="Soeul Soul", longitude=5, latitude=3)
    database.insert_restaurant(name="Nuri Village", longitude=6, latitude=4)
    database.insert_menu_item(restaurant_id=1, name="Pork Bone Soup")
    database.insert_menu_item(restaurant_id=2, name="Pork Bone Soup")
