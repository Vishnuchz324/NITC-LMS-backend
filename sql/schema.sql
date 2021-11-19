DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS staff;
DROP TABLE IF EXISTS librarian;
DROP TABLE IF EXISTS member;

CREATE TABLE member (
  user_id VARCHAR(9) PRIMARY KEY,
  name VARCHAR(35) NOT NULL,
  password TEXT NOT NULL,
  phone VARCHAR(10) NOT NULL UNIQUE,
  email VARCHAR(45) NOT NULL UNIQUE,
  dept VARCHAR(5) NOT NULL,
  role VARCHAR(9) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE student(
  roll_no VARCHAR(9),
  validity DATE,
  programme VARCHAR(6),
  FOREIGN KEY (roll_no) REFERENCES member(user_id)
);

CREATE TABLE staff(
  employee_id VARCHAR(9),
  Tflag BOOLEAN,
  FOREIGN KEY (employee_id) REFERENCES member(user_id)
);

CREATE TABLE librarian (
  employee_id INTEGER PRIMARY KEY,
  name VARCHAR(35) NOT NULL,
  password VARCHAR(20) NOT NULL,
  phone VARCHAR(10) NOT NULL UNIQUE,
  email VARCHAR(45) NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

SELECT version();