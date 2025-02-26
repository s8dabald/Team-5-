import sqlite3
from collections import Counter
from itertools import combinations


def get_all_items(db_path):
    """Fetch all unique item descriptions from the database for dropdown selection."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT LOWER(Description) FROM Order_DB")
        items = [row[0] for row in cursor.fetchall()]
        return sorted(items)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_most_common_customer_combinations(db_path, top_n=10):
    """Retrieve the most common item combinations across all customers."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT CustomerId, LOWER(Description) FROM Order_DB")
        orders = cursor.fetchall()

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
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_combinations_for_item(db_path, item, top_n=10):
    """Finds the most common item combinations that include a specific item."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT CustomerId, LOWER(Description) FROM Order_DB")
        orders = cursor.fetchall()

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
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return [], 0

def get_recommendations_for_cart(db_path, items, top_n=10):
    """
    Für den gegebenen Warenkorb (Liste von Items) wird ermittelt, welche zusätzlichen Items
    von Kunden, die alle Items im Warenkorb bestellt haben, häufig bestellt wurden.
    Gibt eine Liste von Tupeln (Item, Count) und die Anzahl der Kunden zurück.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT CustomerId, LOWER(Description) FROM Order_DB")
        orders = cursor.fetchall()

        customer_orders = {}
        for customer_id, description in orders:
            if customer_id not in customer_orders:
                customer_orders[customer_id] = set()
            customer_orders[customer_id].add(description)

        recommendation_counter = Counter()
        cart_customers = 0
        for order_set in customer_orders.values():
            # Prüfe, ob der Warenkorb (alle Items) in den Bestellungen dieses Kunden enthalten ist.
            if set(items).issubset(order_set):
                cart_customers += 1
                additional_items = order_set - set(items)
                for item in additional_items:
                    recommendation_counter[item] += 1

        recommendations = recommendation_counter.most_common(top_n)
        return recommendations, cart_customers
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return [], 0
    finally:
        if conn:
            conn.close()
