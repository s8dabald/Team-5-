import sqlite3
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# Connecting to SQLite database
db_path = 'holzbau.db'
conn = sqlite3.connect(db_path)

# Querying necessary data from the database
query = """
SELECT OrderId, CustomerId, Description 
FROM Order_DB
"""
# Load the data into a DataFrame
df = pd.read_sql(query, conn)

# Group by CustomerID and aggregate the items each customer bought
# We will mark 1 if the customer bought the specific item, 0 if not.

# Creating a basket for each customer, where each item bought by the customer is marked as 1
basket = df.groupby(['CustomerId', 'Description']).size().unstack(fill_value=0)

# Convert amounts to binary (1 if bought, 0 if not)
basket[basket > 0] = 1

# Applying the Apriori Algorithm to get frequent itemsets
frequent_itemsets = apriori(basket, min_support=0.3, use_colnames=True)

# Generating Association Rules with lift > 1
# Including the 'num_itemsets' argument to resolve the error
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1, num_itemsets=2)

# Filtering for rules with high confidence (e.g. greater than 0.8)
high_confidence_rules = rules[rules['confidence'] > 0.8]

# Printing the results
print("\nFrequent Itemsets:")
print(frequent_itemsets)

print("\nAssociation Rules:")
print(rules)

print("\nHigh Confidence Rules:")
print(high_confidence_rules)


# Closing the database connection
conn.close()
