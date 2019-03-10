import json
import pytest

from src.foodie.server import APP
from src.foodie.database import database
from src.foodie.database.schema import BASE


@pytest.fixture
def client(request):
    test_client = APP.test_client()
    BASE.metadata.drop_all(database.ENGINE)
    BASE.metadata.create_all(database.ENGINE)

    return test_client


def post_json(client, url, json_dict):
    """Send dictionary json_dict as a json to the specified url """
    return client.post(url, data=json_dict)


def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode('utf8'))


def test_restaurant_insert_json(client):
    response = post_json(
        client, '/restaurant', {
            "cuisine_type": "Sushi",
            "description": None,
            "latitude": 43.4729392,
            "longitude": -80.5375325,
            "name": "Mr Sushi",
            "phone_number": "(226) 647-5525",
            "website": None
        })
    assert response.status_code == 200

    response = post_json(client, '/restaurant/1/section/Main', {})

    assert response.status_code == 200

    response = post_json(
        client, '/restaurant/1/item', {
            "item_name":
            "Pork Bone Soup",
            "item_image":
            "https://mykoreankitchen.com/wp-content/uploads/2007/01/2.-Pork-Neck-Bone-Soup-Gamjatang.jpg",
            "section_name":
            "Main"
        })

    assert response.status_code == 200

    response = post_json(
        client, '/restaurant/1/item', {
            "item_name":
            "Pork Bone Soup",
            "item_image":
            "https://mykoreankitchen.com/wp-content/uploads/2007/01/1.-Gamjatang-Pork-Bone-Soup.jpg",
            "section_name":
            "Main"
        })

    assert response.status_code == 200
