from . import db
from flask import Flask

def create_app():
    app = Flask(__name__)
    db.init_app(app)
    return app

