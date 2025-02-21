import sqlite3
from flask import Flask, g, request, render_template, redirect, url_for
from database_manager import execute_db_query  # Import the database function

app = Flask(__name__)

# DATABASE = 'holzbau.db'  # No longer needed here

# Helper function to get the database connection (modified)
def get_db():
    if 'db' not in g:
       g.db = True # placeholder, since we are not using direct sqlite connection here
    return g.db

# Close the database connection when the request ends (modified)
@app.teardown_appcontext
def close_db(exception):
    g.pop('db', None) # nothing to close

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# ---------------------- Customers ----------------------

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = execute_db_query("SELECT * FROM Customer_DB")
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['POST'])
def add_customer():
    name = request.form['Name']
    lastname = request.form['LastName']
    age = request.form['Age']
    country = request.form['Country']
    execute_db_query("INSERT INTO Customer_DB (Name, LastName, Age, Country) VALUES (?, ?, ?, ?)", (name, lastname, age, country))
    return redirect(url_for('get_customers'))

@app.route('/customers/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    name = request.form['Name']
    lastname = request.form['LastName']
    age = request.form['Age']
    country = request.form['Country']
    execute_db_query("UPDATE Customer_DB SET Name = ?, LastName = ?, Age = ?, Country = ? WHERE CustomerId = ?", (name, lastname, age, country, customer_id))
    return redirect(url_for('get_customers'))

@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    execute_db_query("DELETE FROM Customer_DB WHERE CustomerId = ?", (customer_id,))
    return redirect(url_for('get_customers'))

# ---------------------- Orders ----------------------

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = execute_db_query("SELECT * FROM Order_DB")
    return render_template('orders.html', orders=orders)

@app.route('/orders/add', methods=['POST'])
def add_order():
    customer_id = request.form['CustomerId']
    description = request.form['Description']
    price = request.form['Price']
    amount = request.form['Amount']
    date = request.form['Date']
    execute_db_query("INSERT INTO Order_DB (CustomerId, Description, Price, Amount, Date) VALUES (?, ?, ?, ?, ?)", (customer_id, description, price, amount, date))
    return redirect(url_for('get_orders'))

@app.route('/orders/edit/<int:order_id>', methods=['POST'])
def edit_order(order_id):
    customer_id = request.form['CustomerId']
    description = request.form['Description']
    price = request.form['Price']
    amount = request.form['Amount']
    date = request.form['Date']
    execute_db_query("UPDATE Order_DB SET CustomerId = ?, Description = ?, Price = ?, Amount = ?, Date = ? WHERE OrderId = ?", (customer_id, description, price, amount, date, order_id))
    return redirect(url_for('get_orders'))

@app.route('/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    execute_db_query("DELETE FROM Order_DB WHERE OrderId = ?", (order_id,))
    return redirect(url_for('get_orders'))

# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True)