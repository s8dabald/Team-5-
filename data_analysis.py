import pandas as pd
from sklearn.cluster import KMeans
from database_manager import execute_db_query
def get_data():
    customer_data = execute_db_query("SELECT * FROM Customer_DB", as_dict=True)
    customers = pd.DataFrame([dict(row) for row in customer_data]) if customer_data else pd.DataFrame()

    order_data = execute_db_query("SELECT * FROM Order_DB", as_dict=True)
    orders = pd.DataFrame([dict(row) for row in order_data]) if order_data else pd.DataFrame()
    return customers, orders
def get_segments(orders, customers):
    merged = customers.merge(orders, left_on='CustomerId', right_on='CustomerId')

    grouped = merged.groupby('CustomerId')[['Price', 'Amount']].sum()

    kmeans = KMeans(n_clusters=3, random_state=42)
    grouped['Segment'] = kmeans.fit_predict(grouped)

    segment_labels = {0: "Low Spenders", 1: "Medium Spenders", 2: "High Spenders"}
    segments = {segment_labels[key]: value for key, value in grouped['Segment'].value_counts().items()}
    return segments

def get_sales_trend(orders):
    orders['Date'] = pd.to_datetime(orders['Date'], errors='coerce')
    sales_trend = orders.groupby(orders['Date'].dt.to_period("M"))['Amount'].sum().to_dict()
    sales_trend = {str(k): v for k, v in sales_trend.items()}
    return sales_trend

def get_dashboard_data():
    customers, orders= get_data()

    if customers.empty or orders.empty:
        return {}, {}, {}, {}
    popular_products = orders['Description'].value_counts().to_dict()
    country_distribution = customers['Country'].value_counts().to_dict()
    return country_distribution,popular_products, get_segments(orders, customers), get_sales_trend(orders)

def get_loyal_customers():
    """Ermittelt die Top 10 Kunden nach Bestellhäufigkeit und Ausgaben"""
    customers, orders = get_data()

    if customers.empty or orders.empty:
        return [], []

    # Kunden mit den meisten Bestellungen
    top_customers_by_orders = (
        orders.groupby("CustomerId")
        .size()
        .reset_index(name="TotalOrders")
        .sort_values(by="TotalOrders", ascending=False)
        .head(10)
    )

    # Berechnung des gesamten ausgegebenen Betrags (Price * Amount)
    orders["TotalSpent"] = orders["Price"] * orders["Amount"]

    # Top 10 größte Spender
    top_biggest_spenders = (
        orders.groupby("CustomerId")["TotalSpent"]
        .sum()
        .reset_index()
        .sort_values(by="TotalSpent", ascending=False)
        .head(10)
    )

    # Merge mit Kundendaten für vollständige Informationen
    top_customers_by_orders = top_customers_by_orders.merge(customers, on="CustomerId", how="left").to_dict(orient="records")
    top_biggest_spenders = top_biggest_spenders.merge(customers, on="CustomerId", how="left").to_dict(orient="records")

    return top_customers_by_orders, top_biggest_spenders
