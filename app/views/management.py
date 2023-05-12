from flask import (
    Blueprint,
    render_template,
    current_app,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
)
from app.helpers import login_required
from werkzeug.local import LocalProxy
from app.db import get_db
import click
import re

management = Blueprint("management", __name__)
database = LocalProxy(get_db)


@management.route("/management")
@login_required
def management_layout():
    return render_template("management/management_layout.html")


@management.route("/items")
@login_required
def items():
    return render_template("management/items.html")


@management.route("/products")
@login_required
def products():
    return render_template("management/products.html")


@management.route("/new_product", methods=["GET", "POST"])
@login_required
def new_product():
    if request.method == "POST":
        PRODUCT = {"name": request.form.get("NAME")}

        for i in range(int(request.form.get("quantity")) - 1):
            PRODUCT[f"component_{i+1}"] = request.form.get(f"component{i+1}")

            # Ensure item aren't in use already
            if PRODUCT[f"component_{i+1}"]:
                item_ocupied = database.execute(
                    "SELECT product_id FROM items WHERE name = ?",
                    (PRODUCT[f"component_{i+1}"],),
                ).fetchone()

            if item_ocupied[0]:
                flash("One of the items selected is in use already")
                return redirect(url_for("management.new_product"))

        # TODO: Ensure product doesn't exist yet
        if PRODUCT["name"]:
            name_ocupied = database.execute(
                "SELECT description FROM products WHERE description = ?",
                (PRODUCT["name"],),
            ).fetchone()

        if name_ocupied:
            flash("The product already exists")
            return redirect(url_for("management.new_product"))

        # TODO: If doesn't, save product into database
        database.execute(
            "INSERT INTO products (description, sell_value) VALUES (?, ?)",
            (PRODUCT["name"], 0),
        )

        def product_deconstructor(P):
            result = [P["name"]]
            placeholder = ""
            for key, value in P.items():
                if re.search("component", key):
                    result.append(value)
                    placeholder += "?,"
            result.append(placeholder[:-1])
            return tuple(result)

        database.execute(
            f"""UPDATE items
            SET product_id = (SELECT id FROM products WHERE description = ?)
            WHERE name IN ({product_deconstructor(PRODUCT)[-1]})""",
            product_deconstructor(PRODUCT)[:-1],
        )
        database.commit()

        flash(f"Product {PRODUCT['name']} created")
        return redirect(url_for("management.new_product"))

    return render_template("management/new_product.html")


@management.route("/new_item", methods=["GET", "POST"])
@login_required
def new_item():
    if request.method == "POST":
        # TODO: Create query to construct a new entity
        ITEM = {
            "name": request.form.get("name"),
            "cost_center": request.form.get("cost_center"),
            "format": request.form.get("format"),
            "unit": request.form.get("unit"),
            "value": request.form.get("value"),
        }
        validation = 0
        for key, value in ITEM.items():
            if ITEM[key]:
                validation += 1

        if validation == 5:
            database.execute(
                """INSERT INTO items (name, cost_center, format, unit, purchase_value) VALUES (?,?,?,?,?)""",
                (
                    ITEM["name"],
                    ITEM["cost_center"],
                    ITEM["format"],
                    ITEM["unit"],
                    ITEM["value"],
                ),
            )
            database.execute(
                """INSERT INTO inventory (item_id, initial_quantity, stored_quantity)
                    SELECT id, 0, 0 FROM items WHERE name = ?""",
                (ITEM["name"],),
            )
            database.commit()

            flash("Item Created Succesfully")
            return redirect(url_for("management.new_item"))

        flash("Failed to correctly provide data")
        return redirect(url_for("management.new_item"))

    return render_template("management/new_item.html")


@management.route("/search")
@login_required
def search():
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
    # Return the item and its values
    if request.method == "POST":
        item = request.form.get("item")

        if item:
            table = database.execute(
                """SELECT name, stored_quantity, unit, purchase_value
                    FROM items INNER JOIN inventory
                    ON items.id = inventory.item_id
                    WHERE name = ?""",
                (item,),
            ).fetchall()

            return render_template("management/inventory.html", table=table)

    return render_template("management/inventory.html")


@management.route("/invoices")
@login_required
def invoices():
    return render_template("management/invoices.html")
