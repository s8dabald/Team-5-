import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from database_manager import execute_db_query

def get_top_combinations(execute_db_query):
    query = "SELECT OrderId, Description FROM Order_DB"
    df = pd.DataFrame(execute_db_query(query), columns=['OrderId', 'Description'])
    
    if df.empty:
        return {"error": "No order data available"}, 500
    
    basket = df.groupby(['OrderId', 'Description']).size().unstack(fill_value=0)
    basket[basket > 0] = 1
    
    frequent_itemsets = apriori(basket, min_support=0.3, use_colnames=True)
    if frequent_itemsets.empty:
        return {"error": "Not enough frequent itemsets"}, 500
    
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
    if rules.empty:
        return {"error": "No strong associations found"}, 500
    
    rules['antecedents'] = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
    rules['consequents'] = rules['consequents'].apply(lambda x: ', '.join(list(x)))
    rules['items'] = rules['antecedents'] + ' + ' + rules['consequents']
    rules['percentage'] = (rules['support'] * 100).round(2)
    
    return {"top_combinations": rules[['items', 'percentage']].to_dict(orient='records')}

def get_all_items(execute_db_query):
    query = "SELECT DISTINCT Description FROM Order_DB"
    items = [row[0] for row in execute_db_query(query)]
    return items

def get_item_combinations(execute_db_query, item):
    query = "SELECT OrderId, Description FROM Order_DB"
    df = pd.DataFrame(execute_db_query(query), columns=['OrderId', 'Description'])
    
    if df.empty:
        return {"error": "No order data available"}, 500
    
    basket = df.groupby(['OrderId', 'Description']).size().unstack(fill_value=0)
    basket[basket > 0] = 1
    
    frequent_itemsets = apriori(basket, min_support=0.3, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
    if rules.empty:
        return {"error": "No strong associations found for this item"}, 500
    
    item_rules = rules[rules['antecedents'].apply(lambda x: item in x)]
    item_rules['consequents'] = item_rules['consequents'].apply(lambda x: ', '.join(list(x)))
    item_rules['percentage'] = (item_rules['support'] * 100).round(2)
    
    return item_rules[['consequents', 'percentage']].head(5).rename(columns={'consequents': 'combination'}).to_dict(orient='records')
