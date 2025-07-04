# %% [markdown]
# # Exploring DuckDB Database
# 
# This notebook provides a playground for exploring the data in our DuckDB database.

# %%
# Import required libraries
import duckdb
import polars as pl
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Set up the database connection
DB_PATH = Path("data/database.db")
conn = duckdb.connect(str(DB_PATH))

# %% [markdown]
# ## Database Schema
# 
# Let's first look at the schema information we stored in our metadata table:

# %%
# Query schema metadata
schema_info = conn.execute("""
SELECT 
    table_name,
    COALESCE(column_name, '<table_descr>') as column_name,
    description
FROM schema_metadata
ORDER BY 
    table_name,
    column_name IS NOT NULL,
    column_name
""").pl()

schema_info

# %% [markdown]
# ## Sample Data Exploration
# 
# Let's explore the data in each table:

# %%
# Customers data
customers = conn.execute("SELECT * FROM customers").pl()
print("Customers:")
customers

# %%
# Products data
products = conn.execute("SELECT * FROM products").pl()
print("Products:")
products

# %%
# Orders data
orders = conn.execute("SELECT * FROM orders").pl()
print("Orders:")
orders

# %% [markdown]
# ## Example Analysis
# 
# Let's perform some example analyses:

# %%
# Total sales by product
sales_by_product = conn.execute("""
SELECT 
    p.name as product_name,
    SUM(o.quantity) as total_quantity,
    SUM(o.quantity * p.price) as total_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY p.name
ORDER BY total_revenue DESC
""").pl()

sales_by_product

# %%
# Customer order history
customer_orders = conn.execute("""
SELECT 
    c.name as customer_name,
    p.name as product_name,
    o.quantity,
    o.status,
    o.order_date
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
ORDER BY o.order_date DESC
""").pl()

customer_orders

# %%
# Monthly sales across all products
monthly_sales = conn.execute("""
SELECT 
    DATE_TRUNC('month', order_date) as month,
    SUM(quantity * price) as total_sales
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month
""").pl()

# Create the visualization
plt.figure(figsize=(12, 6))
sns.set_style("whitegrid")
plt.plot(monthly_sales['month'], monthly_sales['total_sales'], marker='o', linewidth=2)
plt.title('Monthly Sales Across All Products', fontsize=14, pad=15)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Total Sales ($)', fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Your Turn!
# 
# Feel free to add your own queries and analyses below. Some ideas:
# 
# 1. Calculate average order value
# 2. Find most popular products
# 3. Analyze order status distribution
# 4. Add new sample data
# 
# Remember to close the connection when you're done:

# %%
# Close the database connection
conn.close() 