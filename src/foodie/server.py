'''Simple starter flask app'''
import os

from flask import Flask, request, jsonify, session, g
from src.foodie.database import database
from src.foodie.database import marshmallow_schema
from src.foodie.search import search
import facebook

import src.foodie.settings.settings  # pylint: disable=unused-import

APP = Flask(__name__)

# TODO authentication
FB_APP_ID = os.environ["FB_APP_ID"]
FB_APP_SECRET = os.environ["FB_APP_SECRET"]


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
    return jsonify([{
        "restaurant":
        marshmallow_schema.RestaurantSchema().dump(restaurant).data,
        "menu": [{
            "item":
            marshmallow_schema.MenuItemSchema().dump(item).data,
            "image":
            marshmallow_schema.ItemImageSchema().dump(image).data,
        } for section in database.get_restaurant_menu_items(restaurant.id)
                 for item, image in section[1]][:6]
    } for restaurant in search.find_restaurant(query)])


@APP.route('/search/item/<query>', methods=['GET'])
def search_menu_item(query):
    return jsonify([{
        "item":
        marshmallow_schema.MenuItemSchema().dump(item).data,
        "image":
        marshmallow_schema.ItemImageSchema().dump(image).data
    } for item, image in search.find_menu_item(query)])


@APP.before_request
def get_current_user():
    """Set g.user to the currently logged in user.
    Called before each request, get_current_user sets the global g.user
    variable to the currently logged in user.  A currently logged in user is
    determined by seeing if it exists in Flask's session dictionary.
    If it is the first time the user is logging into this application it will
    create the user and insert it into the database.  If the user is not logged
    in, None will be set to g.user.
    """

    # Set the user in the session dictionary as a global g.user and bail out
    # of this function early.
    if session.get("fb_user"):
        g.fb_user = session.get("user")
        return

    # Attempt to get the short term access token for the current fb_user.
    result = facebook.get_user_from_cookie(
        cookies=request.cookies, app_id=FB_APP_ID, app_secret=FB_APP_SECRET)

    # If there is no result, we assume the user is not logged in.
    if result:
        # Check to see if this fb_user is already in our database.
        fb_user = User.query.filter(User.id == result["uid"]).first()

        with database.SESSION_FACTORY.begin():
            if not fb_user:
                # Not an existing fb_user so get info
                graph = GraphAPI(result["access_token"])
                profile = graph.get_object("me")
                if "link" not in profile:
                    profile["link"] = ""

                # Create the fb_user and insert it into the database
                fb_user = User(
                    id=str(profile["id"]),
                    name=profile["name"],
                    profile_url=profile["link"],
                    access_token=result["access_token"],
                )
                database.SESSION_FACTORY.add(fb_user)
            elif fb_user.access_token != result["access_token"]:
                # If an existing fb_user, update the access token
                fb_user.access_token = result["access_token"]

            # Add the fb_user to the current session
            session["fb_user"] = dict(
                name=fb_user.name,
                profile_url=fb_user.profile_url,
                id=fb_user.id,
                access_token=fb_user.access_token,
            )

    # Commit changes to the database and set the user as a global g.user
    g.fb_user = session.get("user", None)


if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=os.environ['PORT'])
