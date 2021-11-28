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
