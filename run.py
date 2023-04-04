# This script runs and configures the app inside the local machine
import os
import sys
from flask import current_app
from app import create_app
from app.db import get_db

# Create Flask app instance
app = create_app()

# Define if the program should run in development mode
# Asks the user for their preference
response = input("Would you like to run in development mode? (y/n): ")

if response not in ["y", "n"]:
    print("Should give a valid response.")
    print("Try again!")
    sys.exit(1)

if response.lower() == "y":
    development = True
    run_command = "flask --debug run"
else:
    development = False
    run_command = "flask run"

database_setting = input("Create new database file? (y/n): ")

if database_setting not in ["y", "n"]:
    print("Should give a valid response.")
    print("Try again!")
    sys.exit(1)

if database_setting.lower() == "y":
    database = True
    db_command = "flask --app app schema-db"
else:
    database = False
    db_command = None

if db_command is not None:
    commands = ["pip install -e .", db_command, run_command]
else:
    commands = ["pip install -e .", run_command]

if development is True:
    print("#########################################################")
    print("Running app in DEVELOPMENT mode")
    print("#########################################################")
else:
    print("#########################################################")
    print("Running app in NORMAL mode")
    print("#########################################################")

if database is True:
    print("#########################################################")
    print("Trying to create database...")
    print("#########################################################")
else:
    print("#########################################################")
    print("Trying to read existing database...")
    print("#########################################################")
    # Get db to verify if database is already in system
    # If not, create a new database
    with app.app_context():
        db = get_db()
        response = db.execute("PRAGMA TABLE_INFO(users)").fetchone()
        if response is None:
            print("#########################################################")
            print("There was no existing database")
            print("#########################################################")
            with current_app.open_resource("schema.sql") as f:
                db.executescript(f.read().decode("utf8"))
            print("#########################################################")
            print("NEW DATABASE HAS BEEN CREATED!")
            print("#########################################################")
        else:
            print("#########################################################")
            print("Database successfully opened!")
            print("#########################################################")

for command in commands:
    os.system(command)
