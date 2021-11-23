from flask import Flask, blueprints, redirect
from dotenv import load_dotenv
from os import environ

from . import db
from api.routes import auth
from api.routes import book
from api.routes import admin


def create_app():
    load_dotenv()
    app = Flask(__name__)
    db.init_app(app)

    @app.route("/", methods=['GET'])
    def demo():
        return str(environ.get('DATABASE_URL'))
    # def get_postman_docs():
    #     return redirect("https://documenter.getpostman.com/view/15324195/UVCCfjQL")

    app.register_blueprint(auth.bp)
    app.register_blueprint(book.bp)
    app.register_blueprint(admin.bp)

    return app
