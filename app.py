#these are code packages which have useful pre-written functions
import sqlite3
from flask import Flask, g, request, render_template, redirect, url_for

#this creates our website
app = Flask(__name__)

#this is the name of our database
DATABASE = 'holzbau.db'

#this function connects our code to the database
def get_db():
    # checks if we are not connected to the database
    if 'db' not in g:
	# connect to the database
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Enable access by column name
    # returns the database
    return g.db

#when website closes, dısconnects the database from the website
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#everything till here is part 1

# this shows the home page
@app.route('/')
def home():
    return render_template('index.html')

#shows list of all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    # gets the database
    db = get_db()
    cursor = db.cursor()
    #selects all the customer data
    cursor.execute("SELECT * FROM Customer_DB")
    customers = cursor.fetchall()
    #sends all the customer data to be shown
    return render_template('customers.html', customers=customers)

#adds new customer
@app.route('/customers/add', methods=['POST'])
def add_customer():
    #gets the database
    db = get_db()
    cursor = db.cursor()
    #gets the information from the webpage to insert customer data into our database
    name = request.form['Name']
    lastname = request.form['LastName']
    age = request.form['Age']
    country = request.form['Country']
    #inserts customer information into database
    cursor.execute("INSERT INTO Customer_DB (Name, LastName, Age, Country) VALUES (?, ?, ?, ?)", (name, lastname, age, country))
    db.commit()
    #returns to the page with list of all customers
    return redirect(url_for('get_customers'))

#edits the information for a customer given customer id
@app.route('/customers/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    db = get_db()
    cursor = db.cursor()
    
    name = request.form['Name']
    lastname = request.form['LastName']
    age = request.form['Age']
    country = request.form['Country']
    #updates the information for the given customer
    cursor.execute("UPDATE Customer_DB SET Name = ?, LastName = ?, Age = ?, Country = ? WHERE CustomerId = ?", 
                   (name, lastname, age, country, customer_id))
    db.commit()
    
    return redirect(url_for('get_customers'))

#deletes a customer given customer_id
@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    db = get_db()
    cursor = db.cursor()
    # deletes customer from the database
    cursor.execute("DELETE FROM Customer_DB WHERE CustomerId = ?", (customer_id,))
    db.commit()
    
    return redirect(url_for('get_customers'))

#list all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    db = get_db()
    cursor = db.cursor()
    # gets the list of all orders from the database
    cursor.execute("SELECT * FROM Order_DB")
    orders = cursor.fetchall()
    #shows the list of all orders on the website
    return render_template('orders.html', orders=orders)

#adds a new order to our database
@app.route('/orders/add', methods=['POST'])
def add_order():
    db = get_db()
    cursor = db.cursor()
    
    #gets information about the order from the webpage
    customer_id = request.form['CustomerId']
    description = request.form['Description']
    price = request.form['Price']
    amount = request.form['Amount']
    date = request.form['Date']
    
    #inserts information about the order into the database
    cursor.execute("INSERT INTO Order_DB (CustomerId, Description, Price, Amount, Date) VALUES (?, ?, ?, ?, ?)", 
                   (customer_id, description, price, amount, date))
    db.commit()
    
    #returns to the webpage with the order information
    return redirect(url_for('get_orders'))

#edits an order given an order id
@app.route('/orders/edit/<int:order_id>', methods=['POST'])
def edit_order(order_id):
    db = get_db()
    cursor = db.cursor()
    
    #gets information about the order from the webpage
    customer_id = request.form['CustomerId']
    description = request.form['Description']
    price = request.form['Price']
    amount = request.form['Amount']
    date = request.form['Date']
    
    #updates information in the database for that order
    cursor.execute("UPDATE Order_DB SET CustomerId = ?, Description = ?, Price = ?, Amount = ?, Date = ? WHERE OrderId = ?", 
                   (customer_id, description, price, amount, date, order_id))
    db.commit()
    
    return redirect(url_for('get_orders'))

#deletes an order from the order database
@app.route('/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    db = get_db()
    cursor = db.cursor()
    #delete the order with the right order id from the database
    cursor.execute("DELETE FROM Order_DB WHERE OrderId = ?", (order_id,))
    db.commit()
    return redirect(url_for('get_orders'))

#everything till here is part 2

#starts the webpage
if __name__ == '__main__':
    app.run(debug=False)
    #done with task 1 and task 2

