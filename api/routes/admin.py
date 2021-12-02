from flask import Blueprint, request, jsonify

from api.db import get_db
from api.decorator import verify_admin_authorization, verify_authorization, generate_token


bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@bp.route("/requests/borrow", methods=["GET"])
@verify_admin_authorization
def get_borrow_requests():
    db, cursor = get_db()
    try:
        cursor.execute("""SELECT br.request_ID as id,m.mem_name as user,bd.book_name as book,br.req_date FROM borrowal_request br,members m,book_details bd
                        WHERE br.user_ID = m.user_ID AND br.ISBN = bd.ISBN ORDER BY br.req_date """)
    except Exception as e:
        jsonify({"message": str(e)}), 400
    requests = []
    for data in cursor.fetchall():
        requests.append(dict(data))
    return jsonify({"requests": requests}), 200


@bp.route("/borrowals", methods=["GET"])
@verify_admin_authorization
def get_all_borrowals():
    db, cursor = get_db()
    borrowals = []
    try:
        cursor.execute("SELECT * FROM borrowal NATURAL JOIN book_details")
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    for data in cursor.fetchall():
        borrowals.append(dict(data))
    return jsonify({"data": borrowals}), 200


@bp.route("/checkout/<request_id>", methods=["GET"])
@verify_admin_authorization
def checkout(request_id):
    db, cursor = get_db()
    admin_id = request.user["userID"]
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
    elif(renewed < 3):
        renewed += 1
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


@bp.route("/checkin/<borrowal_id>", methods=["GET"])
@verify_admin_authorization
def checkin(borrowal_id):
    db, cursor = get_db()
    try:
        cursor.execute(
            "SELECT * FROM borrowal WHERE issue_ID = %s", (borrowal_id,))
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    borrowal = dict(cursor.fetchone())
    if borrowal:
        try:
            cursor.execute(
                "DELETE FROM borrowal WHERE issue_ID = %s", (borrowal_id,))
        except Exception as e:
            return jsonify({"message": str(e)}), 400
        try:
            book_number = borrowal["book_number"]
            cursor.execute(
                """UPDATE book SET status =%s WHERE book_number=%s""", (
                    "AVAILABLE", book_number))
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    return jsonify({"message": "book has been sucvesfully checked in "}), 200


@bp.route('/users', methods=['GET'])
@verify_admin_authorization
def get_all_users():
    db, cursor = get_db()
    try:
        users = []
        cursor.execute("SELECT user_ID,mem_name,dept,email FROM members")
        rows = cursor.fetchall()
        for user in rows:
            users.append(dict(user))
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


@bp.route('/admins', methods=['GET'])
@verify_admin_authorization
def get_all_admins():
    db, cursor = get_db()
    try:
        users = []
        cursor.execute("SELECT employee_ID,lib_name,email FROM librarian")
        rows = cursor.fetchall()
        for user in rows:
            users.append(dict(user))
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
