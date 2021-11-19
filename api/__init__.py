from flask import Flask, blueprints, redirect
from dotenv import load_dotenv

from . import db
from . import user


def create_app():
    load_dotenv()
    app = Flask(__name__)
    db.init_app(app)

    @app.route("/", methods=['GET'])
    def get_postman_docs():
        return redirect("https://documenter.getpostman.com/view/15324195/UVCCfjQL")

    app.register_blueprint(user.bp)

    return app
