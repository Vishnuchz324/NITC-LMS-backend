from flask import Blueprint, request, jsonify

from api.db import get_db
from api.decorator import verify_admin_authorization, verify_authorization, generate_token


bp = Blueprint('book', __name__, url_prefix='/api/book')


@bp.route("", methods=["POST"])
def add_books():
    db, cursor = get_db()
    body = request.json
    error = None
    required = ['ISBN', 'bookName', 'author', 'publisher']
    for key in required:
        if key not in body.keys():
            error = f"{key} is required"
    if error is None:
        ISBN = body['ISBN'],
        book_name = body['bookName'],
        publisher_name = body['publisher'],
        author_names = body['author']
        print(author_names)
        try:
            cursor.execute(
                'INSERT INTO book_details VALUES(%s,%s,%s) RETURNING *;', (ISBN, book_name, publisher_name))
            book = dict(cursor.fetchone())
            book["authors"] = []
            db.commit()

        except Exception as e:
            return jsonify({"message": str(e)}), 400

        # register if new author
        author_ids = []
        for author_name in author_names:
            cursor.execute(
                'SELECT * FROM author WHERE author_name=%s', (author_name,))
            author = cursor.fetchone()
            if(not author):
                try:
                    cursor.execute(
                        'INSERT INTO author(author_name) VALUES(%s) RETURNING *;', (author_name,))
                    author_ids.append(cursor.fetchone()[0])
                    db.commit()
                except Exception as e:
                    return jsonify({"message": str(e)}), 400
            else:
                author_ids.append(author[0])

        for author_id in author_ids:
            try:
                cursor.execute(
                    'INSERT INTO book_authors(ISBN,author_ID) VALUES(%s,%s)', (ISBN, author_id))
                db.commit()
            except Exc as e:
                return jsonify({"message": str(e)}), 400

        cursor.execute(
            'SELECT author_name FROM author NATURAL JOIN book_authors WHERE book_authors.ISBN=%s', (ISBN))
        for author in cursor.fetchall():
            book['authors'].append(author[0])

        return jsonify({"message": "book succesfully added", "data": book}), 200

    return jsonify({"message": error}), 400


@bp.route("/author", methods=["GET"])
def get_all_books_of_author():
    author = request.args.get('author')
    db, cursor = get_db()
    try:
        books = []
        cursor.execute(
            """SELECT book_name,publisher,book_details.ISBN FROM book_details ,author ,book_authors
            WHERE book_authors.author_ID = author.author_ID
            AND book_authors.ISBN = book_details.ISBN
            AND author.author_name = %s""", (author,))

        for book in cursor.fetchall():
            books.append(dict(book))
        return jsonify({"data": books}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
