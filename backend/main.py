"""Main Flask Application"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from api import api
import db


def create_app():
    """Creates the Flask application with configurations"""

    app = Flask(__name__)

    load_dotenv()
    app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///translations.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # Create database tables
    with app.app_context():
        db.setup_db(app).create_all()

    CORS(app)

    # register blueprints
    app.register_blueprint(api, url_prefix="/api/")

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
