from flask_sqlalchemy import SQLAlchemy
from src.foodie.app import APP

APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(APP)
