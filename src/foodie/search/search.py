from src.foodie.database import database


def find_restaurant(query):  # TODO accept metadata parameters
    return database.get_restaurant_by_name(query)


def find_menu_item(query):
    return database.get_menu_item_by_name(query)
