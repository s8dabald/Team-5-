from flask import Flask, request, render_template, redirect, url_for, jsonify
from services.data_analysis import get_dashboard_data, get_loyal_customers
from database_manager import execute_db_query
from services.employee_analysis import get_employee_distributions
from services.recommendation_engine import get_most_common_customer_combinations, get_combinations_for_item

# Initialize the Flask application
app = Flask(__name__)

# ---------------------- Home Route ----------------------

@app.route('/')
def home():
    """Render the landing page."""
    return render_template('index.html')


# ---------------------- Customers ----------------------

@app.route('/customers', methods=['GET'])
def get_customers():
    """Retrieve all customers from the database and display them on the customers page."""
    query = "SELECT * FROM Customer_DB"
    customers = execute_db_query(query, as_dict=True)  # Fetch customers as a dictionary
    return render_template('customers.html', customers=customers)


@app.route('/customers/add', methods=['POST'])
def add_customer():
    """Add a new customer to the database and redirect to the customers list page."""
    name = request.form['Name']
    lastname = request.form['LastName']
    age = request.form['Age']
    country = request.form['Country']

    query = """
        INSERT INTO Customer_DB (Name, LastName, Age, Country) 
        VALUES (?, ?, ?, ?)
    """
    params = (name, lastname, age, country)

    execute_db_query(query, params)
    return redirect(url_for('get_customers'))


@app.route('/customers/edit/<int:customer_id>', methods=['POST'])
def edit_customer(customer_id):
    """Edit an existing customer's details in the database."""
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

    execute_db_query(query, params)
    return redirect(url_for('get_customers'))


@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    """Delete a customer from the database."""
    query = "DELETE FROM Customer_DB WHERE CustomerId = ?"
    params = (customer_id,)

    execute_db_query(query, params)
    return redirect(url_for('get_customers'))


# ---------------------- Loyal Customers ----------------------

@app.route("/loyal_customers")
def top_customers():
    """Retrieve and display the most loyal customers based on order frequency and spending."""
    top_orders, top_spenders = get_loyal_customers()
    return render_template("loyal_customers.html", top_orders=top_orders, top_spenders=top_spenders)


# ---------------------- Orders ----------------------

@app.route('/orders', methods=['GET'])
def get_orders():
    """Retrieve all orders from the database and display them on the orders page."""
    query = "SELECT * FROM Order_DB"
    orders = execute_db_query(query, as_dict=True)
    return render_template('orders.html', orders=orders)


@app.route('/orders/add', methods=['POST'])
def add_order():
    """Add a new order to the database and redirect to the orders list page."""
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

    execute_db_query(query, params)
    return redirect(url_for('get_orders'))


@app.route('/orders/edit/<int:order_id>', methods=['POST'])
def edit_order(order_id):
    """Edit an existing order in the database."""
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

    execute_db_query(query, params)
    return redirect(url_for('get_orders'))


@app.route('/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    """Delete an order from the database."""
    query = "DELETE FROM Order_DB WHERE OrderId = ?"
    params = (order_id,)

    execute_db_query(query, params)
    return redirect(url_for('get_orders'))


# ---------------------- Dashboard ----------------------

@app.route("/dashboard")
def dashboard():
    """Retrieve key business metrics and display them on the dashboard page."""
    country_distribution, popular_products, segments, sales_trend = get_dashboard_data()

    return render_template("dashboard.html", country_distribution=country_distribution,
                           popular_products=popular_products, segments=segments,
                           sales_trend=sales_trend)


# ---------------------- Employees ----------------------

@app.route('/employee_analysis')
def employee():
    """Retrieve employee analytics data and display it on the employee analysis page."""
    employee_country_distribution, employee_job_distribution = get_employee_distributions()
    return render_template("employees.html", employee_country_distribution=employee_country_distribution,
                           employee_job_distribution=employee_job_distribution)


# ---------------------- Offers ----------------------

@app.route('/offers', methods=['GET'])
def offers():
    """Retrieve and display current promotional offers."""
    try:
        offers_data = {}
        rows = execute_db_query("SELECT holiday, active, percentage FROM Offers", as_dict=True)
        if rows:
            for row in rows:
                offers_data[row['holiday']] = {'active': bool(row['active']), 'percentage': row['percentage']}
    except Exception as e:
        print(f"Error fetching offers: {e}")
        offers_data = {}

    return render_template('offers.html', offers=offers_data)


@app.route('/save_offers', methods=['POST'])
def save_offers():
    """Save promotional offers settings to the database."""
    try:
        offers_data = request.get_json()
        for holiday, settings in offers_data.items():
            rows_affected = execute_db_query(
                "INSERT OR REPLACE INTO Offers (holiday, active, percentage) VALUES (?, ?, ?)",
                (holiday, settings['active'], settings['percentage'])
            )
            if rows_affected is None:
                return jsonify({'error': 'Error saving offers'}), 500
        return jsonify({'message': 'Offers saved successfully'}), 200
    except Exception as e:
        print(f"Error saving offers: {e}")
        return jsonify({'error': 'Error saving offers'}), 500


# ---------------------- Recommendation Engine ----------------------

def get_unique_products():
    """Retrieve a list of unique products from the order database."""
    query = "SELECT DISTINCT Description FROM Order_DB"
    products = execute_db_query(query, as_dict=True)
    return [product["Description"] for product in products]


@app.route('/recommendation_engine/', methods=['GET'])
def order_combinations():
    """Display frequently bought-together items and allow product-based searches."""
    static_combinations = get_most_common_customer_combinations()
    product_list = get_unique_products()
    return render_template('recommendation_engine.html',
                           static_combinations=static_combinations,
                           product_list=product_list,
                           search_item=None)


@app.route('/recommendation_engine/search', methods=['POST'])
def search_order_combinations():
    """Retrieve product recommendations based on a searched item."""
    item = request.form['item'].strip().lower()
    relative_frequencies, item_occurrences = get_combinations_for_item(item)
    search_top_combinations = [(combo, count) for combo, count, _ in relative_frequencies]
    static_combinations = get_most_common_customer_combinations()
    product_list = get_unique_products()
    total_combinations = item_occurrences
    return render_template('recommendation_engine.html',
                           static_combinations=static_combinations,
                           product_list=product_list,
                           search_item=item,
                           search_top_combinations=search_top_combinations,
                           total_combinations=total_combinations)


# ---------------------- Run Flask Application ----------------------

if __name__ == '__main__':
    app.run(debug=True)  # Start the Flask server in debug mode
