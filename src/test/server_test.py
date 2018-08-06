from src.foodie.server import APP
from flask import request
import json
import pytest


@pytest.fixture
def client(request):
    test_client = APP.test_client()

    def teardown():
        pass

    request.addfinalizer(teardown)
    return test_client


def post_json(client, url, json_dict):
    """Send dictionary json_dict as a json to the specified url """
    return client.post(url, json=json.dumps(json_dict))


def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode('utf8'))


def test_json(client):
    response = post_json(
        client, '/restaurant', {
            "cuisine_type": "Sushi",
            "description": None,
            "id": 5,
            "latitude": 43.4729392,
            "longitude": -80.5375325,
            "name": "Mr Sushi",
            "normalized_name": "Mr Sushi",
            "phone_number": "(226) 647-5525",
            "website": None
        })
    assert response.status_code == 200
    print(response)
