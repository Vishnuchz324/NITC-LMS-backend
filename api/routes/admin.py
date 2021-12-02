from flask import Blueprint, request, jsonify

from api.db import get_db
from api.decorator import verify_admin_authorization, verify_authorization, generate_token


bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# fetch all the borrowal requests
@bp.route("/requests/borrow", methods=["GET"])
@verify_admin_authorization
def get_borrow_requests():
    db, cursor = get_db()
    # get the details of all the requests to borrow ordered by the date of request
    try:
        cursor.execute("""SELECT br.request_ID as id,m.mem_name as user,bd.book_name as book,br.req_date FROM borrowal_request br,members m,book_details bd
                        WHERE br.user_ID = m.user_ID AND br.ISBN = bd.ISBN ORDER BY br.req_date """)
    except Exception as e:
        jsonify({"message": str(e)}), 400
    requests = []
    for data in cursor.fetchall():
        # collect all borrowal requests
        requests.append(dict(data))
    return jsonify({"requests": requests}), 200

# fetch all the borrow requests that are checked out but not checked back in
@bp.route("/borrowals", methods=["GET"])
@verify_admin_authorization
def get_all_borrowals():
    db, cursor = get_db()
    borrowals = []
    # get all the borrowals requests that are accepted/checked out
    try:
        cursor.execute("SELECT * FROM borrowal NATURAL JOIN book_details")
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    for data in cursor.fetchall():
        borrowals.append(dict(data))
    return jsonify({"data": borrowals}), 200

# check out books by the librarain
# request_id is passed as parameter for checking out a particular request
@bp.route("/checkout/<request_id>", methods=["GET"])
@verify_admin_authorization
def checkout(request_id):
    db, cursor = get_db()
    admin_id = request.user["userID"]
    # check if the request_id passed is valid
    try:
        cursor.execute(
            "SELECT * FROM borrowal_request WHERE request_ID=%s", (request_id,))
        borrow_request = dict(cursor.fetchone())
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    user_id = borrow_request["user_id"]
    isbn = borrow_request["isbn"]

    # get the number of times the book have been renewed if taken previously
    try:
        cursor.execute(
            """SELECT renewed FROM borrowal WHERE user_ID=%s AND ISBN = %s""", (user_id, isbn))
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    renewed = 0
    previos_renewal = cursor.fetchone()
    if(previos_renewal):
        renewed = previos_renewal[0]
    # if the book is checked out for the first time by that user
    if(renewed == 0):
        renewed = 1
        # select a book from the books list to issue to the user
        cursor.execute(
            """SELECT * FROM book WHERE ISBN=%s AND status=%s ORDER BY arrival_date LIMIT 1""", (isbn, "AVAILABLE"))
        book = cursor.fetchone()
        if not book:
            return jsonify({"message": "no copies available"}), 400
        else:
            book_number = book["book_number"]

            # insert the borrowal entry to the borrowal table
            try:
                cursor.execute(
                    """INSERT INTO borrowal(user_ID,admin_ID,ISBN,book_number,renewed) VALUES(%s,%s,%s,%s,%s)""", (user_id, admin_id, isbn, book_number, renewed))
            except Exception as e:
                return jsonify({"message": str(e)}), 400

            # update the status of the borrowed book
            try:
                cursor.execute(
                    """UPDATE book SET status =%s WHERE book_number=%s""", (
                        "BORROWED", book_number))
            except Exception as e:
                return jsonify({"message": str(e)}), 400
    # check if the number of renewals is exceeding 3
    elif(renewed < 3):
        renewed += 1
        # update the number of renewals in the borrowal table
        try:
            cursor.execute(
                """UPDATE borrowal SET renewed = %s WHERE user_ID=%s AND ISBN=%s""", (renewed, user_id, isbn))
        except Exception as e:
            return jsonify({"message": str(e)}), 400

    # delete the entry from pending requests
    try:
        cursor.execute(
            """DELETE FROM borrowal_request WHERE request_ID = %s""", (request_id,))
    except Exception as e:
        return jsonify({"message": str(e)}), 400

    return jsonify({"message": "book succesfully checked out"}), 200

# checkin a book by the librarian
# borrowal_id is passed as parameter for checking in a particular book
@bp.route("/checkin/<borrowal_id>", methods=["GET"])
@verify_admin_authorization
def checkin(borrowal_id):
    db, cursor = get_db()
    # check if the borrowal_id is valid
    try:
        cursor.execute(
            "SELECT * FROM borrowal WHERE issue_ID = %s", (borrowal_id,))
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    borrowal = dict(cursor.fetchone())
    if borrowal:
        # the borrowal details are deleted form the borrowal table
        try:
            cursor.execute(
                "DELETE FROM borrowal WHERE issue_ID = %s", (borrowal_id,))
        except Exception as e:
            return jsonify({"message": str(e)}), 400
        # the status of the book is updated to AVAILABLE
        try:
            book_number = borrowal["book_number"]
            cursor.execute(
                """UPDATE book SET status =%s WHERE book_number=%s""", (
                    "AVAILABLE", book_number))
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    return jsonify({"message": "book has been sucvesfully checked in "}), 200

# fetch the details of all users registed in the system
@bp.route('/users', methods=['GET'])
@verify_admin_authorization
def get_all_users():
    db, cursor = get_db()
    try:
        users = []
        # get the details of the users from the members table
        cursor.execute("SELECT user_ID,mem_name,dept,email FROM members")
        rows = cursor.fetchall()
        for user in rows:
            users.append(dict(user))
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

# fetch the details of all librarians registed in the system
@bp.route('/admins', methods=['GET'])
@verify_admin_authorization
def get_all_admins():
    db, cursor = get_db()
    try:
        users = []
        # get the details of the librarians from the librarian table
        cursor.execute("SELECT employee_ID,lib_name,email FROM librarian")
        rows = cursor.fetchall()
        for user in rows:
            users.append(dict(user))
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
