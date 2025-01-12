import sqlite3
from flask import Flask, g, request, render_template, redirect, url_for

#create the Flask app
app = Flask(__name__)

DATABASE = 'holzbau.db'

#helper function to get the database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Enable access by column name
    return g.db

#close the database connection when the request ends
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#everything till here is part 1

# Home route
@app.route('/')
def home():
    return render_template('index.html')  # Landing page

# ---------------------- Customers ----------------------

#List all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Customer_DB")
    customers = cursor.fetchall()
    return render_template('customers.html', customers=customers)

#Add a new customer
@app.route('/customers/add', methods=['POST'])
def add_customer():
    db = get_db()
    cursor = db.cursor()
    name = request.form['Name']
    lastname = request.form['LastName']
    age = request.form['Age']
    country = request.form['Country']
    cursor.execute("INSERT INTO Customer_DB (Name, LastName, Age, Country) VALUES (?, ?, ?, ?)", (name, lastname, age, country))
    db.commit()
    return redirect(url_for('get_customers'))

#Edit an existing customer
@app.route('/customers/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    db = get_db()
    cursor = db.cursor()
    name = request.form['Name']
    lastname = request.form['LastName']
    age = request.form['Age']
    country = request.form['Country']
    cursor.execute("UPDATE Customer_DB SET Name = ?, LastName = ?, Age = ?, Country = ? WHERE CustomerId = ?", 
                   (name, lastname, age, country, customer_id))
    db.commit()
    return redirect(url_for('get_customers'))

#Delete a customer
@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Customer_DB WHERE CustomerId = ?", (customer_id,))
    db.commit()
    return redirect(url_for('get_customers'))

# ---------------------- Orders ----------------------

#List all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Order_DB")
    orders = cursor.fetchall()
    return render_template('orders.html', orders=orders)

#Add a new order
@app.route('/orders/add', methods=['POST'])
def add_order():
    db = get_db()
    cursor = db.cursor()
    customer_id = request.form['CustomerId']
    description = request.form['Description']
    price = request.form['Price']
    amount = request.form['Amount']
    date = request.form['Date']
    cursor.execute("INSERT INTO Order_DB (CustomerId, Description, Price, Amount, Date) VALUES (?, ?, ?, ?, ?)", 
                   (customer_id, description, price, amount, date))
    db.commit()
    return redirect(url_for('get_orders'))

#Edit an existing order
@app.route('/orders/edit/<int:order_id>', methods=['POST'])
def edit_order(order_id):
    db = get_db()
    cursor = db.cursor()
    customer_id = request.form['CustomerId']
    description = request.form['Description']
    price = request.form['Price']
    amount = request.form['Amount']
    date = request.form['Date']
    cursor.execute("UPDATE Order_DB SET CustomerId = ?, Description = ?, Price = ?, Amount = ?, Date = ? WHERE OrderId = ?", 
                   (customer_id, description, price, amount, date, order_id))
    db.commit()
    return redirect(url_for('get_orders'))

#Delete an order
@app.route('/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Order_DB WHERE OrderId = ?", (order_id,))
    db.commit()
    return redirect(url_for('get_orders'))

#everything till here is part 2

# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True)


