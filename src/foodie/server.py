'''Simple starter flask app'''
import os
import requests

from flask import Flask, request, jsonify, session, g
from src.foodie.database import database
from src.foodie.database import marshmallow_schema
from src.foodie.database.schema import FBUser
from src.foodie.search import search

import src.foodie.settings.settings  # pylint: disable=unused-import

APP = Flask(__name__)

FB_APP_ID = os.environ["FB_APP_ID"]
FB_APP_SECRET = os.environ["FB_APP_SECRET"]


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class UserNotAuthorized(InvalidUsage):
    def __init__(self):
        InvalidUsage.__init__(
            self,
            "User must be Facebook authenticated to perform this action",
            status_code=403)


@APP.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@APP.route('/restaurant', methods=['POST'])
def upload_restaurant():
    '''new restaurant scheme'''
    if not g.fb_user:
        raise UserNotAuthorized()

    restaurant = database.insert_restaurant(
        submitter_id=g.fb_user['id'],
        **request.form.to_dict())  # TODO request level form validation
    return jsonify(marshmallow_schema.RestaurantSchema().dump(restaurant).data)


@APP.route('/restaurant/<restaurant_id>/section/<name>', methods=['POST'])
def upload_restaurant_menu_section(restaurant_id, name):
    if not g.fb_user:
        raise UserNotAuthorized()
    menu_section = database.insert_menu_section(
        submitter_id=g.fb_user['id'], restaurant_id=restaurant_id, name=name)
    return jsonify(
        marshmallow_schema.MenuSectionSchema().dump(menu_section).data)


@APP.route('/restaurant/<restaurant_id>/item', methods=['POST'])
def upload_menu_item(restaurant_id):
    '''insert a new menu item for a restaurant'''
    if not g.fb_user:
        raise UserNotAuthorized()

    menu_item = database.insert_new_item(
        restaurant_id, submitter_id=g.fb_user['id'],
        **request.form.to_dict())  # TODO request level form validation
    return jsonify(marshmallow_schema.MenuItemSchema().dump(menu_item).data)


@APP.route('/restaurant/<restaurant_id>/item/<menu_item_id>', methods=['PUT'])
def upload_menu_item_images(restaurant_id, menu_item_id):
    if not g.fb_user:
        raise UserNotAuthorized()

    if 'item_image' in request.form:
        for image in request.form.getlist('item_image'):
            database.insert_item_image(
                submitter_id=g.fb_user['id'],
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


@APP.route('/fbuser', methods=['GET'])
def get_fb_user():
    # TODO Jack: Admin auth to use this function
    if not g.fb_user:
        raise UserNotAuthorized()
    fb_user = database.get_fb_user_by_id(g.fb_user['id'])
    return jsonify(marshmallow_schema.FBUserSchema().dump(fb_user))


@APP.route('/fbuser/<fbuser_id>', methods=['GET'])
def get_fb_user_by_id(fbuser_id):
    # TODO Jack: Admin auth to use this function
    fb_user = database.get_fb_user_by_id(fbuser_id)
    return jsonify(marshmallow_schema.FBUserSchema().dump(fb_user))


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
        g.fb_user = session.get("fb_user")
        return

    fb_base_url = "https://graph.facebook.com"
    profile = None

    if os.environ.get("TEST_RUN") == "True":
        user_access_token = "TEST TOKEN"
        profile = dict(
            name="Test User",
            profile_url=None,
            id="1",
        )
    else:
        if not hasattr(g, "access_token"):
            g.access_token = requests.get(
                "{0}/oauth/access_token".format(fb_base_url), {
                    "client_id": FB_APP_ID,
                    "client_secret": FB_APP_SECRET,
                    "grant_type": "client_credentials",
                }).json()["access_token"]

        # Attempt to get the short term access token for the current fb_user.
        if "fb_access_token" in request.cookies:
            user_access_token = request.cookies["fb_access_token"]
            response = requests.get("{0}/me".format(fb_base_url), {
                "access_token": user_access_token,
            })
            if response.ok:
                profile = response.json()

    # If there is no result, we assume the user is not logged in.
    if profile:
        # Check to see if this fb_user is already in our database.
        with database.SESSION_FACTORY.begin():
            fb_user = database.SESSION_FACTORY.query(FBUser).filter(
                FBUser.id == profile["id"]).one_or_none()

            if not fb_user:
                # Not an existing fb_user so get info
                if "link" not in profile:
                    profile["link"] = ""

                # Create the fb_user and insert it into the database
                fb_user = FBUser(
                    id=str(profile["id"]),
                    name=profile["name"],
                    profile_url=profile["link"],
                    access_token=user_access_token)
                database.SESSION_FACTORY.add(fb_user)
            elif fb_user.access_token != user_access_token:
                # If an existing fb_user, update the access token
                fb_user.access_token = user_access_token

            # Add the fb_user to the current session
            session["fb_user"] = dict(
                name=fb_user.name,
                profile_url=fb_user.profile_url,
                id=fb_user.id,
                access_token=fb_user.access_token,
            )

    # Commit changes to the database and set the user as a global g.user
    g.fb_user = session.get("fb_user", None)


APP.secret_key = os.environ['FLASK_SECRET_KEY']
if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=os.environ['PORT'])
