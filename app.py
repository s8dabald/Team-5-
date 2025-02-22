from flask import Flask, request, render_template, redirect, url_for, jsonify
from database_manager import execute_db_query  # Import the execute_db_query function

# Create the Flask app
app = Flask(__name__)


# Home route
@app.route('/')
def home():
    return render_template('index.html')  # Landing page


# ---------------------- Customers ----------------------

# List all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    query = "SELECT * FROM Customer_DB"  # Query to select all customers
    customers = execute_db_query(query)  # Call the execute_db_query function to fetch customers
    return render_template('customers.html', customers=customers)


# Add a new customer
@app.route('/customers/add', methods=['POST'])
def add_customer():
    name = request.form['Name']
    lastname = request.form['LastName']
    age = request.form['Age']
    country = request.form['Country']

    query = """
        INSERT INTO Customer_DB (Name, LastName, Age, Country) 
        VALUES (?, ?, ?, ?)
    """
    params = (name, lastname, age, country)

    execute_db_query(query, params)  # Add the new customer to the database
    return redirect(url_for('get_customers'))  # Redirect to the customers list page


# Edit an existing customer
@app.route('/customers/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    name = request.form['Name']
    lastname = request.form['LastName']
    age = request.form['Age']
    country = request.form['Country']

    query = """
        UPDATE Customer_DB 
        SET Name = ?, LastName = ?, Age = ?, Country = ? 
        WHERE CustomerId = ?
    """
    params = (name, lastname, age, country, customer_id)

    execute_db_query(query, params)  # Update the customer information in the database
    return redirect(url_for('get_customers'))  # Redirect to the customers list page


# Delete a customer
@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    query = "DELETE FROM Customer_DB WHERE CustomerId = ?"
    params = (customer_id,)

    execute_db_query(query, params)  # Delete the customer from the database
    return redirect(url_for('get_customers'))  # Redirect to the customers list page


# ---------------------- Orders ----------------------

# List all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    query = "SELECT * FROM Order_DB"  # Query to select all orders
    orders = execute_db_query(query)  # Call the execute_db_query function to fetch orders
    return render_template('orders.html', orders=orders)


# Add a new order
@app.route('/orders/add', methods=['POST'])
def add_order():
    customer_id = request.form['CustomerId']
    description = request.form['Description']
    price = request.form['Price']
    amount = request.form['Amount']
    date = request.form['Date']

    query = """
        INSERT INTO Order_DB (CustomerId, Description, Price, Amount, Date) 
        VALUES (?, ?, ?, ?, ?)
    """
    params = (customer_id, description, price, amount, date)

    execute_db_query(query, params)  # Add the new order to the database
    return redirect(url_for('get_orders'))  # Redirect to the orders list page


# Edit an existing order
@app.route('/orders/edit/<int:order_id>', methods=['POST'])
def edit_order(order_id):
    customer_id = request.form['CustomerId']
    description = request.form['Description']
    price = request.form['Price']
    amount = request.form['Amount']
    date = request.form['Date']

    query = """
        UPDATE Order_DB 
        SET CustomerId = ?, Description = ?, Price = ?, Amount = ?, Date = ? 
        WHERE OrderId = ?
    """
    params = (customer_id, description, price, amount, date, order_id)

    execute_db_query(query, params)  # Update the order information in the database
    return redirect(url_for('get_orders'))  # Redirect to the orders list page


# Delete an order
@app.route('/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    query = "DELETE FROM Order_DB WHERE OrderId = ?"
    params = (order_id,)

    execute_db_query(query, params)  # Delete the order from the database
    return redirect(url_for('get_orders'))  # Redirect to the orders list page

#For the offers screen
@app.route('/offers', methods=['GET'])
def offers():
    try:
        offers_data = {}
        rows = execute_db_query("SELECT holiday, active, percentage FROM Offers")  # Note: "Offers" (capital O)
        if rows:
            for row in rows:
                offers_data[row['holiday']] = {'active': bool(row['active']), 'percentage': row['percentage']}

    except Exception as e:
        print(f"Error fetching offers: {e}")
        offers_data = {}  # Provide a default value in case of error

    return render_template('offers.html', offers=offers_data)

@app.route('/save_offers', methods=['POST'])
def save_offers():
    try:
        offers_data = request.get_json()
        for holiday, settings in offers_data.items():
            rows_affected = execute_db_query(
                "INSERT OR REPLACE INTO Offers (holiday, active, percentage) VALUES (?, ?, ?)",
                (holiday, settings['active'], settings['percentage'])
            )
            if rows_affected is None:  # Check for database errors
                return jsonify({'error': 'Error saving offers'}), 500  # Return error
        return jsonify({'message': 'Offers saved successfully'}), 200
    except Exception as e:
        print(f"Error saving offers: {e}")
        return jsonify({'error': 'Error saving offers'}), 500
# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True)
