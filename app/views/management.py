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
import re

management = Blueprint("management", __name__)
database = LocalProxy(get_db)


@management.route("/management")
@login_required
def management_layout():
    return render_template("management/management.html")


@management.route("/balance")
@login_required
def balance():
    # Get the total money earned from sales
    revenues = database.execute("SELECT revenues FROM balance").fetchone()
    # Get the total money spent on purchases
    expenses = database.execute("SELECT expenses FROM balance").fetchone()
    # Get the total income
    income = database.execute("SELECT income FROM balance").fetchone()
    # Get 0 if no sales
    if revenues[0] is None:
        revenues = 0
    else:
        revenues = revenues[0]
    # Get 0 if no purchases
    if expenses[0] is None:
        expenses = 0
    else:
        expenses = expenses[0]
    # Calculate income
    income = revenues - expenses
    # Return balance
    table = [revenues, expenses, income]
    return render_template("management/balance.html", table=table)


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
        # Product attributes
        PRODUCT = {
            "name": request.form.get("NAME"),
            "category": request.form.get("CATEGORY"),
            "sell_value": request.form.get("VALUE"),
        }

        # Product components
        for i in range(int(request.form.get("quantity")) - 3):
            PRODUCT[f"component_{i+1}"] = request.form.get(f"component{i+1}")
            for j in range(i):
                if PRODUCT[f"component_{i+1}"] == PRODUCT[f"component_{j+1}"]:
                    flash("The same item cannot be used twice")
                    return redirect(url_for("management.new_product"))

            # Ensure item isn't already in use
            if PRODUCT[f"component_{i+1}"]:
                item_ocupied = database.execute(
                    "SELECT product_id FROM items WHERE name = ?",
                    (PRODUCT[f"component_{i+1}"],),
                ).fetchone()
                if item_ocupied[0] != None:
                    flash(
                        f"One of the items selected is in use already: {PRODUCT[f'component_{i+1}']}"
                    )
                    return redirect(url_for("management.new_product"))

        # Ensure product doesn't exist yet
        if PRODUCT["name"]:
            name_ocupied = database.execute(
                "SELECT description FROM products WHERE description = ?",
                (PRODUCT["name"],),
            ).fetchone()
            if name_ocupied:
                flash("The name provided is already in use")
                return redirect(url_for("management.new_product"))

        if PRODUCT["category"] and PRODUCT["sell_value"]:
            database.execute(
                "INSERT INTO products (description, price, category) VALUES (?, ?, ?)",
                (PRODUCT["name"], PRODUCT["sell_value"], PRODUCT["category"]),
            )

        # Process each product to enter it in the database
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

    # Fetch product categories from database
    categories = database.execute("SELECT product_category FROM categories").fetchall()
    return render_template("management/new_product.html", categories=categories)


# Create new category of product
@management.route("/new_category", methods=["GET", "POST"])
@login_required
def new_category():
    if request.method == "POST":
        product_category = request.form.get("product_category")
        # Ensuring name is spelled correctly
        if product_category and product_category.isalpha() == True:
            # Verify that name is not already in use
            existing_name = database.execute(
                "SELECT product_category FROM categories WHERE product_category = ?",
                (product_category,),
            ).fetchone()
            if not existing_name:
                database.execute(
                    "INSERT INTO categories (product_category) VALUES (?)",
                    (product_category,),
                )
                database.commit()
                flash("New category created")
                return redirect(url_for("management.new_category"))

            # Otherwise redirect
            flash("The category already exists")
            return redirect(url_for("management.new_category"))
        # If the name is invalid
        flash("Invalid name")
        return redirect(url_for("management.new_category"))

    return render_template("management/new_category.html")


@management.route("/new_item", methods=["GET", "POST"])
@login_required
def new_item():
    if request.method == "POST":
        # Create query to construct a new database entity
        ITEM = {
            "name": request.form.get("name"),
            "cost_center": request.form.get("cost_center"),
            "format": request.form.get("format"),
            "unit": request.form.get("unit"),
            "value": request.form.get("value"),
        }

        # Make sure the name provided is not in use
        item_ocupied = database.execute(
            "SELECT name FROM items WHERE name = ?",
            (ITEM["name"],),
        ).fetchone()
        if item_ocupied:
            flash("The item name provided is already in use")
            return redirect(url_for("management.new_item"))

        # Make sure each entry has been written
        validation = 0
        fields_required = 5
        for key, value in ITEM.items():
            if ITEM[key]:
                validation += 1
        if validation == fields_required:
            database.execute(
                """INSERT INTO items (name, cost_center, format, unit, updated_price) VALUES (?,?,?,?,?)""",
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

    COST_CENTER = ["Operational", "Personal", "Machinery", "Product"]
    UNITS = ["u", "g", "ml"]
    return render_template(
        "management/new_item.html", cost_center=COST_CENTER, units=UNITS
    )


# Search route to fetch values from client side
@management.route("/search")
@login_required
def search():
    item_q = request.args.get("item_q")
    supplier_q = request.args.get("supplier_q")
    product_q = request.args.get("product_q")

    Json = []
    # Search item name
    if item_q:
        items = database.execute(
            "SELECT name FROM items WHERE name LIKE ?||?", (item_q, "%")
        ).fetchall()

        for row in range(len(items)):
            Json.append({"name": items[row]["name"]})

    # Search supplier name
    elif supplier_q:
        suppliers = database.execute(
            "SELECT supplier_name FROM suppliers WHERE supplier_name LIKE ?||?",
            (supplier_q, "%"),
        ).fetchall()

        for row in range(len(suppliers)):
            Json.append({"name": suppliers[row]["supplier_name"]})

    # Search product name and price
    elif product_q:
        products = database.execute(
            "SELECT description, ROUND(price, 2) AS price FROM products WHERE description LIKE ?||?",
            (product_q, "%"),
        ).fetchall()

        for row in range(len(products)):
            Json.append(
                {"name": products[row]["description"], "price": products[row]["price"]}
            )

    return Json


@management.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory():
    # Return the item and its values
    if request.method == "POST":
        item = request.form.get("item")

        if item:
            table = database.execute(
                """SELECT name, stored_quantity, unit, ROUND(updated_price, 2)
                    FROM items INNER JOIN inventory
                    ON items.id = inventory.item_id
                    WHERE name = ?""",
                (item,),
            ).fetchall()
            # Return the item typed in search
            return render_template("management/inventory.html", table=table)

    table = database.execute(
        """SELECT name, stored_quantity, unit, ROUND(updated_price, 2)
                    FROM items INNER JOIN inventory
                    ON items.id = inventory.item_id LIMIT 10"""
    )
    # Return a general list of items
    return render_template("management/inventory.html", table=table)


# Purchases template
@management.route("/purchases")
@login_required
def purchases():
    return render_template("management/purchases.html")


# Item class to validate a purchase
class Purchase_item:
    def __init__(self, fields):
        self.name = fields["name"]
        self.quantity = fields["quantity"]
        self.unit_value = fields["unit_value"]
        self.subtotal = fields["subtotal"]

    # Function to make printable each property of the instance, as a formatted string
    def __str__(self):
        return f"name:{self.name}, quantity:{self.quantity}, unit value: {self.unit_value}, subtotal: {self.subtotal}"

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

    # unit value getter, to return the unit_value property of an instance
    @property
    def unit_value(self):
        return self._unit_value

    # unit value setter, to return the unit_value property of an instance
    @unit_value.setter
    def unit_value(self, unit_value):
        if not unit_value or unit_value.isnumeric() == False:
            raise NameError("Failed to provide valid unit value")
        self._unit_value = unit_value


# wap (weighted average price) function, to update an item value
def wap(Prices):
    prices_and_quantities = []
    checked = []
    for i in range(len(Prices)):
        current_price = Prices[i][0]
        quantity = Prices[i][1]

        if current_price not in checked:
            if i < len(Prices) - 1:
                for j in range(i + 1, len(Prices), 1):
                    next_price = Prices[j][0]
                    if current_price == next_price:
                        quantity += Prices[j][1]
            n_price_by_quantity = current_price * quantity

            prices_and_quantities.append((n_price_by_quantity, quantity))
            checked.append(current_price)

    total_price_by_quantity = prices_and_quantities[0][0]
    total_quantity = prices_and_quantities[0][1]
    for p in range(1, len(prices_and_quantities), 1):
        total_price_by_quantity = total_price_by_quantity + prices_and_quantities[p][0]
        total_quantity = total_quantity + prices_and_quantities[p][1]

    wheighted_average = total_price_by_quantity / total_quantity
    return wheighted_average


@management.route("/new_purchase", methods=["GET", "POST"])
@login_required
def new_purchase():
    if request.method == "POST":
        Invoice_info = {
            "Supplier name": request.form.get("supplier_name"),
            "Invoice number": request.form.get("invoice_number"),
            "Invoice date": request.form.get("invoice_date"),
        }
        # Ensure user provide valid invoice info
        validation = 0
        for key, value in Invoice_info.items():
            if not Invoice_info[key]:
                validation += 1
                flash(f"Invalid {key}")
        if validation > 0:
            flash("Failed to provide invoice info")
            return redirect(url_for("management.new_purchase"))

        exist_invoice_number = database.execute(
            """SELECT invoice_number FROM purchases WHERE invoice_number = ?""",
            (Invoice_info["Invoice number"],),
        ).fetchone()
        if exist_invoice_number:
            flash("invoice number already exists")
            return redirect(url_for("management.new_purchase"))

        Purchase = []
        item_number = request.form.get("item_number")
        if item_number:
            total_price = 0
            for i in range(int(item_number)):
                Purchase.append(
                    {
                        "name": request.form.get(f"name_{i+1}"),
                        "quantity": request.form.get(f"quantity_{i+1}"),
                        "unit_value": request.form.get(f"value_{i+1}"),
                        "subtotal": request.form.get(f"total_{i+1}"),
                    }
                )

                try:
                    Purchase[i] = Purchase_item(Purchase[i])

                    database.execute(
                        """UPDATE inventory
                    SET stored_quantity = (
                    SELECT stored_quantity
                    FROM inventory
                    WHERE item_id = (
                        SELECT id
                        FROM items
                        WHERE name = ?
                        )
                        ) + ?
                    WHERE item_id = (
                    SELECT id
                    FROM items
                    WHERE name = ?
                    )""",
                        (Purchase[i].name, Purchase[i].quantity, Purchase[i].name),
                    )

                    database.execute(
                        """INSERT INTO purchases (item_id, supplier_id, invoice_number, date, quantity, purchase_price)
                        VALUES ((SELECT id FROM items WHERE name = ?),
                        (SELECT id FROM suppliers WHERE supplier_name = ?),
                        ?, ?, ?, ?)""",
                        (
                            Purchase[i].name,
                            Invoice_info["Supplier name"],
                            Invoice_info["Invoice number"],
                            Invoice_info["Invoice date"],
                            Purchase[i].quantity,
                            Purchase[i].unit_value,
                        ),
                    )

                    prices = database.execute(
                        """SELECT purchase_price, quantity FROM purchases WHERE date IN (SELECT DISTINCT date 
                            FROM purchases
                            WHERE item_id = (SELECT id FROM items WHERE name = ?))
                            AND item_id = (SELECT id FROM items WHERE name = ?)""",
                        (Purchase[i].name, Purchase[i].name),
                    ).fetchall()

                    # Update new purchase value of the item
                    database.execute(
                        "UPDATE items SET updated_price = ? WHERE name = ?",
                        (wap(prices), Purchase[i].name),
                    )
                    # Update total purchase price
                    total_price += float(Purchase[i].subtotal)

                except NameError as e:
                    flash(e.args[i])
                    return redirect(url_for("management.new_purchase"))

            # Calculate revenues, expenses
            revenues = database.execute("SELECT revenues FROM balance").fetchone()[0]
            if not revenues:
                revenues = 0
            expenses = database.execute("SELECT expenses FROM balance").fetchone()[0]
            if not expenses:
                expenses = 0

            # Check if there is registry and income greater than or equal to the total purchase price
            income = database.execute("SELECT income FROM balance").fetchone()[0]
            if income < total_price:
                flash("There are insufficient funds to make this purchase")
                return redirect(url_for("management.new_purchase"))

            # Update balance table
            new_expenses = expenses + total_price
            new_income = revenues - new_expenses
            database.execute(
                "UPDATE balance SET expenses = ?, income = ? WHERE id = 1",
                (
                    new_expenses,
                    new_income,
                ),
            )

            # Update product value (40% of profit)
            for item in range(len(Purchase)):
                database.execute(
                    """UPDATE products SET price = (SELECT SUM(updated_price) * 1.4
                FROM items WHERE product_id = (SELECT product_id FROM items WHERE name = ?))
                WHERE id = (SELECT product_id FROM items WHERE name = ?)""",
                    (
                        Purchase[item].name,
                        Purchase[item].name,
                    ),
                )
            database.commit()
            flash("New purchase saved")
            return redirect(url_for("management.new_purchase"))

        else:
            flash("Failed to provide an item to purchase")
            return redirect(url_for("management.new_purchase"))

    return render_template("management/new_purchase.html")


# TODO: Show saved invoices
@management.route("/invoices")
@login_required
def invoices():
    return render_template("management/invoices.html")


@management.route("/new_supplier", methods=["GET", "POST"])
@login_required
def new_supplier():
    # Global list of supplier status
    STATUS = ["Active", "Inactive"]

    if request.method == "POST":
        supplier = request.form.get("supplier")
        status = request.form.get("status")
        # Check if supplier already exists
        if supplier:
            existing_supplier = database.execute(
                "SELECT supplier_name FROM suppliers WHERE supplier_name = ?",
                (supplier,),
            ).fetchone()
            if existing_supplier:
                flash("supplier name already exists")
                return redirect(url_for("management.new_supplier"))

            if status in STATUS:
                # Save supplier into database
                database.execute(
                    "INSERT INTO suppliers (supplier_name, status) VALUES (?, ?)",
                    (supplier, status),
                )
                database.commit()
                flash("New supplier added")
                return redirect(url_for("management.new_supplier"))

        flash("Failed to provide correct information")
        return redirect(url_for("management.new_supplier"))

    return render_template("management/new_supplier.html", status=STATUS)
