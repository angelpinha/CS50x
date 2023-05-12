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


@management.route("/products", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "POST":
        name = request.form.get("trade_name")
        return render_template("management/products.html", name=name)

    return render_template("management/products.html")


@management.route("/new_product", methods=["GET", "POST"])
@login_required
def new_product():
    if request.method == "POST":
        PRODUCT = {"name": request.form.get("NAME")}

        for i in range(int(request.form.get("quantity")) - 1):
            PRODUCT[f"component_{i+1}"] = request.form.get(f"component{i+1}")

        # TODO: Ensure product doesn't exist yet
        if PRODUCT["name"]:
            name = database.execute(
                "SELECT description FROM products WHERE description = ?",
                (PRODUCT["name"],),
            ).fetchone()

            if name:
                flash("The product already exists")
                return redirect(url_for("management.new_product"))

            else:
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

        # TODO: Else: redirect, sending a messege to user
        # click.echo(PRODUCT)

    return render_template("management/new_product.html")


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
    # TODO Return the item and its values
    if request.method == "POST":
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
