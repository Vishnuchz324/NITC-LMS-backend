# Library Management Backend

`flask api`

### Getting Started

1. clone the repo using `git clone`
2. enter the project directory `cd library-management-backend`
3. create a virtual enviornment in the directory `python -m venv venv`
4. install all the dependencies to the virtual enviornment from the requirements file `pip install -r requirements.txt`
5. rename the _env_example_ file as _.env_ and add the missing details
6. setup the flask enviornmnet variables (_steps illustrated fot windows_)
   ```
   $env:FLASK_APP="api"
   $env:FLASK_ENV="development"
   ```
7. start the application using `flask run` opens up by default in _localhost:5000_
8. API documentation available at _localhost:5000_ or <a href="https://documenter.getpostman.com/view/15324195/UVCCfjQL">here</a>
