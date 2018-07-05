'''Simple starter flask app'''
import os
from flask import Flask, request, jsonify
from src.foodie.database import database
from src.foodie.database import marshmallow_schema
from src.foodie.search import search
import src.foodie.settings.settings  # pylint: disable=unused-import

APP = Flask(__name__)

# TODO authentication


@APP.route('/restaurant', methods=['POST'])
def insert_restaurant():
    '''new restaurant scheme'''
    restaurant = database.insert_restaurant(
        **request.form.to_dict())  # TODO request level form validation
    return jsonify(marshmallow_schema.RestaurantSchema().dump(restaurant).data)


@APP.route('/restaurant/<restaurant_id>/section/<name>', methods=['POST'])
def insert_restaurant_menu_section(restaurant_id, name):
    menu_section = database.insert_menu_section(
        restaurant_id=restaurant_id, name=name)
    return jsonify(
        marshmallow_schema.MenuSectionSchema().dump(menu_section).data)


@APP.route('/restaurant/<restaurant_id>/item', methods=['POST'])
def insert_menu_item(restaurant_id):
    '''insert a new menu item for a restaurant'''
    menu_item = database.insert_new_item(
        restaurant_id,
        **request.form.to_dict())  # TODO request level form validation
    return jsonify(marshmallow_schema.MenuItemSchema().dump(menu_item).data)


@APP.route('/restaurant/<restaurant_id>/item/<menu_item_id>', methods=['PUT'])
def upload_menu_item_images(restaurant_id, menu_item_id):
    if 'item_image' in request.form:
        for image in request.form.getlist('item_image'):
            database.insert_item_image(
                restaurant_id=restaurant_id,
                menu_item_id=menu_item_id,
                link=image)
    return database.get_menu_item_by_id(restaurant_id, menu_item_id)


@APP.route('/restaurant/<restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    return jsonify(marshmallow_schema.RestaurantSchema().dump(
        database.get_restaurant_by_id(restaurant_id)).data)


@APP.route('/restaurant/<restaurant_id>/menu', methods=['GET'])
def get_restaurant_menu(restaurant_id):
    '''get a specific restaurant item scheme'''
    menu_sections = database.get_restaurant_menu_items(restaurant_id)
    return jsonify([(menu_section.name if menu_section is not None else '', [{
        "item":
        marshmallow_schema.MenuItemSchema().dump(item).data,
        "image":
        marshmallow_schema.ItemImageSchema().dump(image).data,
    } for item, image in item_list])
                    for menu_section, item_list in menu_sections])


@APP.route('/search/restaurant/<query>', methods=['GET'])
def search_restaurant(query):
    return jsonify([
        marshmallow_schema.RestaurantSchema().dump(restaurant).data
        for restaurant in search.find_restaurant(query)
    ])


@APP.route('/search/item/<query>', methods=['GET'])
def search_menu_item(query):
    return jsonify([{
        "item":
        marshmallow_schema.MenuItemSchema().dump(item).data,
        "image":
        marshmallow_schema.ItemImageSchema().dump(image).data
    } for item, image in search.find_menu_item(query)])


APP.run(host='0.0.0.0', port=os.environ['PORT'])
