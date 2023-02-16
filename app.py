from flask import Flask, render_template
import os

# Seting the database session for global usage
from db import db_session

# Import Blueprints
from views.auth import auth
from views.management import management


# Create the App object
app = Flask(__name__)


# Close db connection when finish request
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/")
def index():
    return render_template("index.html")


### TODO: Following routes should be properly organized into blueprints
@app.route("/about")
def about():
    return render_template("about.html")


# Register Blueprints into the main app
app.register_blueprint(auth)
app.register_blueprint(management)
