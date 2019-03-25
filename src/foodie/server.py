'''Simple starter flask app'''
import os
import requests
import uuid

from flask import Flask, request, jsonify, g, Response
from src.foodie.database import database
from src.foodie.database import marshmallow_schema
from src.foodie.database.schema import *
from src.foodie.search import search
from src.foodie.app import APP
from src.foodie.database.db import db
from src.foodie.exceptions.exceptions import *
from itertools import groupby

import src.foodie.settings.settings  # pylint: disable=unused-import

FB_APP_ID = os.environ["FB_APP_ID"]
FB_APP_SECRET = os.environ["FB_APP_SECRET"]

#TODO Jack: replace get_or_404 tuples with dicts

#TODO Jack: This is kinda wonky, but flask Session doesn't actually do what we want it to
# do
session = {}


def ensure_proper_submitter_for_delete(submitter_id):
    if g.is_admin:
        return

    if not g.fb_user:
        raise UserNotFacebookAuthed()

    if g.fb_user['id'] != submitter_id:
        raise InvalidUsage(
            "User may not edit other user's submissions!", status_code=403)


def submitter_id_or_error():
    if g.fb_user:
        return g.fb_user['id']
    elif g.is_admin:
        return 1
    else:
        raise UserNotFacebookAuthed()


def approved_or_admin(item_image):
    return g.is_admin or item_image.approval_status == ApprovalStatus.approved


@APP.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@APP.errorhandler(IntegrityError)
def handle_integrity_error(error):
    return jsonify({
        "message":
        str(error),
        "info":
        "You are likely seeing this, because you attempted to associate an update with a foreign key that does not exist",
        "status_code":
        400
    })


@APP.route('/restaurant', methods=['POST'])
def upload_restaurant():
    '''new restaurant scheme'''
    restaurant = database.insert_restaurant(
        submitter_id=submitter_id_or_error(),
        **request.form)  # TODO request level form validation
    return jsonify(marshmallow_schema.RestaurantSchema().dump(restaurant).data)


@APP.route('/restaurant/<restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    if not g.is_admin:
        raise UserNotAdmin()

    restaurant = database.get_restaurant_by_id(restaurant_id)
    db.session.delete(restaurant)
    db.session.commit()
    return jsonify(success=True)


@APP.route('/restaurant/<restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    return jsonify(marshmallow_schema.RestaurantSchema().dump(
        database.get_restaurant_by_id(restaurant_id)).data)


@APP.route('/restaurant/<restaurant_id>', methods=['PUT'])
def update_restaurant(restaurant_id):
    restaurant = database.get_restaurant_by_id(restaurant_id)
    ensure_proper_submitter_for_delete(restaurant.submitter_id)

    if not g.is_admin and restaurant.approval_status == ApprovalStatus.approved:
        raise InvalidUsage(
            "User may not update a restaurant that was already approved!")

    for k, v in request.form.items():
        setattr(restaurant, k, v)

    if g.is_admin and "approval_status" in request.form:
        if request.form['approval_status'] == "approved":
            fbuser = db.session.query(FBUser).get_or_404(
                restaurant.submitter_id)
            fbuser.points = fbuser.points + 50
    elif not g.is_admin:
        restaurant.approval_status = ApprovalStatus.pending

    db.session.commit()
    return jsonify(marshmallow_schema.RestaurantSchema().dump(restaurant).data)


def get_restaurant_menu_items(restaurant_id):
    menu_sections = database.get_restaurant_menu_items(restaurant_id)
    section_list = [(menu_section.name if menu_section is not None else '',
                     [(marshmallow_schema.MenuItemSchema().dump(item).data,
                       marshmallow_schema.ItemImageSchema().dump(image).data)
                      for item, image in item_list
                      if approved_or_admin(image)])
                    for menu_section, item_list in menu_sections]
    grouped_sections = []
    for menu_section, item_list in section_list:
        grouped_items = {}
        for item, item_image in item_list:
            if item['name'] in grouped_items:
                grouped_items[item['name']]['item_images'].append(item_image)
            else:
                grouped_items[item['name']] = {
                    'item': item,
                    'item_images': [item_image]
                }
        grouped_sections.append([menu_section, list(grouped_items.values())])
    return grouped_sections


@APP.route('/restaurant/<restaurant_id>/menu', methods=['GET'])
def get_restaurant_menu(restaurant_id):
    '''get a specific restaurant item scheme'''
    return jsonify(get_restaurant_menu_items(restaurant_id))


@APP.route('/restaurant/<restaurant_id>/section/<name>', methods=['POST'])
def upload_restaurant_menu_section(restaurant_id, name):
    menu_section = database.insert_menu_section(
        submitter_id=submitter_id_or_error(),
        restaurant_id=restaurant_id,
        name=name)
    return jsonify(
        marshmallow_schema.MenuSectionSchema().dump(menu_section).data)


@APP.route('/restaurant/<restaurant_id>/section/<name>', methods=['DELETE'])
def delete_restaurant_menu_section(restaurant_id, name):
    if not g.is_admin:
        raise UserNotAdmin()
    menu_section = db.session.query(MenuSection).get_or_404((restaurant_id,
                                                             name))
    db.session.delete(menu_section)
    db.session.commit()
    return jsonify(success=True)


@APP.route('/restaurant/<restaurant_id>/section/<name>', methods=['PUT'])
def update_restaurant_menu_section(restaurant_id, name):
    if not g.is_admin:
        raise UserNotAdmin()

    menu_section = db.session.query(MenuSection).get_or_404((restaurant_id,
                                                             name))
    for k, v in request.form.items():
        setattr(menu_section, k, v)
    db.session.commit()
    return jsonify(
        marshmallow_schema.MenuSectionSchema().dump(menu_section).data)


@APP.route('/restaurant/<restaurant_id>/item', methods=['POST'])
def upload_menu_item(restaurant_id):
    '''insert a new menu item for a restaurant'''
    menu_item = database.insert_new_item(
        restaurant_id, submitter_id=submitter_id_or_error(),
        **request.form)  # TODO request level form validation
    return jsonify(marshmallow_schema.MenuItemSchema().dump(menu_item).data)


@APP.route('/restaurant/<restaurant_id>/item/<menu_item_id>', methods=['PUT'])
def update_menu_item(restaurant_id, menu_item_id):
    if not g.is_admin:
        raise UserNotAdmin()
    menu_item = db.session.query(MenuItem).get_or_404((restaurant_id,
                                                       menu_item_id))
    for k, v in request.form.items():
        setattr(menu_item, k, v)
    db.session.commit()
    return jsonify(marshmallow_schema.MenuItemSchema().dump(menu_item).data)


@APP.route(
    '/restaurant/<restaurant_id>/item/<menu_item_id>/section', methods=['PUT'])
def update_menu_item_section(restaurant_id, menu_item_id):
    if not g.is_admin:
        raise UserNotAdmin()

    if not "section_name" in request.form:
        raise InvalidUsage("New section name not provided!", status_code=400)

    section_name = request.form["section_name"]
    menu_section_assignment = db.session.query(MenuSectionAssignment) \
                              .filter(MenuSectionAssignment.restaurant_id == restaurant_id) \
                              .filter(MenuSectionAssignment.menu_item_id == menu_item_id) \
                              .first() # Assuming single entry per menuitem right now

    if not menu_section_assignment:
        database.insert_menu_section_assignment(
            restaurant_id=restaurant_id,
            menu_item_id=menu_item_id,
            section_name=section_name)

    else:
        menu_section_assignment.section_name = section_name
    db.session.commit()
    return jsonify(success=True)


@APP.route(
    '/restaurant/<restaurant_id>/item/<menu_item_id>', methods=['DELETE'])
def delete_restaurant_menu_item(restaurant_id, menu_item_id):
    if not g.is_admin:
        raise UserNotAdmin()

    menu_item = db.session.query(MenuItem).get_or_404((restaurant_id,
                                                       menu_item_id))
    db.session.delete(menu_item)
    db.session.commit()
    return jsonify(success=True)


@APP.route(
    '/restaurant/<restaurant_id>/item/<menu_item_id>/image',
    methods=['DELETE'])
def delete_menu_item_image(restaurant_id, menu_item_id):
    if not 'item_image' in request.form:
        raise InvalidUsage("Item image not provided!", status_code=400)
    link = request.form['item_image']
    item_image = db.session.query(ItemImage).get_or_404((link, restaurant_id,
                                                         menu_item_id))
    ensure_proper_submitter_for_delete(item_image.submitter_id)
    db.session.delete(item_image)
    db.session.commit()
    return jsonify(success=True)


@APP.route(
    '/restaurant/<restaurant_id>/item/<menu_item_id>/image', methods=['PUT'])
def update_item_image_approval(restaurant_id, menu_item_id):
    if not g.is_admin:
        raise UserNotAdmin()
    link = request.form['item_image']
    item_image = db.session.query(ItemImage).get_or_404((link, restaurant_id,
                                                         menu_item_id))
    item_image.approval_status = request.form['approval_status']

    if request.form['approval_status'] == "approved":
        fbuser = db.session.query(FBUser).get_or_404(item_image.submitter_id)
        fbuser.points = fbuser.points + 50
    db.session.commit()
    return jsonify(success=True)


def group_submissions_by_request_uuid(fb_user):
    fb_user_ = fb_user.data
    submission_types = [
        'submitted_restaurants', 'submitted_menu_sections', 'submitted_items',
        'submitted_item_images'
    ]
    submissions = [
        i for j in [[(type_, k) for k in fb_user_[type_]]
                    for type_ in submission_types] for i in j
    ]
    grouped_submissions = [
        list(g) for k, g in groupby(
            sorted(submissions, key=lambda x: x[1]['request_uuid']),
            lambda x: x[1]['request_uuid'])
    ]
    fb_user_['submissions'] = grouped_submissions
    for submission_type in submission_types:
        del fb_user_[submission_type]


def get_fb_user_information(fb_user_id):
    fb_user = database.get_fb_user_by_id(fb_user_id)
    fb_user = marshmallow_schema.FBUserSchema().dump(fb_user)
    group_submissions_by_request_uuid(fb_user)
    return jsonify(fb_user)


@APP.route('/fbuser', methods=['GET'])
def get_fb_user():
    if not g.fb_user:
        raise UserNotFacebookAuthed()
    return get_fb_user_information(g.fb_user['id'])


@APP.route('/fbuser/<fb_user_id>', methods=['GET'])
def get_fb_user_by_id(fb_user_id):
    if not g.is_admin:
        raise UserNotAdmin()
    return get_fb_user_information(fb_user_id)


def get_results_key(request_uuid):
    return "results_" + str(request_uuid)


def paginate_results(results, pagination_limit):
    results_key = get_results_key(g.request_uuid)
    session[results_key] = results[pagination_limit:]
    return {
        "results": results[:pagination_limit],
        "next": results_key if results[pagination_limit:] else None
    }


def query_restaurants(query, pagination_limit):
    restaurant_menu_pairs = [{
        "restaurant":
        marshmallow_schema.RestaurantSchema().dump(restaurant).data,
        "menu":
        get_restaurant_menu_items(restaurant.id)
    } for restaurant in search.find_restaurant(query)
                             if approved_or_admin(restaurant)]

    restaurant_menu_pairs = sorted(
        restaurant_menu_pairs, key=lambda r: len(r["menu"]), reverse=True)
    restaurant_menu_pairs = [{
        "restaurant": restaurant_menu_pair["restaurant"],
        "menu": restaurant_menu_pair["menu"][:6]
    } for restaurant_menu_pair in restaurant_menu_pairs]

    if pagination_limit:
        return paginate_results(restaurant_menu_pairs, int(pagination_limit))
    else:
        return restaurant_menu_pairs


@APP.route('/search/restaurant/', methods=['GET'])
@APP.route('/search/restaurant', methods=['GET'])
def search_all_restaurant():
    return jsonify(query_restaurants("", request.form.get("pagination_limit")))


@APP.route('/search/restaurant/<query>', methods=['GET'])
def search_restaurant(query):
    return jsonify(
        query_restaurants(query, request.form.get("pagination_limit")))


def query_items(query, pagination_limit):
    item_image_pairs = [{
        "item":
        marshmallow_schema.MenuItemSchema().dump(item).data,
        "image":
        marshmallow_schema.ItemImageSchema().dump(image).data
    } for item, image in search.find_menu_item(query)
                        if approved_or_admin(image)]
    if pagination_limit:
        return paginate_results(item_image_pairs, int(pagination_limit))
    else:
        return item_image_pairs


@APP.route('/search/item/', methods=['GET'])
@APP.route('/search/item', methods=['GET'])
def search_all_menu_item():
    return jsonify(query_items("", request.form.get("pagination_limit")))


@APP.route('/search/item/<query>', methods=['GET'])
def search_menu_item(query):
    return jsonify(query_items(query, request.form.get("pagination_limit")))


@APP.route('/pending/restaurant', methods=['GET'])
def get_pending_restaurants():
    if not g.is_admin:
        raise UserNotAdmin()

    return jsonify([{
        "restaurant":
        marshmallow_schema.RestaurantSchema().dump(restaurant).data,
        "submitter":
        marshmallow_schema.FBUserSchemaNoSubmissions().dump(submitter).data
    } for restaurant, submitter in database.get_all_pending_restaurants()])


@APP.route('/image/pending', methods=['GET'])
@APP.route('/pending/image', methods=['GET'])
def get_pending_images():
    if not g.is_admin:
        raise UserNotAdmin()

    return jsonify([{
        "item":
        marshmallow_schema.MenuItemSchema().dump(item).data,
        "image":
        marshmallow_schema.ItemImageSchema().dump(image).data,
        "submitter":
        marshmallow_schema.FBUserSchemaNoSubmissions().dump(submitter).data
    } for item, image, submitter in database.get_all_pending_images()])


@APP.route('/image/recent', methods=['GET'])
def get_recently_updated_images():
    if not g.is_admin:
        raise UserNotAdmin()

    if "updated_since" in request.args:
        updated_since = datetime.datetime.utcfromtimestamp(
            int(request.args["updated_since"]))
    else:
        updated_since = None

    return jsonify([{
        "item":
        marshmallow_schema.MenuItemSchema().dump(item).data,
        "image":
        marshmallow_schema.ItemImageSchema().dump(image).data,
        "submitter":
        marshmallow_schema.FBUserSchemaNoSubmissions().dump(submitter).data
    } for item, image, submitter in database.get_recently_updated_images(
        updated_since)])


@APP.route('/suggest_amendment', methods=['POST'])
def suggest_amendment():
    amendment = Amendment(**request.form, submitter_id=submitter_id_or_error())
    database._add_and_commit(amendment)
    return jsonify(success=True)


@APP.route('/pagination/next', methods=['GET'])
def pagination_next():
    if not "next" in request.form:
        raise InvalidUsage("No results key provided")

    results_key = request.form["next"]
    if results_key in session:
        results = session[results_key]
        pagination_limit = request.form.get("pagination_limit")
        if pagination_limit:
            return jsonify(paginate_results(results, int(pagination_limit)))
        else:
            return jsonify(results)
    else:
        raise InvalidUsage("Last query does not exist", status_code=404)


@APP.route('/blob/<key>', methods=['GET'])
def get_blob(key):
    return Response(
        db.session.query(Blob).get_or_404(key).data,
        content_type='application/json ')


@APP.before_request
def generate_request_uuid():
    g.request_uuid = uuid.uuid4()


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

    # TODO Jack actually figure out how sessions work
    # if session.get("fb_user"):
    #     g.fb_user = session.get("fb_user")
    #     return

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
        fb_user = db.session.query(FBUser).filter(
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
            db.session.add(fb_user)
            db.session.commit()
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


@APP.before_request
def auth_admin():
    request.form = request.form.to_dict()
    if "admin_secret_key" in request.cookies and os.environ['ADMIN_SECRET_KEY'] == request.cookies["admin_secret_key"]:
        g.is_admin = True
    elif "admin_secret_key" in request.form and os.environ['ADMIN_SECRET_KEY'] == request.form['admin_secret_key']:
        del request.form['admin_secret_key']
        g.is_admin = True
    else:
        g.is_admin = False


if __name__ == "__main__":
    APP.run(host='0.0.0.0', port=os.environ['PORT'])
