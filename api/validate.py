import re
# from api.db import get_db
# db, cursor = get_db()


def validate_register_user(body):

    # body validation
    # {
    #     "userID"   : - required
    #                  - 6 characters
    #                  - unique
    #     "userName" : - required
    #     "phoneNo"    : - required
    #                  - 10 to 12 characters
    #                  - unique
    #     "email"    : - required
    #                  - verified email,
    #                  - unique
    #     "dept"     : - required
    #                  - enum ['CSE', 'ECE', 'EEE', 'CIVIL', 'MECH', 'CHEM', 'PD']
    #     "role"     : - required
    #                  - enum ['student','staff']
    #     "tFlag"    : - required [ if role is 'staff' ]
    #                  - enum [True,False] (boolean),
    #     "programme": - required [ if role is 'student' ]
    #                  - enum ['BTECH', 'BARCH', 'MTECH', 'MSC', 'PHD'],
    # }

    required = ['userID', 'userName', 'password',
                'email', 'phoneNo', 'dept', 'role']

    # validate if required fields are present
    for key in required:
        if not body[key]:
            return f"{key} is required"

    # # verify if userID is valid and that it have not registered before
    user_id = body['userID']
    if len(user_id) != 6:
        return f"{user_id} is not a valid userID"
    # else:
    #     cursor.execute("SELECT * FROM users WHERE username = %s", (user_id,))
    #     if cursor.fetchone() is not None:
    #         return f"{user_id} is already registered"

    # # verify if email is valid and that it have not registered before
    email = body['email']
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(not re.fullmatch(regex, email)):
        return f"{email} is not a valid email id"
    # else:
    #     cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    #     if cursor.fetchone() is not None:
    #         return f"{email} already registered with an existing body"

    # # verify if phoneNo is valid and that it have not registered before
    phoneNo = body['phoneNo']
    if len(phoneNo) < 10 or len(phoneNo) > 12:
        return f"{phoneNo} is not a valid phone number"
    # else:
    #     cursor.execute("SELECT * FROM users WHERE phoneNo = %s", (phoneNo,))
    #     if cursor.fetchone() is not None:
    #         return f"{phoneNo} already registered with an existing body"

    # verify if department is allowed
    departments = ['CSE', 'ECE', 'EEE', 'CIVIL', 'MECH', 'CHEM', 'PD']
    dept = body['dept'].upper()
    if dept not in departments:
        return f"{dept} is not a valid department"

    # verify if role is allowed
    roles = ['student', 'staff']
    role = body['role']
    if role not in roles:
        return f"{body['role']} is not a valid role"

    else:
        # verify if details are correct if role is student
        if role == "student":
            programme = body["programme"].upper()
            if not programme:
                return f"programme is required for student"
            else:
                programmes = ['BTECH', 'BARCH', 'MTECH', 'MSC', 'PHD']
                if programme not in programmes:
                    return f"{programme} is an  invalid student programme"
        elif role == "staff":
            tflag = body["tFlag"]
            if not programme:
                return f"teacher flag is required for staff"
            else:
                if tflag not in [True, False]:
                    return f"tflag is not valid"
    return None
