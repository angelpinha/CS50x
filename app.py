from flask import Flask, render_template, url_for
from sqlalchemy import create_engine, text

app = Flask(__name__)

db = create_engine("sqlite+pysqlite:///prototype.db", echo=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/invoices')
def invoices():
    return render_template('invoices.html')

@app.route('/inventory')
def inventory():
    with db.connect() as conn:
        table = conn.execute(text
                ("""SELECT name, cost_center, format, size, size_value, initial_value, warehouse, counter
                FROM items, inventory WHERE items.id = inventory.item_id"""))

    return render_template('inventory.html', table=table)
