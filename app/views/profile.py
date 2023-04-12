from io import BytesIO
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    session,
    g,
)

import uuid
import pyotp
import qrcode
import base64

from app.db import get_db
from app.helpers import login_required

user_profile = Blueprint("user_profile", __name__)


@user_profile.before_app_request
def logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        )


@user_profile.route("/profile")
@login_required
def profile():
    db = get_db()
    rows = db.execute(
        """
        SELECT username, first_name, last_name, role
        FROM users
        WHERE id = (?)
        """,
        (g.user[0],),
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
        "profile/profile.html",
        username=username,
        first_name=first_name,
        last_name=last_name,
        role=role,
    )


@login_required
def create_totp_qrcode():
    # Get username from database
    db = get_db()
    rows = db.execute(
        """
            SELECT username
            FROM users
            WHERE id = (?)
            """,
        (g.user[0],),
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


@user_profile.route("/2FA", methods=["GET", "POST"])
@login_required
def two_factor_authentication():
    if request.method == "POST":
        qr_key = session["qr_key"]

        try:
            user_input_code = int(request.form.get("totp"))
        except ValueError:
            flash("Must provide a valid 6-digit 2FA code", "error")
            return redirect("/2FA")

        verify_otp = pyotp.TOTP(qr_key).verify(user_input_code)

        if verify_otp is True:
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
                    g.user[0],
                ),
            )
            db.commit()

            session.pop("qr_encoded", None)
            session.pop("qr_key", None)

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
            (g.user[0],),
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
                "profile/2fa.html", qr_encoded=qr_encoded, is_totp_set=is_totp_set
            )
        else:
            is_totp_set = True
            return render_template("profile/2fa.html", is_totp_set=is_totp_set)


@user_profile.route("/recovery_key", methods=["GET", "POST"])
@login_required
def recovery_key():
    if "show_recovery_key" in request.form:
        # Counter for missing credentials
        missing_credentials = 0
        fields = {
            "rk_totp": "2FA 6-Digit code",
        }

        # Makes sure every input has been filled
        for input in fields:
            if not request.form.get(f"{input}"):
                flash(f"Must provide {fields[input]}", "error")
                missing_credentials += 1
                continue

        if missing_credentials != 0:
            return redirect("/recovery_key")

        try:
            rk_totp = int(request.form.get("rk_totp"))
        except ValueError:
            flash("Must provide a valid 6-digit 2FA code", "error")
            return redirect("/recovery_key")

        db = get_db()
        totp_key = db.execute(
            """
            SELECT totp_key
            FROM users
            WHERE id = (?)
            """,
            (g.user[0],),
        ).fetchone()[0]

        verify_otp = pyotp.TOTP(totp_key).verify(rk_totp)

        if verify_otp is True:
            session["reveal_rk_info"] = True
            return redirect("/reveal_rk")

        else:
            flash("Invalid 2FA code", "error")
            return redirect("/recovery_key")

    if "generate_new_recovery_key" in request.form:
        # Counter for missing credentials
        missing_credentials = 0
        fields = {
            "rk_generate": "Text confirmation on form",
            "rk_generate_totp": "2FA 6-Digit code",
        }

        # Makes sure every input has been filled
        for input in fields:
            if not request.form.get(f"{input}"):
                flash(f"Must provide {fields[input]}", "error")
                missing_credentials += 1
                continue

        if missing_credentials != 0:
            return redirect("/recovery_key")

        try:
            user_totp = int(request.form.get("rk_generate_totp"))
        except ValueError:
            flash("Must provide a valid 6-digit 2FA code", "error")
            return redirect("/recovery_key")

        user_confirmation = request.form.get("rk_generate").lower()
        confirmation_message = "generate a new recovery key"

        db = get_db()
        totp_key = db.execute(
            """
            SELECT totp_key
            FROM users
            WHERE id = (?)
            """,
            (g.user[0],),
        ).fetchone()[0]

        verify_otp = pyotp.TOTP(totp_key).verify(user_totp)

        if user_confirmation == confirmation_message and verify_otp:
            UUID = str(uuid.uuid4()).upper()
            db = get_db()
            db.execute(
                """
                UPDATE users
                SET uuid = (?)
                WHERE id = (?)
                """,
                (
                    UUID,
                    g.user[0],
                ),
            )
            db.commit()
            flash("New recovery key has been generated!", "success")
            return redirect("/recovery_key")
        else:
            flash("Could not generate a new recovery key!", "error")
            flash("Please fill out the form accordingly", "error")
            return redirect("/recovery_key")
    else:
        db = get_db()
        TOTP = db.execute(
            """
            SELECT totp_key
            FROM users
            WHERE id = (?)
            """,
            (g.user[0],),
        ).fetchone()[0]

        if TOTP is None:
            is_totp_set = False
        else:
            is_totp_set = True

        return render_template("profile/recovery_key.html", is_totp_set=is_totp_set)


@user_profile.route("/reveal_rk")
@login_required
def reveal_rk():
    if session.get("reveal_rk_info") is True:
        session["reveal_rk_info"] = False

        db = get_db()
        UUID = db.execute(
            """
            SELECT uuid
            FROM users
            WHERE id = (?)
            """,
            (g.user[0],),
        ).fetchone()[0]

        return render_template("profile/reveal_rk.html", uuid=UUID)
    else:
        session["reveal_rk_info"] = False
        return redirect("/recovery_key")
