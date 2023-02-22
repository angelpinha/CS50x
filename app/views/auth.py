from flask import Blueprint, render_template

auth = Blueprint("auth", __name__)


@auth.route("/register")
def register():
    return "Hello, Register!"


@auth.route("/login")
def login():
    return render_template("auth/login.html")


@auth.route("/password")
def change_password():
    return "Hello, Password!"
