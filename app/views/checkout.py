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


# product class to validate each product to be sold
class Sell_product:
    def __init__(self, fields):
        self.name = fields["name"]
        self.quantity = fields["quantity"]
        self.total = fields["total"]

    # Function to make printable each property of the instance, as a formatted string
    def __str__(self):
        return f"name:{self.name}, quantity:{self.quantity}, total:{self.total}"

    # name getter, to return the name property of an instance
    @property
    def name(self):
        return self._name

    # Name setter, to construct the name property of an instance
    @name.setter
    def name(self, name):
        if not name:
            raise NameError("Failed to provide valid name")
        self._name = name

    # Quantity getter, to return the quantity property of an instance
    @property
    def quantity(self):
        return self._quantity

    # Quantity setter, to construct the quantity property of an instance
    @quantity.setter
    def quantity(self, quantity):
        if not quantity or quantity.isnumeric() == False:
            raise NameError("Failed to provide valid quantity")
        self._quantity = quantity

    # Total getter, to return the total property of an instance
    @property
    def total(self):
        return self._total

    # Total setter, to construct the total property of an instance
    @total.setter
    def total(self, total):
        if not total or total.replace(".", "", 1).isnumeric() == False:
            raise NameError("Invalid total value")
        self._total = total


@checkout.route("/new_sale", methods=["GET", "POST"])
@login_required
def new_sale():
    if request.method == "POST":
        # list to save each product to sell
        Products = []
        # Get the number of products to sell
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
                    # Create a new instance of the Sell_product class
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
                    # Check if there is enough quantity of items to sell
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
                        total_sale += float(Products[i].total)
                except NameError as e:
                    flash(e.args[i])
                    return redirect(url_for("checkout.new_sale"))
            if not_enough > 0:
                return redirect(url_for("checkout.new_sale"))
            # Set the number of transaction
            last_transaction_number = database.execute(
                "SELECT MAX(transaction_number) FROM sales"
            ).fetchone()
            if last_transaction_number[0]:
                new_transaction_number = last_transaction_number[0] + 1
            else:
                new_transaction_number = 1
            # Update sales table
            for product in range(int(product_number)):
                database.execute(
                    """INSERT INTO sales (transaction_number, product_id, quantity, amount)
                    VALUES (?, (SELECT id FROM products WHERE description = ?), ?, ?)""",
                    (
                        new_transaction_number,
                        Products[product].name,
                        Products[product].quantity,
                        Products[product].total,
                    ),
                )
            revenues = database.execute("SELECT revenues FROM balance").fetchone()[0]
            new_revenues = revenues + total_sale
            expenses = database.execute("SELECT expenses FROM balance").fetchone()[0]
            new_income = new_revenues - expenses
            database.execute(
                "UPDATE balance SET revenues = ?, income = ? WHERE id = 1",
                (new_revenues, new_income),
            )
            database.commit()
            flash("Sale completed")

        return redirect(url_for("checkout.new_sale"))
    return render_template("checkout/checkout.html")
