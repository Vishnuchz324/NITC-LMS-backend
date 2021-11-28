from flask import Blueprint, request, jsonify, make_response

from api.db import get_db
from api.decorator import verify_admin_authorization, verify_authorization, generate_token


bp = Blueprint('user', __name__, url_prefix='/api/user')


@bp.route("/<id>/borrow/<isbn>", methods=["GET"])
@verify_authorization
def borrow_request(id, isbn):
    db, cursor = get_db()
    cursor.execute("SELECT * FROM book_details WHERE ISBN=%s", (isbn,))
    error = None
    if not cursor.fetchall():
        error = "book not registered"
    if error is None:
        try:
            cursor.execute(
                "INSERT INTO borrowal_request(user_ID,ISBN) VALUES(%s,%s)", (id, isbn))
            return jsonify({"message": f"succesfully added borrowal request for {isbn}"}), 200
        except Exception as e:
            error = str(e)
    return jsonify({"message": error}), 400


@bp.route("/<id>", methods=["GET"])
@verify_authorization
def get_user(id):
    db, cursor = get_db()
    error = None
    cursor.execute("SELECT * FROM members WHERE user_ID = %s", (id,))
    user = dict(cursor.fetchone())
    del user['user_id']
    del user['pwd']
    if(user is None):
        error = "user not registered"
    if(error is None):
        cursor.execute(
            "SELECT * FROM student WHERE roll_No = %s", (id,))
        data = cursor.fetchone()
        role = "student"
        if(data is None):
            try:
                cursor.execute(
                    "SELECT * FROM staff WHERE employee_ID = %s", (id,))
                data = cursor.fetchone()
                role = "staff"
            except Exception as e:
                error = e
        if(data is None):
            error = "the user id entered is incorrect"
        elif(error is None):
            data = dict(data)
            data["role"] = role
            user.update(data)
            return jsonify({"user": user}), 200
    return jsonify({"message": error}), 400


@bp.route("/<id>", methods=["PATCH"])
def update_user_info():
    pass
