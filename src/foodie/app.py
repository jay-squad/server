from flask import Flask

import os
import src.foodie.settings.settings  # pylint: disable=unused-import

APP = Flask(__name__)
APP.secret_key = os.environ['FLASK_SECRET_KEY']
APP.config['SQLALCHEMY_DATABASE_URI'] = os.environ[
    'HEROKU_POSTGRESQL_CHARCOAL_URL']

# SESSION_TYPE = 'sqlalchemy'
APP.config.from_object(__name__)
