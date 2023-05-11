from io import BytesIO
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    session,
    g,
    url_for,
)

from werkzeug.security import check_password_hash, generate_password_hash
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


class Credentials:
    # Checks for complete credentials in a form, given a dict of fields
    def verify(self, fields) -> bool:
        # Counter for missing credentials
        missing_credentials = 0
        # Iterate over the credentials
        for input, label in fields.items():
            if not request.form.get(f"{input}"):
                flash(f"Must provide {fields[input]}", "error")
                missing_credentials += 1
                continue
        if missing_credentials != 0:
            return False
        return True

    # Gets active user username
    def get_username(self) -> str:
        db = get_db()
        USERNAME = db.execute(
            """
            SELECT username
            FROM users
            WHERE id = (?)
            """,
            (g.user[0],),
        ).fetchone()[0]
        return USERNAME

    # Gets active user password_hash
    def get_password_hash(self) -> str:
        db = get_db()
        PWHASH = db.execute(
            """
            SELECT password_hash
            FROM users
            WHERE id = (?)
            """,
            (g.user[0],),
        ).fetchone()[0]
        return PWHASH

    # Checks if totp is set for active user
    def totp_checker(self) -> bool:
        # Returns True if totp is set, false otherwise
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
        return is_totp_set

    # Validates 6-digit 2FA code provided by user
    def validate_totp(self, given_totp_code) -> bool:
        db = get_db()
        totp_key = db.execute(
            """
            SELECT totp_key
            FROM users
            WHERE id = (?)
            """,
            (g.user[0],),
        ).fetchone()[0]

        # Validates provided 6-digit totp code
        verify_otp = pyotp.TOTP(totp_key).verify(given_totp_code)
        return verify_otp


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
    # ID data inside the TOTP
    USERNAME = Credentials().get_username()
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
            return redirect(url_for("user_profile.two_factor_authentication"))

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
            return redirect(url_for("user_profile.two_factor_authentication"))
        # verify_otp is False
        else:
            flash("Invalid 6-digit code, try again", "error")
            return redirect(url_for("user_profile.two_factor_authentication"))
    else:
        # Initialize the database and get totp_key from database
        is_totp_set = Credentials().totp_checker()

        if is_totp_set is False:
            if session.get("qr_encoded") is None:
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
            return render_template("profile/2fa.html", is_totp_set=is_totp_set)


@user_profile.route("/recovery_key", methods=["GET", "POST"])
@login_required
def recovery_key():
    if "show_recovery_key" in request.form:
        fields = {
            "rk_totp": "2FA 6-Digit code",
        }

        # Check credentials
        if not Credentials().verify(fields):
            return redirect(url_for("user_profile.recovery_key"))

        try:
            rk_totp = int(request.form.get("rk_totp"))
        except ValueError:
            flash("Must provide a valid 6-digit 2FA code", "error")
            return redirect(url_for("user_profile.recovery_key"))

        verify_otp = Credentials().validate_totp(rk_totp)

        if verify_otp is False:
            flash("Invalid 2FA code", "error")
            return redirect(url_for("user_profile.recovery_key"))

        else:
            session["reveal_rk_info"] = True
            return redirect(url_for("user_profile.reveal_rk"))

    if "generate_new_recovery_key" in request.form:
        # Counter for missing credentials
        fields = {
            "rk_generate": "Text confirmation on form",
            "rk_generate_totp": "2FA 6-Digit code",
        }

        # Check credentials
        if not Credentials().verify(fields):
            return redirect(url_for("user_profile.recovery_key"))

        try:
            user_totp = int(request.form.get("rk_generate_totp"))
        except ValueError:
            flash("Must provide a valid 6-digit 2FA code", "error")
            return redirect(url_for("user_profile.recovery_key"))

        user_confirmation = request.form.get("rk_generate").lower()
        confirmation_message = "generate a new recovery key"

        verify_otp = Credentials().validate_totp(user_totp)

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
            return redirect(url_for("user_profile.recovery_key"))
        else:
            flash("Could not generate a new recovery key!", "error")
            flash("Please fill out the form accordingly", "error")
            return redirect(url_for("user_profile.recovery_key"))
    else:
        is_totp_set = Credentials().totp_checker()
        return render_template("profile/recovery_key.html", is_totp_set=is_totp_set)


@user_profile.route("/reveal_rk")
@login_required
def reveal_rk():
    if session.get("reveal_rk_info") is True:
        session.pop("reveal_rk_info", None)
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
        session.pop("reveal_rk_info", None)
        return redirect(url_for("user_profile.recovery_key"))


@user_profile.route("/deactivate_2fa", methods=["GET", "POST"])
@login_required
def deactivate_2fa():
    if request.method == "POST":
        fields = {
            "password": "Password",
            "totp": "2FA 6-Digit code",
        }

        # Check credentials
        if not Credentials().verify(fields):
            return redirect(url_for("user_profile.deactivate_2fa"))

        try:
            totp = int(request.form.get("totp"))
        except ValueError:
            flash("Must provide a valid 6-digit 2FA code", "error")
            return redirect("/deactivate_2fa")

        pwhash = Credentials().get_password_hash()
        verify_otp = Credentials().validate_totp(totp)
        checker = check_password_hash(pwhash, request.form.get("password"))

        if verify_otp and checker:
            UUID = str(uuid.uuid4()).upper()
            db = get_db()
            db.execute(
                """
                UPDATE users
                SET totp_key = NULL, uuid = (?)
                WHERE id = (?)
                """,
                (
                    UUID,
                    g.user[0],
                ),
            )
            db.commit()

            flash("Two-factor authentication has been deactivated!", "success")
            flash("ALERT: Recovery key for your account has been replaced!", "success")
            return redirect(url_for("user_profile.two_factor_authentication"))
        # Not verify_otp and/or not checker
        else:
            flash("Invalid credentials", "error")
            return redirect(url_for("user_profile.deactivate_2fa"))

    else:
        is_totp_set = Credentials().totp_checker()

        if is_totp_set:
            return render_template("profile/deactivate_2fa.html")
        # Handles case if totp is not set for account
        else:
            return redirect(url_for("user_profile.two_factor_authentication"))


@user_profile.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        fields = {
            "password": "Current password",
            "new_password": "New password",
            "new_password_check": "New password confirmation",
            "totp": "2FA 6-digit code",
        }

        # Check credentials
        if not Credentials().verify(fields):
            return redirect(url_for("user_profile.change_password"))

        pwhash = Credentials().get_password_hash()
        current_password = request.form.get("password")
        checker = check_password_hash(pwhash, current_password)

        # Validates current password with db password_hash
        if checker is not True:
            flash("Incorrect current password", "error")
            return redirect(url_for("user_profile.change_password"))

        new_password = request.form.get("new_password")
        new_password_check = request.form.get("new_password_check")

        # Validates new password and confirmation
        if new_password != new_password_check:
            flash("New Password and Confirmation must be equal!", "error")
            return redirect(url_for("user_profile.change_password"))

        # Validates provided password
        if current_password == new_password:
            flash("New Password must be different to Current Password!", "error")
            return redirect(url_for("user_profile.change_password"))

        # Validates TOTP input type
        try:
            totp = int(request.form.get("totp"))
        except ValueError:
            flash("Must provide a valid 6-digit 2FA code", "error")
            return redirect(url_for("user_profile.change_password"))

        verify_otp = Credentials().validate_totp(totp)

        if verify_otp is False:
            flash("Invalid 2FA code", "error")
            return redirect(url_for("user_profile.change_password"))

        else:
            # Updates password_hash for active user
            NEW_PWHASH = generate_password_hash(new_password)
            db = get_db()
            db.execute(
                """
                UPDATE users
                SET password_hash = (?)
                WHERE id = (?)
                """,
                (
                    NEW_PWHASH,
                    g.user[0],
                ),
            )
            db.commit()

        # Success!
        flash("Password has been changed!", "success")
        return redirect(url_for("user_profile.profile"))

    else:
        is_totp_set = Credentials().totp_checker()
        return render_template("profile/change_password.html", is_totp_set=is_totp_set)


@user_profile.route("/change_username", methods=["GET", "POST"])
@login_required
def change_username():
    if request.method == "POST":
        fields = {
            "new_username": "New username",
            "password": "Current password",
            "totp": "2FA 6-digit code",
        }

        # Check credentials
        if not Credentials().verify(fields):
            return redirect(url_for("user_profile.change_username"))

        pwhash = Credentials().get_password_hash()
        current_password = request.form.get("password")
        checker = check_password_hash(pwhash, current_password)

        # Validates provided password
        if checker is not True:
            flash("Incorrect password", "error")
            return redirect(url_for("user_profile.change_username"))

        # Validates TOTP input type
        try:
            totp = int(request.form.get("totp"))
        except ValueError:
            flash("Must provide a valid 6-digit 2FA code", "error")
            return redirect(url_for("user_profile.change_username"))

        verify_otp = Credentials().validate_totp(totp)

        if verify_otp is False:
            flash("Invalid 2FA code", "error")
            return redirect(url_for("user_profile.change_username"))

        else:
            NEW_USERNAME = request.form.get("new_username")
            # Updates username
            try:
                db = get_db()
                db.execute(
                    """
                    UPDATE users
                    SET username = (?)
                    WHERE id = (?)
                    """,
                    (
                        NEW_USERNAME,
                        g.user[0],
                    ),
                )
                db.commit()
            except db.IntegrityError:
                flash("Username has already been taken, try again!", "error")
                return redirect(url_for("user_profile.change_username"))

        # Success!
        flash(f"Username has been changed to {NEW_USERNAME}!", "success")
        return redirect(url_for("user_profile.profile"))
    else:
        username = Credentials().get_username()
        is_totp_set = Credentials().totp_checker()

        return render_template(
            "profile/change_username.html",
            username=username,
            is_totp_set=is_totp_set,
        )
