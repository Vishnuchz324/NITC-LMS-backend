from flask import Blueprint, request, jsonify, make_response

from api.db import get_db
from api.decorator import verify_admin_authorization, verify_authorization, generate_token


bp = Blueprint('book', __name__, url_prefix='/api/book')


@bp.route("/register", methods=["POST"])
def add_books():
    db, cursor = get_db()
    body = request.json
    error = None
    required = ['ISBN', 'bookName', 'authors', 'tags', 'publisher']
    for key in required:
        if key not in body.keys():
            error = f"{key} is required"
    if error is None:
        ISBN = body['ISBN'],
        book_name = body['bookName'],
        publisher_name = body['publisher'],
        author_names = body['authors']
        tag_names = body['tags']

        try:
            cursor.execute(
                'INSERT INTO book_details VALUES(%s,%s,%s) RETURNING *;', (ISBN, book_name, publisher_name))
            book = dict(cursor.fetchone())
            book["authors"] = []
            book["tags"] = []
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
                    'INSERT INTO books_authors(ISBN,author_ID) VALUES(%s,%s)', (ISBN, author_id))
                db.commit()
            except Exception as e:
                return jsonify({"message": str(e)}), 400

               # register if new author
        tag_ids = []
        for tag_name in tag_names:
            cursor.execute(
                'SELECT * FROM tags WHERE tag_name=%s', (tag_name,))
            tag = cursor.fetchone()
            if(not tag):
                try:
                    cursor.execute(
                        'INSERT INTO tags(tag_name) VALUES(%s) RETURNING *;', (tag_name,))
                    tag_ids.append(cursor.fetchone()[0])
                    db.commit()
                except Exception as e:
                    return jsonify({"message": str(e)}), 400
            else:
                tag_ids.append(tag[0])

        for tag_id in tag_ids:
            try:
                cursor.execute(
                    'INSERT INTO books_tags(ISBN,tag_ID) VALUES(%s,%s)', (ISBN, tag_id))
                db.commit()
            except Exception as e:
                return jsonify({"message": str(e)}), 400

        cursor.execute(
            'SELECT tag_name FROM tags NATURAL JOIN books_tags WHERE books_tags.ISBN=%s', (ISBN))
        for tag in cursor.fetchall():
            book['tags'].append(tag[0])

        cursor.execute(
            'SELECT author_name FROM author NATURAL JOIN books_authors WHERE books_authors.ISBN=%s', (ISBN))
        for author in cursor.fetchall():
            book['authors'].append(author[0])

        return jsonify({"message": "book succesfully added", "data": book}), 200

    return jsonify({"message": error}), 400


@bp.route("/", methods=["GET"])
def get_all_books():
    db, cursor = get_db()
    try:
        cursor.execute("SELECT * FROM book_details")
        books = []
        for book in cursor.fetchall():
            books.append(dict(book))
        return jsonify({"data": books}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


def get_book(isbn):
    db, cursor = get_db()
    book = None
    error = None
    try:
        cursor.execute("SELECT * FROM book_details WHERE ISBN=%s", (isbn,))
        book = dict(cursor.fetchone())
        book['authors'] = []
        book['tags'] = []
        cursor.execute(
            "SELECT tag_name FROM tags NATURAL JOIN books_tags WHERE ISBN=%s", (isbn,))
        for tag in cursor.fetchall():
            book['tags'].append(tag[0])
        cursor.execute(
            "SELECT author_name FROM author NATURAL JOIN books_authors WHERE ISBN=%s", (isbn,))
        for author in cursor.fetchall():
            book['authors'].append(author[0])
    except Exception as e:
        error = e
    return book, error


@bp.route("/<isbn>", methods=["GET"])
def get_book_from_isbn(isbn):
    book, error = get_book(isbn)
    if error:
        return jsonify({"message": str(error)}), 400
    else:
        return jsonify({"data": book}), 200


@bp.route("/search", methods=["GET"])
def search_books():
    body = request.json
    required = ["authors", "tags"]
    for key in required:
        if key not in body.keys():
            return jsonify({"message": f"{key} is a required key"}), 400
    authors = tuple(body['authors'])
    tags = tuple(body['tags'])
    db, cursor = get_db()
    book_ids = []
    books = []
    if(len(authors) == 0 and len(tags) == 0):
        return jsonify({"data": books}), 200
    if(len(authors) > 0 and len(tags) > 0):
        try:
            cursor.execute(
                """SELECT book_details.ISBN FROM book_details WHERE
                book_details.ISBN IN (SELECT books_tags.ISBN FROM (books_tags NATURAL JOIN tags)
                WHERE tags.tag_name IN %s)
                AND book_details.ISBN IN (SELECT books_authors.ISBN FROM (books_authors NATURAL JOIN author)
                WHERE author.author_name IN %s)""", (tags, authors))
            for isbn_list in cursor.fetchall():
                isbn = isbn_list[0]
                if isbn not in book_ids:
                    book_ids.append(isbn)
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    elif(len(authors) > 0):
        try:
            cursor.execute(
                """SELECT book_details.ISBN FROM book_details WHERE
                book_details.ISBN IN (SELECT books_authors.ISBN FROM (books_authors NATURAL JOIN author)
                WHERE author.author_name IN %s)""", (authors,))
            for isbn_list in cursor.fetchall():
                isbn = isbn_list[0]
                if isbn not in book_ids:
                    book_ids.append(isbn)
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    elif(len(tags) > 0):
        try:
            cursor.execute(
                """SELECT book_details.ISBN FROM book_details WHERE
                book_details.ISBN IN (SELECT books_tags.ISBN FROM (books_tags NATURAL JOIN tags)
                WHERE tags.tag_name IN %s)""", (tags,))

            for isbn_list in cursor.fetchall():
                isbn = isbn_list[0]
                if isbn not in book_ids:
                    book_ids.append(isbn)
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    for isbn in book_ids:
        book, error = get_book(isbn)
        if(not error):
            books.append(book)
    return jsonify({"data": books}), 200
