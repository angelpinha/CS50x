import sqlite3
import click
from flask import current_app, g


# Database Connection
def get_db():
    # Ensure the db conection is set globally
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["SQLite_Database_URI"],
            # Find the data type of each db column
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        # The connection will return dicts as rows
        g.db.row_factory = sqlite3.Row

    return g.db


# Checking if a global connection was created, to close it
def close_db(e=None):
    # Remove attribute if it exists, otherwise return None
    db = g.pop("db", None)

    # Close connection if db attribute of g is not None
    if db is not None:
        db.close()


# Get schema from sql file to db
def schema_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


# Create database through CLI or run.py script
@click.command("schema-db")
def schema_db_command():
    try:
        schema_db()
        click.echo("#########################################################")
        click.echo("Database has been created!")
        click.echo("#########################################################")
    except sqlite3.OperationalError:
        click.echo("#########################################################")
        click.echo("Previous database already in system!")
        click.echo("#########################################################")
        click.echo("Opening existing database instead")
        click.echo("#########################################################")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(schema_db_command)
