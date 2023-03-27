from io import BytesIO
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
import qrcode
import base64

from app.db import get_db
from app.helpers import login_required

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

        # Checks if username is registered in database
        if rows is None:
            flash("Username not registered", "error")
            next_url = request.form.get("next")
            if next_url:
                return redirect(next_url)
            return render_template("auth/login.html")

        auth = check_password_hash(rows["password_hash"], password)

        # Checks if password is valid
        if auth is not True:
            flash("Incorrect password", "error")
            next_url = request.form.get("next")
            if next_url:
                return redirect(next_url)
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


@auth.route("/profile")
@login_required
def profile():
    db = get_db()

    rows = db.execute(
        """
        SELECT username, first_name, last_name, role
        FROM users
        WHERE id = (?)
        """,
        (session["user_id"],),
    ).fetchone()

    username = rows["username"]
    first_name = rows["first_name"]
    last_name = rows["last_name"]
    role = rows["role"]

    # Redirects to a previously requested url if exists
    next_url = request.form.get("next")
    if next_url:
        return redirect(next_url)

    return render_template(
        "auth/profile.html",
        username=username,
        first_name=first_name,
        last_name=last_name,
        role=role,
    )


@auth.route("/2FA")
def two_factor_authentication():
    # Generate the QR code image using the "qrcode" library
    qr = qrcode.QRCode(
        version = None,
        error_correction = qrcode.constants.ERROR_CORRECT_M,
        box_size = 5,
        border = 4,
    )
    # Data inside the QR code
    qr.add_data("Two Factor Authentication! :)")
    # Generated QR size is determined by how much information will be stored
    qr.make(fit = True)
    # Translate the above information into a PilImage
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Convert the "PilImage" object to a byte stream
    # This step is implemented this way because there is no need to store
    # The QR image into a file inside the hard drive
    byte_stream = BytesIO()
    # Save the byte stream into a PNG
    qr_img.save(byte_stream, format="PNG")
    # Locate the pointer of the byte stream at the first location
    byte_stream.seek(0)

    # Encode the byte stream as a base64 ascii string
    # 1) byte_stream.getvalue() gets the bythes from the byte stream
    # 2) base64.b64encode() encodes the bytes as base64-encoded string
    # 3) .decode("ascii") converts the byte string to a regular string
    qr_code_data = base64.b64encode(byte_stream.getvalue()).decode("ascii")
    # This string can be used in an HTML image tag as the source of the image
    # Without having to write the image to a file on the server

    return render_template("auth/2fa.html", qr_code_data=qr_code_data)


@auth.route("/recover")
def change_password():
    # TODO
    return render_template("auth/recover.html")
