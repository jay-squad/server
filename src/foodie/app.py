from flask import Flask

import os
import src.foodie.settings.settings  # pylint: disable=unused-import

APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = os.environ[
    'HEROKU_POSTGRESQL_CHARCOAL_URL']
