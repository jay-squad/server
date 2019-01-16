import os
from src.foodie.server import APP

APP.run(host='0.0.0.0', port=os.environ['PORT'])