from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    session,
    url_for,
    g,
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db

auth = Blueprint("auth", __name__)


@auth.before_app_request
def logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        )


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Counter for missing credentials
        missing_credentials = 0
        fields = {
            "first_name": "first name",
            "last_name": "last name",
            "username": "username",
            "password": "password",
            "password_check": "password confirmation",
        }

        # Makes sure every input has been filled
        for input in fields:
            if not request.form.get(f"{input}"):
                flash(f"Must provide {fields[input]}", "error")
                missing_credentials += 1
                continue

        if missing_credentials != 0:
            return redirect("/register")

        db = get_db()
        credentials = {}
        role = "inactive"

        # Stores key, value pairs in credentials dictionary according to fields keys
        for key, value in fields.items():
            # Makes sure the password is stored in the form of a hash value
            if fields[key] == "password":
                pwhash = generate_password_hash(request.form.get(f"{key}"))
                checker = check_password_hash(
                    pwhash, request.form.get("password_check")
                )
                if checker:
                    credentials[key] = pwhash
                else:
                    flash("Password and confirmation must be equal!", "error")
                    return redirect("/register")
            
            if fields[key] == "password_check":
                continue

            else:
                credentials[key] = request.form.get(f"{key}")
        try:
            db.execute(
                """
                INSERT INTO users 
                    (username, password_hash, first_name, last_name, role)
                VALUES
                    (?,?,?,?,?)
                """,
                (
                    credentials["username"],
                    credentials["password"],
                    credentials["first_name"],
                    credentials["last_name"],
                    role,
                ),
            )
            db.commit()
        except db.IntegrityError:
            flash("Username is already registered.", "error")
            return redirect("/register")

        success = flash("User Registered!", "success")
        wait = flash("Wait until an admin assigns your role.", "success")
        return render_template("auth/login.html", success=success, wait=wait)

    if request.method == "GET":
        return render_template("auth/register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        missing_credentials = 0
        fields = {
            "username": "Username",
            "password": "Password",
        }
        next_url = request.form.get("next")

        for input in fields:
            if not request.form.get(f"{input}"):
                flash(f"Must provide {fields[input]}", "error")
                missing_credentials += 1
                continue

        if missing_credentials != 0:
            return redirect("/login")

        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()

        rows = db.execute(
            """
            SELECT id, password_hash
            FROM users
            WHERE username = (?)
            """,
            (username,),
        ).fetchone()

        if rows is None:
            flash("Username not registered", "error")
            return render_template("auth/login.html")

        auth = check_password_hash(rows["password_hash"], password)

        if auth is not True:
            flash("Incorrect password", "error")
            return render_template("auth/login.html")

        else:
            session.clear()
            session["user_id"] = rows["id"]
            # Redirects to previously requested URL if exists
            if next_url:
                return redirect(next_url)
            return redirect(url_for("index"))

    else:
        return render_template("auth/login.html")


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth.route("/recover")
def change_password():
    # TODO
    return render_template("auth/recover.html")
