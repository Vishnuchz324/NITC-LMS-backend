from flask import Blueprint, request, jsonify, make_response
from datetime import date

from api.db import get_db
from api.decorator import (
    verify_admin_authorization,
    verify_authorization,
    generate_token,
)


bp = Blueprint("book", __name__, url_prefix="/api/book")

# ROUTES ( base = "/api/book" )
# [POST]  "/register"             register new book                         -admin
# [POST]   "/add/<isbn>?nums=""   add more copies of registerd book         -admin
# [GET]   "/<isbn>"               get details of book with given idbn
# [GET]   "/"                     get details of all book
# [GET]   "/search"               search for book by authors and tags
# [GET]   "/authors"              get all authors that are registered
# [GET]   "/tags"                 get all tags that are registered


# register a new book
# book data added to teh book_details table
# route can only be accesed by librarian
@bp.route("/register", methods=["POST"])
@verify_admin_authorization
def register_books():

    # {
    #     "ISBN": "",
    #     "bookName": "",
    #     "authors": [],
    #     "tags": [],
    #     "publisher": "",
    # }

    db, cursor = get_db()
    body = request.json
    error = None
    required = ["ISBN", "bookName", "authors", "tags", "publisher"]
    # check if the request is valid and contains all required parameters
    for key in required:
        if key not in body.keys():
            error = f"{key} is required"
    if error is None:
        ISBN = (body["ISBN"],)
        book_name = (body["bookName"],)
        publisher_name = (body["publisher"],)
        author_names = body["authors"]
        tag_names = body["tags"]

        # insert the data the book_request table and return the recently inserted
        try:
            cursor.execute(
                "SELECT * FROM book_details WHERE book_name=%s OR ISBN=%s ;",
                (ISBN, book_name, publisher_name),
            )
            if cursor.fetchone() is not None:
                return jsonify({"messaage": "the book already registered"}), 400
            cursor.execute(
                "INSERT INTO book_details VALUES(%s,%s,%s) RETURNING *;",
                (ISBN, book_name, publisher_name),
            )
            book = dict(cursor.fetchone())
            # created fields for tags and authors
            book["authors"] = []
            book["tags"] = []
            db.commit()

        except Exception as e:
            return jsonify({"message": str(e)}), 400

        # register author
        author_ids = []
        for author_name in author_names:
            # checks if the author is pre registered
            cursor.execute("SELECT * FROM author WHERE author_name=%s", (author_name,))
            author = cursor.fetchone()
            if not author:
                try:
                    # if new author , the author details are added to author table
                    cursor.execute(
                        "INSERT INTO author(author_name) VALUES(%s) RETURNING *;",
                        (author_name,),
                    )
                    author_ids.append(cursor.fetchone()[0])
                    db.commit()
                except Exception as e:
                    return jsonify({"message": str(e)}), 400
            else:
                # collect the id of all the authors after adding or fetching them to/from the author table
                author_ids.append(author[0])

        # establish the many to many relation b/w book_details and author
        # insert all the author ids to books_authors table
        for author_id in author_ids:
            try:
                cursor.execute(
                    "INSERT INTO books_authors(ISBN,author_ID) VALUES(%s,%s)",
                    (ISBN, author_id),
                )
                db.commit()
            except Exception as e:
                return jsonify({"message": str(e)}), 400

            # register if new author

        # register tags
        tag_ids = []
        for tag_name in tag_names:
            # checks if the tag is pre registered
            cursor.execute("SELECT * FROM tags WHERE tag_name=%s", (tag_name,))
            tag = cursor.fetchone()
            if not tag:
                try:
                    # if new tag , the tag details are added to tags table
                    cursor.execute(
                        "INSERT INTO tags(tag_name) VALUES(%s) RETURNING *;",
                        (tag_name,),
                    )
                    tag_ids.append(cursor.fetchone()[0])
                    db.commit()
                except Exception as e:
                    return jsonify({"message": str(e)}), 400
            else:
                # collect the id of all the tags after adding or fetching them to/from the tags table
                tag_ids.append(tag[0])

        # establish the many to many relation b/w book_details and tags
        # insert all the tag ids to books_tags table
        for tag_id in tag_ids:
            try:
                cursor.execute(
                    "INSERT INTO books_tags(ISBN,tag_ID) VALUES(%s,%s)", (ISBN, tag_id)
                )
                db.commit()
            except Exception as e:
                return jsonify({"message": str(e)}), 400

        # get all tag names
        cursor.execute(
            "SELECT tag_name FROM tags NATURAL JOIN books_tags WHERE books_tags.ISBN=%s",
            (ISBN),
        )
        # append the tag names to the book object
        for tag in cursor.fetchall():
            book["tags"].append(tag[0])

        # get all authors
        cursor.execute(
            "SELECT author_name FROM author NATURAL JOIN books_authors WHERE books_authors.ISBN=%s",
            (ISBN),
        )
        # append the tag names to the book object
        for author in cursor.fetchall():
            book["authors"].append(author[0])

        # by default add just 1 copy
        nums = 1
        # if number of copies provided in request it is used
        if "nums" in body.keys():
            nums = body["nums"]
        # adds num number of books to the book table
        add_book(ISBN, nums)
        return (
            jsonify({"message": f"book succesfully added {nums} copies", "data": book}),
            200,
        )

    return jsonify({"message": error}), 400


# adding more copies of an existing book
# route can only be accesed by librarian
# number of copies passed as query parameter
@bp.route("/add/<isbn>", methods=["POST"])
@verify_admin_authorization
def add_book(isbn, nums=1):
    print("entered here")
    db, cursor = get_db()
    # check if the request parameter have the number of books else only one copy added
    if request.args.get("nums"):
        nums = int(request.args.get("nums"))
        # verify_admin_authorization verifies and adds the admin details to the request
        # the admin who adds the book is obtained from the request
    admin = request.user["userID"]
    try:
        # a loop is iterated num number times
        # a new book entry of the particular isbn is inserted each time
        # the status of the book by defaultt is "AVAILABLE"
        try:
            print(f"adding {nums} copy of {isbn}")
            for i in range(nums):
                cursor.execute(
                    "INSERT INTO book(ISBN,admin_ID) VALUES(%s,%s)", (isbn, admin)
                )
        except Exception as e:
            print(str(e))
        return jsonify({"message": f"{nums} number of books added"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


# a utility function
# return all data of the book including authors , tags and availibility on passing isbn
def get_book(isbn):
    db, cursor = get_db()
    book = None
    error = None
    try:
        # select all details of book from book_details table referenced by isbn
        cursor.execute("SELECT * FROM book_details WHERE ISBN=%s", (isbn,))
        book = dict(cursor.fetchone())
        # added empty array for authors and tags
        book["authors"] = []
        book["tags"] = []
        # select all the tag_names useing join of the books_tags and tags tables
        # reference via isbn
        cursor.execute(
            "SELECT tag_name FROM tags NATURAL JOIN books_tags WHERE ISBN=%s", (isbn,)
        )
        # add all the tag_name as an array
        for tag in cursor.fetchall():
            book["tags"].append(tag[0])
        # select all the author_names useing join of the book_authors and author tables
        # reference via isbn
        cursor.execute(
            "SELECT author_name FROM author NATURAL JOIN books_authors WHERE ISBN=%s",
            (isbn,),
        )
        # add all the author_name as an array
        for author in cursor.fetchall():
            book["authors"].append(author[0])
        # get availability of book
        # select availability of book grouped by status
        cursor.execute(
            "SELECT books.status,COUNT(*) FROM (SELECT * FROM book WHERE ISBN=%s) as books GROUP BY status",
            (isbn,),
        )
        availability = {}
        # a lookup to rename the availability status from database
        # availability can be AVAILABLE or BORROWED or BAD CONDITION
        lookup = {
            "AVAILABLE": "available",
            "BAD CONDITION": "bad_condition",
            "BORROWED": "borrowed",
        }
        for [key, value] in cursor.fetchall():
            availability[lookup[key]] = value
            # availability object is added to the book details
        book["availability"] = availability
    except Exception as e:
        error = e
    return book, error


# get the data of a particluar book
# the isbn of the book to be searched is given as route parameter <isbn>
@bp.route("/<isbn>", methods=["GET"])
def get_book_from_isbn(isbn):
    # return the book with given isbn and error if any
    book, error = get_book(isbn)
    if error:
        return jsonify({"message": str(error)}), 400
    else:
        return jsonify({"data": book}), 200


# get the data of all books
@bp.route("/", methods=["GET"])
def get_all_books():
    db, cursor = get_db()
    user = request.args.get("userID")
    if user is None:
        try:
            # fetch the isbn of all books from book details
            cursor.execute("SELECT ISBN FROM book_details")
            books = []
            for data in cursor.fetchall():
                isbn = dict(data)["isbn"]
                # for each isbn get the details of the book
                # if no error add the book details to an array
                book, error = get_book(isbn)
                if error is None:
                    books.append(dict(book))
                else:
                    raise Exception(error)
            return jsonify({"data": books}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    else:
        try:
            # fetch the isbn of all books from book details
            cursor.execute(
                """SELECT ISBN FROM book_details
                            WHERE ISBN NOT IN
                            (SELECT ISBN FROM borrowal_request WHERE user_ID=%s)
                            AND ISBN NOT IN
                            (SELECT  ISBN FROM borrowal WHERE user_ID=%s)""",
                (
                    user,
                    user,
                ),
            )
            books = []
            for data in cursor.fetchall():
                isbn = dict(data)["isbn"]
                # for each isbn get the details of the book
                # if no error add the book details to an array
                book, error = get_book(isbn)
                if error is None:
                    books.append(dict(book))
                else:
                    raise Exception(error)
            return jsonify({"data": books}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 400


@bp.route("/all", methods=["GET"])
@verify_admin_authorization
def all_books():
    db, cursor = get_db()
    books = []
    try:
        cursor.execute("SELECT * FROM book")
        for data in cursor.fetchall():
            books.append(dict(data))
        return jsonify({"books": books}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


# serach a particlar book
# books can be searched by tags and authors
@bp.route("/search", methods=["GET"])
def search_books():

    # {
    #     "authors": [],
    #     "tags": [],
    # }

    body = request.json
    required = ["authors", "tags"]
    # verifies that the request body have authors and tags array
    for key in required:
        if key not in body.keys():
            return jsonify({"message": f"{key} is a required key"}), 400
    authors = tuple(body["authors"])
    tags = tuple(body["tags"])
    db, cursor = get_db()
    book_ids = []
    books = []
    # if no author or tag matches empty array returned
    if len(authors) == 0 and len(tags) == 0:
        return jsonify({"data": books}), 200
    # if both authors and tags given
    if len(authors) > 0 and len(tags) > 0:
        try:
            # select all those books with the selected authors AND the selected tags
            cursor.execute(
                """SELECT book_details.ISBN FROM book_details WHERE
                book_details.ISBN IN (SELECT books_tags.ISBN FROM (books_tags NATURAL JOIN tags)
                WHERE tags.tag_name IN %s)
                AND book_details.ISBN IN (SELECT books_authors.ISBN FROM (books_authors NATURAL JOIN author)
                WHERE author.author_name IN %s)""",
                (tags, authors),
            )
            for data in cursor.fetchall():
                isbn = dict(data)["isbn"]
                if isbn not in book_ids:
                    book_ids.append(isbn)
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    # if just authors are given
    elif len(authors) > 0:
        try:
            # select all those books written by any of the selected authors
            cursor.execute(
                """SELECT book_details.ISBN FROM book_details WHERE
                book_details.ISBN IN (SELECT books_authors.ISBN FROM (books_authors NATURAL JOIN author)
                WHERE author.author_name IN %s)""",
                (authors,),
            )
            for data in cursor.fetchall():
                isbn = dict(data)["isbn"]
                if isbn not in book_ids:
                    book_ids.append(isbn)
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    # if just authors are given
    elif len(tags) > 0:
        try:
            # select all those books that has the selected tags
            cursor.execute(
                """SELECT book_details.ISBN FROM book_details WHERE
                book_details.ISBN IN (SELECT books_tags.ISBN FROM (books_tags NATURAL JOIN tags)
                WHERE tags.tag_name IN %s)""",
                (tags,),
            )

            for data in cursor.fetchall():
                isbn = dict(data)["isbn"]
                if isbn not in book_ids:
                    book_ids.append(isbn)
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    for isbn in book_ids:
        book, error = get_book(isbn)
        if not error:
            books.append(book)
        else:
            return jsonify({"message": str(error)}), 400
    return jsonify({"data": books}), 200


# get all authors that has been registered
@bp.route("/authors", methods=["GET"])
def get_authors():
    db, cursor = get_db()
    authors = []
    try:
        # fetch all the author names from the author table
        cursor.execute("SELECT author_name FROM author")
        for author_list in cursor.fetchall():
            authors.append(author_list[0])
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    return jsonify({"authors": authors}), 200


# get all tags that has been registered
@bp.route("/tags", methods=["GET"])
def get_tags():
    db, cursor = get_db()
    tags = []
    try:
        # fetch all the tag names from the tags table
        cursor.execute("SELECT tag_name FROM tags")
        for tag_list in cursor.fetchall():
            tags.append(tag_list[0])
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    return jsonify({"tags": tags}), 200
