from flask import Flask

import os
import src.foodie.settings.settings  # pylint: disable=unused-import

APP = Flask(__name__)
APP.secret_key = os.environ['FLASK_SECRET_KEY']
APP.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# SESSION_TYPE = 'sqlalchemy'
