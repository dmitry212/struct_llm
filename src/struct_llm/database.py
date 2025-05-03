import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/database.db")

def init_db():
    """Initialize the database and create tables if they don't exist."""
    # Create data directory if it doesn't exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to the database
    conn = duckdb.connect(str(DB_PATH))
    
    # Create metadata table for schema descriptions
    conn.execute("""
    DROP TABLE IF EXISTS schema_metadata
    """)
    
    conn.execute("""
    CREATE TABLE schema_metadata (
        table_name VARCHAR NOT NULL,
        column_name VARCHAR,  -- NULL for table-level descriptions
        description VARCHAR NOT NULL,
        -- A table can have one table-level description (NULL column_name)
        -- and multiple column-level descriptions (non-NULL column_name)
        UNIQUE (table_name, column_name)
    )
    """)
    
    # Create main tables
    conn.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name VARCHAR,
        email VARCHAR,
        address VARCHAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        name VARCHAR,
        description VARCHAR,
        price DECIMAL(10, 2),
        category VARCHAR,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)
    
    # Insert schema metadata
    metadata = [
        # Table descriptions (NULL column_name)
        ('customers', None, 'Stores information about customers who place orders'),
        ('products', None, 'Stores information about products available for purchase'),
        ('orders', None, 'Stores information about customer orders and their status'),
        
        # Customer columns
        ('customers', 'customer_id', 'Unique identifier for each customer'),
        ('customers', 'name', 'Full name of the customer'),
        ('customers', 'email', 'Email address of the customer'),
        ('customers', 'address', 'Physical address of the customer'),
        ('customers', 'created_at', 'Timestamp when the customer record was created'),
        
        # Product columns
        ('products', 'product_id', 'Unique identifier for each product'),
        ('products', 'name', 'Name of the product'),
        ('products', 'description', 'Detailed description of the product'),
        ('products', 'price', 'Price of the product in USD'),
        ('products', 'category', 'Category the product belongs to'),
        ('products', 'created_at', 'Timestamp when the product record was created'),
        
        # Order columns
        ('orders', 'order_id', 'Unique identifier for each order'),
        ('orders', 'customer_id', 'Reference to the customer who placed the order'),
        ('orders', 'product_id', 'Reference to the product being ordered'),
        ('orders', 'quantity', 'Number of units ordered'),
        ('orders', 'order_date', 'Date and time when the order was placed'),
        ('orders', 'status', 'Current status of the order (e.g., Completed, Processing, Shipped)')
    ]
    
    # Clear existing metadata
    conn.execute("DELETE FROM schema_metadata")
    
    # Insert new metadata
    for table_name, column_name, description in metadata:
        conn.execute(
            "INSERT INTO schema_metadata (table_name, column_name, description) VALUES (?, ?, ?)",
            [table_name, column_name, description]
        )
    
    return conn

def insert_sample_data():
    """Insert sample data into the database."""
    conn = init_db()
    
    # Clear existing data
    conn.execute("DELETE FROM orders")
    conn.execute("DELETE FROM products")
    conn.execute("DELETE FROM customers")
    
    # Insert customers
    conn.execute("""
    INSERT INTO customers (customer_id, name, email, address) VALUES
    (1, 'John Doe', 'john@example.com', '123 Main St'),
    (2, 'Jane Smith', 'jane@example.com', '456 Oak Ave'),
    (3, 'Bob Johnson', 'bob@example.com', '789 Pine St')
    """)
    
    # Insert products
    conn.execute("""
    INSERT INTO products (product_id, name, description, price, category) VALUES
    (1, 'Laptop', 'High-performance laptop with 16GB RAM and 512GB SSD', 999.99, 'Electronics'),
    (2, 'Smartphone', 'Latest smartphone model with 5G capability', 699.99, 'Electronics'),
    (3, 'Tablet', 'Portable tablet with 10-inch display and stylus support', 399.99, 'Electronics')
    """)
    
    # Insert orders
    conn.execute("""
    INSERT INTO orders (order_id, customer_id, product_id, quantity, status) VALUES
    (1, 1, 1, 1, 'Completed'),
    (2, 2, 2, 2, 'Processing'),
    (3, 3, 3, 1, 'Shipped')
    """)
    
    conn.close()

def get_db_connection():
    """Get a connection to the database."""
    return duckdb.connect(str(DB_PATH))

def get_schema_info():
    """Get the complete schema information including descriptions."""
    conn = get_db_connection()
    result = conn.execute("""
    SELECT 
        table_name,
        COALESCE(column_name, '') as column_name,
        description
    FROM schema_metadata
    ORDER BY 
        table_name,
        -- Show table descriptions first, then column descriptions
        column_name IS NOT NULL,
        column_name
    """).fetchall()
    conn.close()
    return result 