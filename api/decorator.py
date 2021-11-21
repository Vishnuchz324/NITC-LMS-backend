from functools import wraps
from flask import request, jsonify, current_app
import jwt
import os
JWT_SECRET = os.getenv('JWT_SECRET')


def generate_token(userId, isAdmin):
    encoded_jwt = jwt.encode(
        {"userID": str(userId), "isAdmin": isAdmin}, JWT_SECRET, algorithm="HS256")
    return encoded_jwt


def add_app_context(f):
    @wraps(f)
    def create_app_context(*args, **kwargs):
        with current_app.app_context():
            return f(*args, **kwargs)
    return create_app_context


def verify_token(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.headers.get("authorization")
        if not token:
            return jsonify({"message": "user not authenticated"}), 400
        encoded_jwt = token.split()[1]
        try:
            user = jwt.decode(
                encoded_jwt, JWT_SECRET, algorithms=["HS256"]
            )
            request.user = user
        except Exception as e:
            return jsonify({"message": "user authentication invalid"}), 400
        return f(*args, **kwargs)
    return wrapped


def verify_authorization(f):
    @wraps(f)
    @verify_token
    def user_authorization(*args, **kwargs):
        isUser = request.view_args["id"] == request.user["userID"]
        isAdmin = request.user["isAdmin"]
        if not (isUser or isAdmin):
            return jsonify({"message": "user not allowed"}), 400
        return f(*args, **kwargs)
    return user_authorization


def verify_admin_authorization(f):
    @wraps(f)
    @verify_token
    def admin_authorization(*args, **kwargs):
        if not request.user["isAdmin"]:
            return jsonify({"message": "you are not an admin"}), 400
        return f(*args, **kwargs)
    return admin_authorization
