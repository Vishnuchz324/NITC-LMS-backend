from api.db import get_db
from flask import current_app
from api.decorator import add_app_context
import re


@add_app_context
def validate_register_user(body):

    # body validation
    # {
    #     "userID"   : - required
    #                  - 9 characters
    #                  - unique [ also not a librarian ]
    #     "userName" : - required
    #     "phoneNo"    : - required
    #                  - 10 to 12 characters
    #                  - unique
    #     "email"    : - required
    #                  - verified email,
    #                  - unique
    #     "dept"     : - required
    #                  - enum ['cse', 'ece', 'eee', 'civil', 'mech', 'chem', 'pd']
    #     "role"     : - required
    #                  - enum ['student','staff','librarian']
    #     "tFlag"    : - required [ if role is 'staff' ]
    #                  - enum [True,False] (boolean),
    #     "programme": - required [ if role is 'student' ]
    #                  - enum ['btech', 'barch', 'mtech', 'msc', 'phd'],
    # }

    db, cursor = get_db()

    required = ["userID", "userName", "password", "email", "phoneNo", "role"]

    # validate if required fields are present
    for key in required:
        if key not in body.keys() or body[key] is None:
            return f"{key} is required"

    # # verify if userID is valid and that it have not registered before
    user_id = body["userID"]
    if len(user_id) != 9:
        return f"user id is not a valid"

    # # verify if email is valid and that it have not registered before
    email = body["email"]
    regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    if not re.fullmatch(regex, email):
        return f"email is not a valid"

    # # verify if phoneNo is valid and that it have not registered before
    phoneNo = body["phoneNo"]
    if len(phoneNo) < 10 or len(phoneNo) > 12:
        return f"contact is not a valid"

    # verify if role is allowed
    roles = ["student", "staff", "librarian"]
    role = body["role"]
    if role not in roles:
        return f"{body['role']} is not a valid role"

    if role == "librarian":
        cursor.execute(f"SELECT * FROM members WHERE user_ID = %s", (user_id,))
        if cursor.fetchone() is not None:
            return f"user with id already registered"

    elif role != "librarian":

        # verify if department is allowed
        # departments = ['cse', 'ece', 'eee', 'civil', 'mech', 'chem', 'pd']
        # dept = body['dept'].lower()
        # if dept not in departments:
        #     return f"{dept} is not a valid department"

        # verify if details are correct if role is student
        if role == "student":
            programme = body["programme"].lower()
            if not programme:
                return f"programme is required for student"
            # else:
            #     programmes = ['btech', 'barch', 'mtech', 'msc', 'phd']
            #     if programme not in programmes:
            #         return f"{programme} is an  invalid student programme"

        elif role == "staff":
            tflag = body["tFlag"]
            if not tflag:
                return f"teacher flag is required for staff"
            else:
                tflag = True if ("true" or "True") else False
                if tflag not in [True, False]:
                    return f"teacher flag is not valid"

    table = "librarian" if (role == "librarian") else "members"
    key = "employee_ID" if (role == "librarian") else "user_ID"

    cursor.execute(f"SELECT * FROM {table} WHERE {key} = %s", (user_id,))
    if cursor.fetchone() is not None:
        return f"user id is already registered"

    cursor.execute(f"SELECT * FROM {table} WHERE email = %s", (email,))
    if cursor.fetchone() is not None:
        return f"email already registered"

    cursor.execute(f"SELECT * FROM {table} WHERE phone = %s", (phoneNo,))
    if cursor.fetchone() is not None:
        return f"contact no already registered"

    return None
