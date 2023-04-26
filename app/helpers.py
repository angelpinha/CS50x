from functools import wraps
from flask import g, request, redirect, url_for, session


def login_required(f):
    """
    Decorate routes to require login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def confirm_2fa_pending(f):
    """
    Decorate to confirm 2fa.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        pending = session.get("user_id_pending")
        if pending is None:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function
