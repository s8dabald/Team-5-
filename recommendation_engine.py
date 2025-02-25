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
                sorted_items = sorted(items)
                sorted_items.remove(item)
                for r in range(1, len(sorted_items) + 1):  # Only count actual combinations
                    for combo in combinations(sorted_items, r):
                        combination_counts[", ".join(combo)] += 1

        most_common = combination_counts.most_common(top_n)

        return most_common

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    db_path = "holzbau.db"  # Adjust if the database is in another directory

    choice = input("Do you want to search for a specific item? (yes/no): ").strip().lower()
    if choice == "yes":
        item = input("Enter the item name: ").strip()
        top_combinations = get_combinations_for_item(db_path, item)
        print(f"Most common combinations with '{item}':")
    else:
        top_combinations = get_most_common_customer_combinations(db_path)
        print("Most common customer purchase combinations:")

    for item, count in top_combinations:
        print(f"{item}: {count} times")

