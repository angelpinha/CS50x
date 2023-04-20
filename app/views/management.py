from flask import Blueprint, render_template, current_app, request, jsonify
from app.helpers import login_required
from app.db import get_db

management = Blueprint("management", __name__)


@management.route("/management")
@login_required
def management_layout():
    return render_template("management/management_layout.html")


@management.route("/products")
@login_required
def products():
    return render_template("management/products.html")


@management.route("/search")
@login_required
def search():
    database = get_db()
    q = request.args.get("q")

    Json = []
    if q:
        items = database.execute(
            "SELECT name FROM items WHERE name LIKE ?||?", (q, "%")
        ).fetchall()

        for row in range(len(items)):
            Json.append({"name": items[row]["name"]})

    return Json


@management.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory():
    # TODO Return the item and its values
    if request.method == "POST":
        database = get_db()
        item = request.form.get("item")

        if item:
            table = database.execute(
                """SELECT name, stored_quantity, unit
                    FROM items INNER JOIN inventory
                    ON items.id = inventory.item_id
                    WHERE name = ?""",
                (item,),
            ).fetchall()

            return render_template("management/inventory.html", table=table)

    else:
        return render_template("management/inventory.html")


@management.route("/invoices")
@login_required
def invoices():
    return render_template("management/invoices.html")
