import sqlite3
from collections import Counter
from itertools import combinations


def get_most_common_customer_combinations(db_path, top_n=5):
    """Connects to the database, retrieves customer purchase histories, and returns the most common item combinations."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch all orders grouped by CustomerId
        cursor.execute("SELECT CustomerId, Description FROM Order_DB")
        orders = cursor.fetchall()

        # Group orders by customer
        customer_orders = {}
        for customer_id, description in orders:
            description = description.lower()  # Normalize case
            if customer_id not in customer_orders:
                customer_orders[customer_id] = set()
            customer_orders[customer_id].add(description)

        # Count item combinations across all customers
        combination_counts = Counter()
        for items in customer_orders.values():
            sorted_items = sorted(items)
            for r in range(2, len(sorted_items) + 1):  # Only count actual combinations
                for combo in combinations(sorted_items, r):
                    combination_counts[", ".join(combo)] += 1

        most_common = combination_counts.most_common(top_n)

        return most_common

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        if conn:
            conn.close()


def get_combinations_for_item(db_path, item, top_n=5):
    """Finds the most common item combinations that include a specific item."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch all orders grouped by CustomerId
        cursor.execute("SELECT CustomerId, Description FROM Order_DB")
        orders = cursor.fetchall()

        # Group orders by customer
        customer_orders = {}
        for customer_id, description in orders:
            description = description.lower()  # Normalize case
            if customer_id not in customer_orders:
                customer_orders[customer_id] = set()
            customer_orders[customer_id].add(description)

        # Normalize input item case
        item = item.lower()

        # Count item combinations that include the specific item
        combination_counts = Counter()
        for items in customer_orders.values():
            if item in items:
                # Remove the searched item to only count combinations with other items
                sorted_items = sorted(items)
                sorted_items.remove(item)

                # Now find all combinations of the remaining items for this customer
                customer_combos = set()  # Ensure combinations are unique for this customer
                for r in range(1, len(sorted_items) + 1):  # Generate combinations
                    for combo in combinations(sorted_items, r):
                        customer_combos.add(frozenset(combo))  # Use frozenset to prevent duplicates

                # Add unique combinations for the customer to the global counter
                for combo in customer_combos:
                    combination_counts[", ".join(sorted(combo))] += 1

        # Get most common combinations
        most_common = combination_counts.most_common(top_n)

        return most_common

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        if conn:
            conn.close()
