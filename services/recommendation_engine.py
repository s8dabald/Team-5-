import sqlite3
from collections import Counter
from itertools import combinations
from database_manager import execute_db_query  # Ensure this import matches the file where execute_db_query is defined

def get_all_items(db_path):
    """
    Fetches all unique item descriptions from the database.
    Used to populate the dropdown menu for product selection.

    - db_path: Path to the SQLite database file.

    Returns:
        A sorted list of unique product descriptions in lowercase.
    """
    query = "SELECT DISTINCT LOWER(Description) FROM Order_DB"
    results = execute_db_query(query)
    return sorted([row[0] for row in results]) if results else []

def get_most_common_customer_combinations(db_path, top_n=10):
    """
    Retrieves the most frequently occurring item combinations across all customers.

    - db_path: Path to the SQLite database file.
    - top_n: The number of most common combinations to return.

    Returns:
        A list of tuples (combination, count), where:
        - combination is a comma-separated string of items,
        - count represents how often the combination appeared.
    """
    query = "SELECT CustomerId, LOWER(Description) FROM Order_DB"
    orders = execute_db_query(query)

    if not orders:
        return []

    customer_orders = {}
    for customer_id, description in orders:
        if customer_id not in customer_orders:
            customer_orders[customer_id] = set()
        customer_orders[customer_id].add(description)

    combination_counts = Counter()
    for items in customer_orders.values():
        sorted_items = sorted(items)
        for r in range(2, len(sorted_items) + 1):  # Generate combinations of at least 2 items
            for combo in combinations(sorted_items, r):
                combination_counts[", ".join(combo)] += 1

    return combination_counts.most_common(top_n)

def get_combinations_for_item(db_path, item, top_n=10):
    """
    Finds the most frequently occurring item combinations that include a given item.

    - db_path: Path to the SQLite database file.
    - item: The product name to search for (case insensitive).
    - top_n: The number of top combinations to return.

    Returns:
        - A list of tuples (combination, count, relative_frequency), where:
          - combination is a comma-separated string of items,
          - count represents how often the combination appeared,
          - relative_frequency is the percentage of times this combination appeared with the selected item.
        - The total number of orders containing the selected item.
    """
    query = "SELECT CustomerId, LOWER(Description) FROM Order_DB"
    orders = execute_db_query(query)

    if not orders:
        return [], 0

    customer_orders = {}
    for customer_id, description in orders:
        if customer_id not in customer_orders:
            customer_orders[customer_id] = set()
        customer_orders[customer_id].add(description)

    item = item.lower()
    combination_counts = Counter()
    item_occurrences = 0

    for items in customer_orders.values():
        if item in items:
            item_occurrences += 1
            sorted_items = sorted(items - {item})  # Exclude the searched item itself
            customer_combos = set()
            for r in range(1, len(sorted_items) + 1):  # Generate all subsets of the remaining items
                for combo in combinations(sorted_items, r):
                    customer_combos.add(frozenset(combo))
            for combo in customer_combos:
                combination_counts[", ".join(sorted(combo))] += 1

    most_common = combination_counts.most_common(top_n)
    relative_frequencies = [(combo, count, round(count / item_occurrences, 2)) for combo, count in most_common]

    return relative_frequencies, item_occurrences

def get_recommendations_for_cart(db_path, items, top_n=10):
    """
    Identifies additional items frequently purchased by customers who ordered all items in a given shopping cart.

    - db_path: Path to the SQLite database file.
    - items: A list of product names representing the shopping cart.
    - top_n: The number of recommendations to return.

    Returns:
        - A list of tuples (recommended_item, count), where:
          - recommended_item is an item frequently bought with the cart items,
          - count represents how often it appeared in relevant orders.
        - The number of customers whose orders contained all the cart items.
    """
    query = "SELECT CustomerId, LOWER(Description) FROM Order_DB"
    orders = execute_db_query(query)

    if not orders:
        return [], 0

    customer_orders = {}
    for customer_id, description in orders:
        if customer_id not in customer_orders:
            customer_orders[customer_id] = set()
        customer_orders[customer_id].add(description)

    recommendation_counter = Counter()
    cart_customers = 0

    for order_set in customer_orders.values():
        # Check if the customer's order contains all cart items
        if set(items).issubset(order_set):
            cart_customers += 1
            additional_items = order_set - set(items)  # Find items not in the cart
            for item in additional_items:
                recommendation_counter[item] += 1

    recommendations = recommendation_counter.most_common(top_n)
    return recommendations, cart_customers
