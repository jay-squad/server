from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.foodie.database.schema import Restaurant, MenuItem

engine = create_engine("postgresql://admin:password@localhost/testdb")
sess = Session(engine)


def insert_restaurant(**kargs):
    assert "id" not in kargs
    sess.add(Restaurant(**kargs))
    sess.commit()


def insert_menu_item(**kargs):
    assert "id" not in kargs
    sess.add(MenuItem(**kargs))
    sess.commit()
