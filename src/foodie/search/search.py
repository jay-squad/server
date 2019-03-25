from src.foodie.database import database
import requests


def find_contains(query):
    query_url = "https://api.datamuse.com/words?ml=dish+{0}".format(query)
    response = requests.get(query_url)
    if response.status_code == 200:
        return [w["word"] for w in response.json() if w["score"] > 20000]
    else:
        return []


def find_restaurant(query):  # TODO accept metadata parameters
    return database.get_restaurant_by_name(query)


def find_menu_item(query):
    return database.get_menu_item_by_names([query] + find_contains(query))
