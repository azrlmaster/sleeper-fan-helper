from flask import Blueprint

main = Blueprint('main', __name__,
                template_folder='templates',
                static_folder='static',
                static_url_path='/static/main')

# Import the routes to ensure they are registered with the blueprint
from . import routes
