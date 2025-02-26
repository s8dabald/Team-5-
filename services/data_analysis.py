import pandas as pd
from sklearn.cluster import KMeans
from database_manager import execute_db_query


def get_data():
    """
    Retrieves customer and order data from the database and stores them in DataFrames.

    Returns:
        tuple: Two Pandas DataFrames (customers, orders). If no data is available, empty DataFrames are returned.
    """
    customer_data = execute_db_query("SELECT * FROM Customer_DB", as_dict=True)
    customers = pd.DataFrame([dict(row) for row in customer_data]) if customer_data else pd.DataFrame()

    order_data = execute_db_query("SELECT * FROM Order_DB", as_dict=True)
    orders = pd.DataFrame([dict(row) for row in order_data]) if order_data else pd.DataFrame()

    return customers, orders


def get_segments(orders, customers):
    """
    Categorizes customers into three spending segments (Low, Medium, High Spenders) based on their purchase behavior.

    Args:
        orders (DataFrame): Order data containing purchase information.
        customers (DataFrame): Customer data.

    Returns:
        dict: A dictionary with segment names as keys and the number of customers per segment as values.
    """
    # Merge customer and order data using CustomerId as the key
    merged = customers.merge(orders, left_on='CustomerId', right_on='CustomerId')

    # Group by CustomerId and sum up total spending and amount
    grouped = merged.groupby('CustomerId')[['Price', 'Amount']].sum()

    # Apply K-Means clustering with 3 clusters to categorize customers
    kmeans = KMeans(n_clusters=3, random_state=42)
    grouped['Segment'] = kmeans.fit_predict(grouped)

    # Assign meaningful labels to the clusters
    segment_labels = {0: "Low Spenders", 1: "Medium Spenders", 2: "High Spenders"}
    segments = {segment_labels[key]: value for key, value in grouped['Segment'].value_counts().items()}

    return segments


def get_sales_trend(orders):
    """
    Creates a monthly sales trend based on the total amount of products sold.

    Args:
        orders (DataFrame): Order data containing a date column.

    Returns:
        dict: A dictionary where the key is the month (YYYY-MM) and the value is the total amount sold.
    """
    # Convert the Date column to datetime format to ensure proper handling
    orders['Date'] = pd.to_datetime(orders['Date'], errors='coerce')

    # Group by month and sum up the total amount of products sold
    sales_trend = orders.groupby(orders['Date'].dt.to_period("M"))['Amount'].sum().to_dict()

    # Convert PeriodIndex keys to string format
    sales_trend = {str(k): v for k, v in sales_trend.items()}

    return sales_trend


def get_dashboard_data():
    """
    Retrieves all relevant data for the dashboard, including:
    - Customer country distribution
    - Most popular products
    - Customer segments
    - Sales trend

    Returns:
        tuple: Contains dictionaries for country distribution, popular products, customer segments, and sales trends.
               Returns empty dictionaries if no data is available.
    """
    customers, orders = get_data()

    # Return empty dictionaries if no data is available to prevent crashes
    if customers.empty or orders.empty:
        return {}, {}, {}, {}

    # Determine the most popular products based on the number of orders
    popular_products = orders['Description'].value_counts().to_dict()

    # Get the distribution of customers by country
    country_distribution = customers['Country'].value_counts().to_dict()

    return country_distribution, popular_products, get_segments(orders, customers), get_sales_trend(orders)


def get_loyal_customers():
    """
    Identifies the top 10 most loyal customers based on:
    - Number of orders placed
    - Total amount spent

    Returns:
        tuple: Two lists of dictionaries containing the top 10 customers by order count and by total spending.
               Returns empty lists if no data is available.
    """
    customers, orders = get_data()

    # Return empty lists if no data is available to prevent crashes
    if customers.empty or orders.empty:
        return [], []

    # Calculate total number of orders per customer, sort in descending order, and select top 10
    top_customers_by_orders = (
        orders.groupby("CustomerId")
        .size()
        .reset_index(name="TotalOrders")
        .sort_values(by="TotalOrders", ascending=False)
        .head(10)
    )

    # Compute total spending per customer
    orders["TotalSpent"] = orders["Price"] * orders["Amount"]

    # Calculate total spending per customer, sort in descending order, and select top 10
    top_biggest_spenders = (
        orders.groupby("CustomerId")["TotalSpent"]
        .sum()
        .reset_index()
        .sort_values(by="TotalSpent", ascending=False)
        .head(10)
    )

    # Merge top customers with customer data to return complete information
    top_customers_by_orders = top_customers_by_orders.merge(customers, on="CustomerId", how="left").to_dict(
        orient="records")
    top_biggest_spenders = top_biggest_spenders.merge(customers, on="CustomerId", how="left").to_dict(orient="records")

    return top_customers_by_orders, top_biggest_spenders
