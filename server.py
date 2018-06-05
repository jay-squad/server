'''Simple starter flask app'''
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
import database

database.import_restaurant()
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


@APP.route('/new/restaurant/', methods=['POST'])
def new_restaurant():
    '''new restaurant scheme'''
    print(request)
    return 'Hello world'


# APP.run(host='0.0.0.0')
