from flask import Blueprint, request, jsonify, make_response

from api.db import get_db
from api.routes.book import get_book
from api.decorator import (
    verify_admin_authorization,
    verify_authorization,
    generate_token,
)


bp = Blueprint("user", __name__, url_prefix="/api/user")

# ROUTES ( base = "/api/user" )
# [GET]    "/<id>"               get uset data              -user
# [PATCH]  "/<id>"               update uset data           -user
# [GET]    "/<id>/borrow?isbn="  put a borrow request       -user
# [GET]    "/<id>/borrowed"      view all borrowed books    -user
# [POST]   "/<id>/request"       request a new book         -user


# get the user data
# passed on <id> as a dynamic parameter and verified using jwt token
@bp.route("/<id>", methods=["GET"])
@verify_authorization
def get_user(id):
    db, cursor = get_db()
    role = request.args.get("role")
    if role == "admin":
        try:
            cursor.execute("SELECT * FROM librarian WHERE employee_ID = %s", (id,))
            user = dict(cursor.fetchone())
            user["user_id"] = user["employee_id"]
            user["mem_name"] = user["lib_name"]
            user["role"] = "librarian"
        except Exception as e:
            return jsonify({"message": str(e)}), 400
        return jsonify({"user": user}), 200
    error = None
    # fetch the user data from the members table if exists
    cursor.execute("SELECT * FROM members WHERE user_ID = %s", (id,))
    user = dict(cursor.fetchone())
    # deleting unwanted keys that neednt be shared with the client
    del user["pwd"]
    # raise an error if there is no entry for the particular userID
    if user is None:
        error = "user not registered"
    if error is None:
        # check if the member is a student
        # fetch the student data from the student table assuming member is a student
        cursor.execute("SELECT * FROM student WHERE roll_No = %s", (id,))
        data = cursor.fetchone()
        role = "student"
        # executes if the member not a student
        if data is None:
            try:
                # check if the member is a staff
                # fetch the staff data from the staff table assuming member is a staff
                cursor.execute("SELECT * FROM staff WHERE employee_ID = %s", (id,))
                data = cursor.fetchone()
                role = "staff"
            except Exception as e:
                error = e
        # eerror is raised if the userID is invalid
        if data is None:
            error = "the user id entered is incorrect"
        elif error is None:
            # collected member data and role is assigned student or staff
            data = dict(data)
            data["role"] = role
            # concatenate the member data with the student or staff data collected
            user.update(data)
            return jsonify({"user": user}), 200
    return jsonify({"message": error}), 400


# TODO
# update the user data
# passed on <id> as a dynamic parameter and verified using jwt token
@bp.route("/<id>", methods=["PATCH"])
@verify_authorization
def update_user_info():
    return "hello"


# make a borrow request for a book
# passed on <id> as a dynamic parameter and verified using jwt token
@bp.route("/<id>/borrow", methods=["POST"])
@verify_authorization
def borrow_request(id):
    db, cursor = get_db()
    error = None
    # checks if the isbn id of the book to be borrowed is given
    isbn = request.args.get("isbn")
    # if no isbn then error is raised
    if isbn is None:
        error = "book not specified"
    else:
        # verifies if the isbn is valid and is of a registered book
        cursor.execute("SELECT * FROM book_details WHERE ISBN=%s", (isbn,))
        if not cursor.fetchall():
            error = "book not registered"
    if error is None:
        try:
            # insert the instance to the borrowal_request table for admin to verify
            cursor.execute(
                "INSERT INTO borrowal_request(user_ID,ISBN) VALUES(%s,%s)", (id, isbn)
            )
            return (
                jsonify({"message": f"succesfully added borrowal request for {isbn}"}),
                200,
            )
        except Exception as e:
            error = str(e)
    return jsonify({"message": error}), 400


# make a borrow request for a book
# passed on <id> as a dynamic parameter and verified using jwt token
@bp.route("/<id>/borrow", methods=["GET"])
@verify_authorization
def get_all_borrow_requests(id):
    db, cursor = get_db()
    try:
        cursor.execute(
            """SELECT br.*,bd.book_name FROM borrowal_request br,book_details bd WHERE br.ISBN=bd.ISBN AND user_ID = %s""",
            (id,),
        )
    except Exception as e:
        jsonify({"message": str(e)}), 400
    requests = []
    for data in cursor.fetchall():
        requests.append(dict(data))
    return jsonify({"requests": requests}), 200


# view all books borrowed by the user
# passed on <id> as a dynamic parameter and verified using jwt token
@bp.route("/<id>/borrowed", methods=["GET"])
@verify_authorization
def view_borrowed(id):
    db, cursor = get_db()
    books = []
    try:
        # fetch all those ISBN and number of times renewed belonging to the given userID
        cursor.execute("SELECT * FROM borrowal WHERE user_ID = %s", (id,))
    except Exception as e:
        return jsonify({"message": error}), 400
    # parsing the array of tyuples
    for data in cursor.fetchall():
        data = dict(data)
        isbn = data["isbn"]
        issue_date = data["issue_date"]
        return_date = data["return_date"]
        renewed = data["renewed"]
        # fetch the details of the book corresponding to given isbn
        book, error = get_book(isbn)
        if not error:
            # add a new key renewed giving number of times the book was renewed
            book["renewed"] = renewed
            book["issue_date"] = issue_date
            book["return_date"] = return_date
            # deleting key values that needent beviewed by the clients
            del book["availability"]
            # collecting all the book details as an array of objects
            books.append(book)
        else:
            return jsonify({"message": str(error)}), 400
    return jsonify({"data": books}), 200


# make a request for a addition of a new book
# passed on <id> as a dynamic parameter and verified using jwt token
@bp.route("/<id>/request", methods=["POST"])
@verify_authorization
def post_book_request(id):
    db, cursor = get_db()
    body = request.json
    required = ["bookName", "type"]
    # checks if the rquest body contains the name of book to be requested
    for key in required:
        if key not in body.keys():
            return jsonify({"message": "book name is required"}), 400
    book_name = body["bookName"]
    req_type = body["type"]
    try:
        # verifies that the book requested is not already registed
        cursor.execute("SELECT * FROM request WHERE book_name = %s", (book_name,))
        # if book already registeed error is raised
        if cursor.fetchone():
            return jsonify({"message": "book already requested"}), 400
        # verifies that the book requested is not already registed
        cursor.execute("SELECT * FROM book_details WHERE book_name = %s", (book_name,))
        # if book already registeed error is raised
        if cursor.fetchone():
            return jsonify({"message": "book already registered"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    try:
        # if the request is for a new book
        # insert the instance to the request table for admin to view
        req_type = "REQUEST" if req_type == "request" else "DONATE"
        cursor.execute(
            "INSERT INTO request(user_ID,book_name,req_type) VALUES(%s,%s,%s)",
            (id, book_name, req_type),
        )
        return jsonify({"message": "book request submitted"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
