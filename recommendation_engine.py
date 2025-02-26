from collections import Counter
from itertools import combinations
from database_manager import execute_db_query


def get_all_items():
    """Fetch all unique item descriptions from the database for dropdown selection."""
    query = "SELECT DISTINCT LOWER(Description) FROM Order_DB"
    result = execute_db_query(query, as_dict=False)  # Fetch data

    if result:
        return sorted(row[0] for row in result)  # Extract and sort item descriptions
    return []  # Return an empty list if no data


def get_most_common_customer_combinations(top_n=10):
    """Retrieve the most common item combinations across all customers."""
    query = "SELECT CustomerId, LOWER(Description) FROM Order_DB"
    orders = execute_db_query(query, as_dict=False)  # Fetch order data

    if not orders:
        return []  # Return an empty list if no data

    customer_orders = {}
    for customer_id, description in orders:
        if customer_id not in customer_orders:
            customer_orders[customer_id] = set()
        customer_orders[customer_id].add(description)

    combination_counts = Counter()
    for items in customer_orders.values():
        sorted_items = sorted(items)
        for r in range(2, len(sorted_items) + 1):
            for combo in combinations(sorted_items, r):
                combination_counts[", ".join(combo)] += 1

    return combination_counts.most_common(top_n)


def get_combinations_for_item( item, top_n=10):
    """Finds the most common item combinations that include a specific item."""
    query = "SELECT CustomerId, LOWER(Description) FROM Order_DB"
    orders = execute_db_query(query, as_dict=False)  # Fetch order data

    if not orders:
        return [], 0  # Return empty data if no orders found

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
            sorted_items = sorted(items - {item})
            customer_combos = set()
            for r in range(1, len(sorted_items) + 1):
                for combo in combinations(sorted_items, r):
                    customer_combos.add(frozenset(combo))
            for combo in customer_combos:
                combination_counts[", ".join(sorted(combo))] += 1

    most_common = combination_counts.most_common(top_n)
    relative_frequencies = [(combo, count, round(count / item_occurrences, 2)) for combo, count in most_common]

    return relative_frequencies, item_occurrences
