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
import pyotp
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


def create_totp_qrcode():
    # Get username from database
    db = get_db()
    rows = db.execute(
        """
            SELECT username
            FROM users
            WHERE id = (?)
            """,
        (session["user_id"],),
    ).fetchone()

    # ID data inside the TOTP
    USERNAME = rows["username"]
    APP_NAME = "CS50x"
    # Generate a secret key to represent in the QR code
    SECRET_KEY = pyotp.random_base32()

    # Encapsulate the information to store TOTP inside a QR code later on
    time_based_otp = pyotp.totp.TOTP(SECRET_KEY).provisioning_uri(
        name=USERNAME, issuer_name=APP_NAME
    )

    # Generate the QR code image using the "qrcode" library
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    # Insert data inside the QR code
    qr.add_data(time_based_otp)
    # Generated QR size based on size of data
    qr.make(fit=True)
    # Convert QR code into an image object
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Convert the "PilImage" object to a byte stream to avoid storing image
    byte_stream = BytesIO()
    qr_img.save(byte_stream, format="PNG")
    # Locate the pointer of the byte stream at the first location
    byte_stream.seek(0)

    # Encode the byte stream as a base64 ascii string
    # 1) byte_stream.getvalue() gets the bytes from the byte stream
    # 2) base64.b64encode() encodes the bytes as base64-encoded string
    # 3) .decode("ascii") converts the byte stream into a regular ascii string
    qr_encoded = base64.b64encode(byte_stream.getvalue()).decode("ascii")

    session["qr_encoded"] = qr_encoded
    session["qr_key"] = SECRET_KEY

    return


@auth.route("/2FA", methods=["GET", "POST"])
def two_factor_authentication():
    if request.method == "POST":
        qr_key = session["qr_key"]
        user_input_code = int(request.form.get("totp"))
        current_code = int(pyotp.TOTP(qr_key).now())

        if current_code == user_input_code:
            # Initialize the database and update totp_key
            db = get_db()
            db.execute(
                """
                UPDATE users
                SET totp_key = (?)
                WHERE id = (?)
                """,
                (
                    qr_key,
                    session["user_id"],
                ),
            )
            db.commit()

            flash("Two factor authentication has been set", "success")
            return redirect("/2FA")

        else:
            flash("Invalid 6-digit code, try again", "error")
            return redirect("/2FA")

    else:
        # Initialize the database and get totp_key from database
        db = get_db()
        rows = db.execute(
            """
                SELECT totp_key
                FROM users
                WHERE id = (?)
                """,
            (session["user_id"],),
        ).fetchone()

        if rows["totp_key"] is None:
            is_totp_set = False

            if "qr_encoded" not in session:
                create_totp_qrcode()
                qr_encoded = session["qr_encoded"]
                qr_key = session["qr_key"]

            else:
                qr_encoded = session["qr_encoded"]
                qr_key = session["qr_key"]

            return render_template(
                "auth/2fa.html", qr_encoded=qr_encoded, is_totp_set=is_totp_set
            )
        else:
            is_totp_set = True
            return render_template("auth/2fa.html", is_totp_set=is_totp_set)


@auth.route("/recover")
def change_password():
    # TODO
    return render_template("auth/recover.html")
