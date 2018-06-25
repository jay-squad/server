'''Simple starter flask app'''
from flask import Flask, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from src.foodie.database import database

APP = Flask(__name__)


@APP.route('/')
def hello_world():
    '''hello world'''
    return 'Hello, World!'


@APP.route('/upload/', methods=['POST'])
def photo_upload():
    '''upload photo path'''
    print(request.files)
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(filename)
    return redirect(url_for('photo_upload', filename=filename))


@APP.route('/restaurant/', methods=['POST'])  # TODO jack
def insert_restaurant():
    '''new restaurant scheme'''
    print(request)
    return 'Hello world'


@APP.route('/restaurant/', methods=['GET'])  # TODO jack
def get_restaurant_menu():
    '''new restaurant scheme'''
    menu_sections = database.get_restaurant_menu_items(1)
    print(menu_sections)
    return jsonify([{
        "section_name":
        menu_section.name,
        "item_list": [{
            "name": item.name,
            "image": image.link,
        } for item, image in item_list]
    } for menu_section, item_list in menu_sections])


APP.run(host='0.0.0.0')
