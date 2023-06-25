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

checkout = Blueprint("checkout", __name__)
database = LocalProxy(get_db)


@checkout.route("/checkout")
@login_required
def checkout_layout():
    return render_template("checkout/checkout_layout.html")


class Sell_product:
    def __init__(self, fields):
        self.name = fields["name"]
        self.quantity = fields["quantity"]
        self.total = fields["total"]

    def __str__(self):
        return f"name:{self.name}, quantity:{self.quantity}, total:{self.total}"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not name:
            raise NameError("Failed to provide valid name")
        self._name = name

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, quantity):
        if not quantity or quantity.isnumeric() == False:
            raise NameError("Failed to provide valid quantity")
        self._quantity = quantity

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, total):
        if not total or total.isnumeric() == False:
            raise NameError("Invalid total value")
        self._total = total


@checkout.route("/new_sale", methods=["GET", "POST"])
@login_required
def new_sale():
    if request.method == "POST":
        Products = []
        product_number = request.form.get("product_number")
        if product_number:
            total_sale = 0
            for i in range(int(product_number)):
                Products.append(
                    {
                        "name": request.form.get(f"name_{i+1}"),
                        "quantity": request.form.get(f"quantity_{i+1}"),
                        "total": request.form.get(f"total_{i+1}"),
                    }
                )
                try:
                    Products[i] = Sell_product(Products[i])
                    # Check if there is enough quantity of the product to sell
                    items_quantity = database.execute(
                        """SELECT name, stored_quantity
                        FROM items INNER JOIN inventory
                        ON items.id = inventory.item_id
                        WHERE items.name IN (SELECT name FROM items
                        WHERE product_id IN (SELECT id FROM products WHERE description = ?))""",
                        (Products[i].name,),
                    ).fetchall()
                    not_enough = 0
                    for item in range(len(items_quantity)):
                        if items_quantity[item][1] < int(Products[i].quantity):
                            not_enough += 1
                            flash(
                                f"""Not enough {items_quantity[item][0]} ({items_quantity[item][1]})
                                for {Products[i].name} ({Products[i].quantity})"""
                            )
                    if not_enough == 0:
                        # Update quantity of each item of the current product
                        items_id = database.execute(
                            """SELECT id FROM items
                        WHERE product_id = (SELECT id FROM products WHERE description = ?)""",
                            (Products[i].name,),
                        ).fetchall()
                        for row in range(len(items_id)):
                            database.execute(
                                """UPDATE inventory
                            SET stored_quantity = (SELECT stored_quantity
                            FROM inventory WHERE item_id = ?) - ? WHERE item_id = ?""",
                                (
                                    items_id[row][0],
                                    Products[i].quantity,
                                    items_id[row][0],
                                ),
                            )
                        total_sale += int(Products[i].total)
                        # TODO: Create entity to save total income
                        # TODO: Update balance table
                        database.commit()
                except NameError as e:
                    flash(e.args[i])
                    return redirect(url_for("checkout.new_sale"))
            if not_enough > 0:
                return redirect(url_for("checkout.new_sale"))
            flash("Sell saved")

        return redirect(url_for("checkout.new_sale"))
    return render_template("checkout/new_sale.html")
