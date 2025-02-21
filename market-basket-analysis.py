import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from database_manager import execute_db_query

query = """
SELECT OrderId, CustomerId, Description 
FROM Order_DB
"""

# Use execute_db_query to fetch the data
data = execute_db_query(query)

# Convert the list of tuples to a list of lists (required for DataFrame creation)
data_list = [list(row) for row in data]

# Load the data into a DataFrame
df = pd.DataFrame(data_list, columns=['OrderId', 'CustomerId', 'Description'])


# Group by CustomerID and aggregate the items each customer bought
basket = df.groupby(['CustomerId', 'Description']).size().unstack(fill_value=0)

# Convert amounts to binary (1 if bought, 0 if not)
basket[basket > 0] = 1

# Applying the Apriori Algorithm to get frequent itemsets
frequent_itemsets = apriori(basket, min_support=0.3, use_colnames=True)

# Generating Association Rules with lift > 1
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)  # No need for num_itemsets here

# Filtering for rules with high confidence (e.g. greater than 0.8)
high_confidence_rules = rules[rules['confidence'] > 0.8]

# Printing the results
print("\nFrequent Itemsets:")
print(frequent_itemsets)

print("\nAssociation Rules:")
print(rules)

print("\nHigh Confidence Rules:")
print(high_confidence_rules)