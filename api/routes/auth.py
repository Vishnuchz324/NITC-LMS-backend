from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from api.db import get_db
from api.validate import validate_register_user
from api.decorator import (
    verify_admin_authorization,
    verify_authorization,
    generate_token,
)


bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ROUTES ( base = "/api/auth" )
# [POST]   "/register"    get uset data       -user
# [PATCH]  "/login"       update uset data    -user

# register a new user
@bp.route("/register", methods=["POST"])
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

        user_id = body["userID"]
        user_name = body["userName"]
        password = body["password"]
        phone = body["phoneNo"]
        email = body["email"]
        role = body["role"]

        db, cursor = get_db()
        hashed_password = generate_password_hash(password)
        if role == "librarian":
            # insert into librarian table
            try:
                cursor.execute(
                    "INSERT INTO librarian(employee_ID,lib_name,pwd,phone,email) VALUES (%s,%s,%s,%s,%s)",
                    (user_id, user_name, hashed_password, phone, email),
                )
                db.commit()
            except Exception as e:
                error = e
            if error is None:
                cursor.execute(
                    "SELECT * FROM librarian WHERE employee_ID = %s AND pwd = %s",
                    (user_id, hashed_password),
                )
                user = dict(cursor.fetchone())
                return (
                    jsonify(
                        {
                            "message": f"{user_name} succesfully registered as a {role}",
                            "data": user,
                        }
                    ),
                    200,
                )
        else:
            department = body["dept"].lower()
            # insert into member table
            try:
                cursor.execute(
                    "INSERT INTO members(user_ID,mem_name,pwd,phone,email,dept) VALUES (%s,%s,%s,%s,%s,%s)",
                    (user_id, user_name, hashed_password, phone, email, department),
                )
                db.commit()
            except Exception as e:
                error = e
            if error is None:
                if role == "student":
                    programme = body["programme"].lower()
                    validity = body["validity"]

                    # query to insert details into student table 
                    insert = {
                        "query": "INSERT INTO student(roll_No,validity,programme) VALUES (%s,%s,%s)",
                        "vars": (user_id, validity, programme),
                    }
                    # query to fetch details of the student from the student table and member table
                    fetch = {
                        "query": "SELECT * FROM members mem,student stud WHERE mem.user_ID = stud.roll_no and mem.user_ID = %s AND mem.pwd = %s",
                        "vars": (user_id, hashed_password),
                    }

                elif role == "staff":
                    tflag = True if ("true" or "True") else False

                    # query to insert details of staff into the staff table
                    insert = {
                        "query": "INSERT INTO staff(employee_ID,Tflag) VALUES (%s,%s)",
                        "vars": (user_id, tflag),
                    }
                    # query to fetch details of staff from the staff table and members table
                    fetch = {
                        "query": "SELECT * FROM members mem,staff stf WHERE mem.user_ID = stf.employee_ID and mem.user_ID = %s AND mem.pwd = %s",
                        "vars": (user_id, hashed_password),
                    }
                # inserting user details into respective tables based on roles
                try:
                    cursor.execute(insert["query"], insert["vars"])
                    db.commit()
                except Exception as e:
                    error = e
                if error is None:
                    cursor.execute(fetch["query"], fetch["vars"])
                    user = dict(cursor.fetchone())
                    return (
                        jsonify(
                            {
                                "message": f"{user_name} succesfully registered as a {role}",
                                "data": user,
                            }
                        ),
                        200,
                    )

    return jsonify({"message": f"{error}"}), 400

# login
@bp.route("/login", methods=["POST"])
def login():
    body = request.json

    # {
    #     "userID": "",
    #     "password": "",
    # }

    user_id = str(body["userID"])
    password = str(body["password"])
    db, cursor = get_db()
    isAdmin = False
    error = None
    if not user_id:
        error = "userID is required"
    elif not password:
        error = "password is required"
    else:
        # check if the user is registered as a member
        cursor.execute("SELECT * FROM members WHERE user_ID = %s", (user_id,))
        user = cursor.fetchone()
        if user is None:
            # check if the user is registered as a librarian
            cursor.execute("SELECT * FROM librarian WHERE employee_ID = %s", (user_id,))
            user = cursor.fetchone()
            if user is None:
                error = "userID not registered"
            else:
                isAdmin = True
        if user is not None:
            # check if the password entered is correct
            if not check_password_hash(user["pwd"], password):
                error = "incorrect password"
            else:
                # generate token for the user
                encoded_jwt = generate_token(user_id, isAdmin)
                return (
                    jsonify(
                        {"user_id": user_id, "admin": isAdmin, "token": encoded_jwt}
                    ),
                    200,
                )
    return jsonify({"message": f"{error}"}), 400
