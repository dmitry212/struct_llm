import duckdb
import polars as pl
from pathlib import Path

# Set up the database connection
DB_PATH = Path("data/database.db")
conn = duckdb.connect(str(DB_PATH))

# Drop existing tables in the correct order (child tables first)
conn.execute("DROP TABLE IF EXISTS orders")
conn.execute("DROP TABLE IF EXISTS customers")
conn.execute("DROP TABLE IF EXISTS products")
conn.execute("DROP TABLE IF EXISTS schema_metadata")

# Create tables with proper schema and constraints
conn.execute("""
CREATE TABLE products AS
SELECT * FROM read_csv_auto('data/products.csv')
""")

conn.execute("""
CREATE TABLE customers AS
SELECT * FROM read_csv_auto('data/customers.csv')
""")

# Create orders table with foreign key references
conn.execute("""
CREATE TABLE orders AS
SELECT 
    o.*,
    c.customer_id as _check_customer,
    p.product_id as _check_product
FROM read_csv_auto('data/orders.csv') o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
""")

# Create schema metadata table
conn.execute("""
CREATE TABLE schema_metadata (
    table_name VARCHAR,
    column_name VARCHAR,
    description VARCHAR
)
""")

# Insert schema metadata
conn.execute("""
INSERT INTO schema_metadata VALUES
    ('products', NULL, 'Life insurance products available for purchase'),
    ('products', 'product_id', 'Unique identifier for the product'),
    ('products', 'product_name', 'Name of the insurance product'),
    ('products', 'coverage_type', 'Type of life insurance coverage'),
    ('products', 'term_length_years', 'Length of term for term life insurance (NULL for permanent policies)'),
    ('products', 'base_premium', 'Base monthly premium amount'),
    ('products', 'max_coverage_amount', 'Maximum coverage amount available'),
    
    ('customers', NULL, 'Customer information'),
    ('customers', 'customer_id', 'Unique identifier for the customer'),
    ('customers', 'first_name', 'Customer first name'),
    ('customers', 'last_name', 'Customer last name'),
    ('customers', 'email', 'Customer email address'),
    ('customers', 'phone', 'Customer phone number'),
    ('customers', 'address', 'Customer street address'),
    ('customers', 'city', 'Customer city'),
    ('customers', 'state', 'Customer state'),
    ('customers', 'zip_code', 'Customer zip code'),
    ('customers', 'date_of_birth', 'Customer date of birth'),
    ('customers', 'age', 'Customer age in years'),
    
    ('orders', NULL, 'Insurance policy orders'),
    ('orders', 'order_id', 'Unique identifier for the order'),
    ('orders', 'customer_id', 'ID of the customer who placed the order'),
    ('orders', 'product_id', 'ID of the product ordered'),
    ('orders', 'order_date', 'Date the order was placed'),
    ('orders', 'premium_amount', 'Monthly premium amount for the policy'),
    ('orders', 'coverage_amount', 'Coverage amount for the policy'),
    ('orders', 'payment_status', 'Status of the payment (Paid, Pending, Failed)'),
    ('orders', 'policy_status', 'Status of the policy (Active, Pending, Cancelled)')
""")

# Verify the data was loaded correctly
print("Products table:")
print(conn.execute("SELECT * FROM products LIMIT 5").pl())

print("\nCustomers table:")
print(conn.execute("SELECT * FROM customers LIMIT 5").pl())

print("\nOrders table:")
print(conn.execute("SELECT * FROM orders LIMIT 5").pl())

# Close the connection
conn.close()

print("\nDatabase updated successfully!") 