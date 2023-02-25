from flask import Blueprint, render_template
from app.helpers import login_required

management = Blueprint("management", __name__)


@management.route("/inventory")
@login_required
def inventory():
    # TODO import inventory_db from db.py
    return render_template("inventory.html")


@management.route("/invoices")
@login_required
def invoices():
    return render_template("invoices.html")
