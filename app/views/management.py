from flask import Blueprint, render_template

management = Blueprint("management", __name__)


@management.route("/inventory")
def inventory():
    # TODO import inventory_db from db.py
    return render_template("inventory.html")


@management.route("/invoices")
def invoices():
    return render_template("invoices.html")
