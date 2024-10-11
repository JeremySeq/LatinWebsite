"""contains API routes"""

from flask import Blueprint
from passage_routes import passage_routes
from login_routes import login_routes

api = Blueprint('api', __name__)

api.register_blueprint(passage_routes, url_prefix="passages/")
api.register_blueprint(login_routes, url_prefix="login/")
