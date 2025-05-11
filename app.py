import streamlit as st
import duckdb
from pathlib import Path

# Set up the database connection
DB_PATH = Path("data/database.db")
conn = duckdb.connect(str(DB_PATH))

def get_table_metadata():
    """Get metadata about all tables and their columns from DuckDB using our schema_metadata table."""
    metadata_query = """
    SELECT 
        table_name,
        column_name,
        description
    FROM schema_metadata
    ORDER BY 
        table_name,
        column_name IS NOT NULL,
        column_name
    """
    metadata_rows = conn.execute(metadata_query).fetchall()
    
    # Format metadata into a readable string
    current_table = None
    metadata_parts = []
    current_table_info = []
    
    for table_name, column_name, description in metadata_rows:
        if current_table != table_name:
            if current_table_info:
                metadata_parts.append('\n'.join(current_table_info))
            current_table = table_name
            current_table_info = [f"Table: {table_name}"]
            if column_name is None:
                current_table_info.append(f"Description: {description}")
                current_table_info.append("Columns:")
        elif column_name is not None:
            current_table_info.append(f"- {column_name}: {description}")
    
    if current_table_info:
        metadata_parts.append('\n'.join(current_table_info))
    
    return '\n\n'.join(metadata_parts)

# Streamlit app
st.title("Natural Language to SQL Converter")

st.write("This application converts natural language queries into SQL using OpenAI's API. It leverages a database schema to generate accurate SQL queries based on user input.")

st.header("Database Schema")
metadata = get_table_metadata()
st.text(metadata) 