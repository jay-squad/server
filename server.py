'''Simple starter flask app'''
from flask import Flask
APP = Flask(__name__)


@APP.route('/')
def hello_world():
    '''hello world'''
    return 'Hello, World!'


APP.run(host='0.0.0.0')
