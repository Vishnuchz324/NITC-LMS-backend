DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS fine;
DROP TABLE IF EXISTS request;
DROP TABLE IF EXISTS borrowal;
DROP TABLE IF EXISTS book_authors;
DROP TABLE IF EXISTS books_tags;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS author;
DROP TABLE IF EXISTS book_details;
DROP TABLE IF EXISTS librarian;
DROP TABLE IF EXISTS members;



CREATE TABLE members(
user_ID CHAR(9),
mem_name VARCHAR(35),
pwd TEXT,
phone CHAR(10),
email VARCHAR(45),
dept VARCHAR(5),
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
programme VARCHAR(6),
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
fine_status BOOLEAN,
amount DECIMAL(8,2),
payment_date DATE,
PRIMARY KEY(fine_ID),
FOREIGN KEY(user_ID) REFERENCES members(user_ID),
FOREIGN KEY(admin_ID) REFERENCES librarian(employee_ID));


CREATE TABLE request(
request_ID serial,
user_ID CHAR(9),
book_name VARCHAR(35),
req_date DATE,
req_type BOOLEAN,
PRIMARY KEY(request_ID),
FOREIGN KEY(user_ID) REFERENCES members(user_ID)
);

CREATE TABLE book_details(
ISBN CHAR(13),
book_name VARCHAR(35),
publisher VARCHAR(25),
PRIMARY KEY(ISBN)
);

CREATE TABLE author(
author_ID serial,
author_name VARCHAR(25),
PRIMARY KEY (author_ID)
);



CREATE TABLE book_authors(
author_ID serial,
ISBN CHAR(13),
PRIMARY KEY(author_ID,ISBN),
FOREIGN KEY (author_ID) REFERENCES author(author_ID),
FOREIGN KEY (ISBN) REFERENCES book_details(ISBN)
);

CREATE TABLE tags(
tag_ID serial,
tag_name VARCHAR(10),
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
book_number INTEGER,
ISBN CHAR(13) UNIQUE,
status BOOLEAN,
admin_ID CHAR(9),
arrival_date DATE,
PRIMARY KEY (book_number),
FOREIGN KEY (ISBN) REFERENCES book_details(ISBN),
FOREIGN KEY(admin_ID) REFERENCES librarian(employee_ID)
);

CREATE TABLE borrowal(
issue_ID serial,
user_ID CHAR(9),
admin_ID CHAR(9),
ISBN CHAR(13),
book_number INTEGER,
renewals_left INTEGER,
issue_date INTEGER,
PRIMARY KEY(issue_ID),
FOREIGN KEY(user_ID) REFERENCES members(user_ID),
FOREIGN KEY(admin_ID) REFERENCES librarian(employee_ID),
FOREIGN KEY (ISBN) REFERENCES book_details(ISBN),
FOREIGN KEY (book_number) REFERENCES book(book_number)
);

SELECT VERSION();