from flask import Blueprint, render_template
from sqlalchemy import text
from db import engine

management = Blueprint('management', __name__)


@management.route("/inventory")
def inventory():
    with engine.connect() as conn:
        query = text(
            """
                SELECT name, department, format, unit, purchase_value,
                    initial_quantity, stored_quantity
                FROM items, inventory
                WHERE items.id = inventory.item_id
            """
        )
        table = conn.execute(query)
    return render_template("inventory.html", table=table)


@management.route("/purchases")
def purchases():
    return "Hello, Purchases"


@management.route("/invoices")
def invoices():
    return render_template("invoices.html")


@management.route("/items")
def items():
    return "Hello, Items"


@management.route("/products")
def products():
    return "Hello, Products"