from flask import Flask, render_template
from app.helpers import login_required


def create_app():
    # Create and configure the app
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config["SQLite_Database_URI"] = "data.db"

    from .views.auth import auth
    from .views.profile import user_profile
    from .views.management import management
    from .views.checkout import checkout

    @app.route("/")
    @login_required
    def index():
        return render_template("index.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    app.register_blueprint(auth)
    app.register_blueprint(user_profile)
    app.register_blueprint(management)
    app.register_blueprint(checkout)

    # Initialize database after app initialitation
    from . import db

    db.init_app(app)

    return app
