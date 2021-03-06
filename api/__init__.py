from flask import Flask, blueprints, redirect
from flask_cors import CORS
from dotenv import load_dotenv

from . import db
from api.routes import auth
from api.routes import book
from api.routes import admin
from api.routes import user


def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)
    db.init_app(app)

    @app.route("/", methods=['GET'])
    def get_postman_docs():
        return redirect("https://documenter.getpostman.com/view/15324195/UVCCfjQL")

    app.register_blueprint(auth.bp)
    app.register_blueprint(book.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(admin.bp)

    return app
