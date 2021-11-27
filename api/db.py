import os
from os import environ
import psycopg2
import click
from flask.cli import with_appcontext
from flask import current_app, g
from psycopg2 import extras


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    # app.cli.add_command(seed_db_command)


# initialize the database with the schema given in sql/schema.sql file
def init_db():
    db, cur = get_db()
    schema_path = os.path.join(os.getcwd(), 'sql/schema.sql')
    with current_app.open_resource(schema_path) as f:
        cur.execute(f.read().decode('utf8'))
    return cur.fetchone()['version']


@click.command("init-db")
@with_appcontext
def init_db_command():
    db_version = init_db()
    click.echo("Database Initialized. DB version:")
    click.echo("    {0}".format(db_version))


def get_db():
    if "db" not in g:
        enviornment = environ.get('ENV')
        # DB_URL = environ.get(
        #     'DATABASE_URL_DEV') if enviornment == "developemnt" else environ.get('DATABASE_URL')
        DB_URL = environ.get('DATABASE_URL_DEV')
        g.db = psycopg2.connect(DB_URL)
        g.db.autocommit = True
        g.cursor = g.db.cursor(cursor_factory=extras.DictCursor)
    return g.db, g.cursor


def close_db(e=None):
    cursor = g.pop("cursor", None)
    if cursor is not None:
        cursor.close()
    db = g.pop("db", None)
    if db is not None:
        db.commit()
        db.close()
