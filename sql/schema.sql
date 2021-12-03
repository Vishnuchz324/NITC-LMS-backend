
DROP TABLE IF EXISTS staff CASCADE;
DROP TABLE IF EXISTS student CASCADE;
DROP TABLE IF EXISTS fine CASCADE;
DROP TABLE IF EXISTS request CASCADE;
DROP TABLE IF EXISTS borrowal CASCADE;
DROP TABLE IF EXISTS books_authors CASCADE;
DROP TABLE IF EXISTS books_tags CASCADE;
DROP TABLE IF EXISTS book CASCADE;
DROP TABLE IF EXISTS book_details CASCADE;
DROP TABLE IF EXISTS librarian CASCADE;
DROP TABLE IF EXISTS members CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS author CASCADE;
DROP TABLE IF EXISTS borrowal_request CASCADE;

CREATE TABLE members(
user_ID CHAR(9),
mem_name VARCHAR(35),
pwd TEXT,
phone CHAR(10),
email VARCHAR(45),
dept TEXT,
PRIMARY KEY(user_ID)
);

CREATE TABLE staff(
employee_ID CHAR(9),
Tflag BOOLEAN,
PRIMARY KEY(employee_ID),
FOREIGN KEY(employee_ID) REFERENCES members(user_ID)
);


CREATE TABLE student(
roll_No CHAR(9),
validity DATE,
programme TEXT,
PRIMARY KEY(roll_No),
FOREIGN KEY(roll_No) REFERENCES members(user_ID));

CREATE TABLE librarian(
employee_ID CHAR(9),
lib_name VARCHAR(25),
pwd TEXT,
phone CHAR(10),
email VARCHAR(45),
PRIMARY KEY(employee_ID));


CREATE TABLE fine(
fine_ID serial,
user_ID CHAR(9),
admin_ID CHAR(9),
fine_status VARCHAR(15) DEFAULT 'PENDING',
amount DECIMAL(8,2),
payment_date  DATE DEFAULT current_date + interval '15 days',
PRIMARY KEY(fine_ID),
FOREIGN KEY(user_ID) REFERENCES members(user_ID),
FOREIGN KEY(admin_ID) REFERENCES librarian(employee_ID));


CREATE TABLE request(
request_ID serial,
user_ID CHAR(9),
book_name VARCHAR(35),
req_date DATE default current_date,
req_type VARCHAR(10),
PRIMARY KEY(request_ID),
FOREIGN KEY(user_ID) REFERENCES members(user_ID)
);

CREATE TABLE book_details(
ISBN CHAR(13),
book_name TEXT,
publisher VARCHAR(30),
PRIMARY KEY(ISBN)
);

CREATE TABLE author(
author_ID serial,
author_name VARCHAR(35),
PRIMARY KEY (author_ID)
);

CREATE TABLE books_authors(
author_ID serial,
ISBN CHAR(13),
PRIMARY KEY(author_ID,ISBN),
FOREIGN KEY (author_ID) REFERENCES author(author_ID),
FOREIGN KEY (ISBN) REFERENCES book_details(ISBN)
);

CREATE TABLE tags(
tag_ID serial,
tag_name VARCHAR(35),
PRIMARY KEY (tag_ID)
);


CREATE TABLE books_tags(
tag_ID serial,
ISBN CHAR(13),
PRIMARY KEY(tag_ID,ISBN),
FOREIGN KEY (tag_ID) REFERENCES tags(tag_ID),
FOREIGN KEY (ISBN) REFERENCES book_details(ISBN)
);


CREATE TABLE book(
book_number serial,
ISBN CHAR(13),
status VARCHAR(20) DEFAULT 'AVAILABLE',
admin_ID CHAR(9),
arrival_date DATE DEFAULT current_date,
PRIMARY KEY (book_number),
FOREIGN KEY (ISBN) REFERENCES book_details(ISBN),
FOREIGN KEY(admin_ID) REFERENCES librarian(employee_ID)
);

CREATE TABLE borrowal_request(
    request_ID serial,
    user_ID CHAR(9),
    ISBN CHAR(13),
    req_date DATE DEFAULT current_date,
    status VARCHAR(20) DEFAULT 'PROCESSING',
    PRIMARY KEY(request_ID),
    FOREIGN KEY(user_ID) REFERENCES members(user_ID),
    FOREIGN KEY (ISBN) REFERENCES book_details(ISBN)
);

CREATE TABLE borrowal(
issue_ID serial,
user_ID CHAR(9),
admin_ID CHAR(9),
ISBN CHAR(13),
book_number INTEGER,
renewed INTEGER,
issue_date DATE DEFAULT current_date,
return_date DATE DEFAULT current_date + interval '30 days',
PRIMARY KEY(issue_ID),
FOREIGN KEY(user_ID) REFERENCES members(user_ID),
FOREIGN KEY(admin_ID) REFERENCES librarian(employee_ID),
FOREIGN KEY (ISBN) REFERENCES book_details(ISBN),
FOREIGN KEY (book_number) REFERENCES book(book_number)
);

SELECT VERSION();