from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash

from api.db import get_db
from api.validate import validate_register_user
from api.decorator import verify_admin_authorization, verify_authorization, generate_token


bp = Blueprint('auth', __name__, url_prefix='/api/user')


@bp.route("/register", methods=['GET', 'POST'])
def register():
    body = request.json

    # {
    #     "userID": "",
    #     "userName": "",
    #     "password": "",
    #     "phoneNo": "",
    #     "email": "",
    #     "dept": "",
    #     "role":"",
    #     "tFlag": "",
    #     "programme": "",
    #     "validity": "",
    # }

    error = validate_register_user(body)
    if error is None:

        user_id = body['userID']
        user_name = body['userName']
        password = body['password']
        phone = body['phoneNo']
        email = body['email']
        department = body['dept'].upper()
        role = body['role']
        tflag = eval(body['tFlag'].capitalize())
        programme = body['programme'].upper()
        validity = body['validity']

        db, cursor = get_db()
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO member(user_id,name,password,phone,email,dept,role) VALUES (%s,%s,%s,%s,%s,%s,%s)", (
                user_id, user_name, hashed_password, phone, email, department, role)
        )
        db.commit()
        cursor.execute(
            "SELECT * FROM member WHERE user_id = %s AND password = %s", (user_id, hashed_password))
        user = dict(cursor.fetchone())
        return jsonify(user), 200
    return jsonify({"message": f"{error}"}), 400


@bp.route("/login", methods=['GET', 'POST'])
def login():
    body = request.json

    # {
    #     "userID": "",
    #     "password": "",
    # }

    user_id = str(body['userID'])
    password = str(body['password'])
    db, cursor = get_db()
    error = None
    if not user_id:
        error = "userID is required"
    elif not password:
        error = "password is required"
    else:
        cursor.execute(
            "SELECT * FROM member WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if user is None:
            error = "userID not registered"
        else:
            if not check_password_hash(user['password'], password):
                # if user['password'] != password:
                error = "incorrect password"
            else:
                # cursor.execute(
                #     "SELECT * FROM librarian WHERE userID = %s", (user['id'],))
                isAdmin = False
                # if(cursor.fetchone()):
                #     isAdmin = True
                encoded_jwt = generate_token(user["user_id"], isAdmin)
                return jsonify({"token": encoded_jwt}), 200
    return jsonify({"message": f"{error}"}), 400
