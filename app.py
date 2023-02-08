from flask import Flask, render_template
from sqlalchemy import create_engine, text

# Import Blueprints
from views.auth import auth

# Create the App object
app = Flask(__name__)
# Initialize the database
db = create_engine("sqlite+pysqlite:///prototype.db", echo=True)


@app.route("/")
def index():
    return render_template("index.html")


### TODO: Following routes should be properly organized into blueprints
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/invoices")
def invoices():
    return render_template("invoices.html")


@app.route("/inventory")
def inventory():
    with db.connect() as conn:
        query = text(
            """
                SELECT name, cost_center, format, size, size_value,
                    initial_value, warehouse, counter
                FROM items, inventory
                WHERE items.id = inventory.item_id
            """
        )
        table = conn.execute(query)
    return render_template("inventory.html", table=table)

# Register Blueprints into the main app
app.register_blueprint(auth)
