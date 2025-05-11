import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import duckdb
import polars as pl
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Set up OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
client = OpenAI(api_key=api_key)

# Set up the database connection
DB_PATH = Path("data/database.db")
conn = duckdb.connect(str(DB_PATH))

def get_table_metadata() -> str:
    """Get metadata about all tables and their columns from DuckDB using our schema_metadata table."""
    print("\n=== Fetching Database Metadata ===")

    # Get metadata for all tables and columns
    metadata_query = """
    SELECT 
        table_name,
        column_name,
        description
    FROM schema_metadata
    ORDER BY 
        table_name,
        -- Show table descriptions first, then column descriptions
        column_name IS NOT NULL,
        column_name
    """
    print("Executing metadata query...")
    metadata_rows = conn.execute(metadata_query).fetchall()
    print(f"Retrieved {len(metadata_rows)} metadata rows")

    # Format metadata into a readable string
    current_table = None
    metadata_parts = []
    current_table_info = []

    for table_name, column_name, description in metadata_rows:
        if current_table != table_name:
            # Start a new table section
            if current_table_info:
                metadata_parts.append('\n'.join(current_table_info))
            current_table = table_name
            current_table_info = [f"Table: {table_name}"]
            # Add table description if this is a table-level metadata
            if column_name is None:
                current_table_info.append(f"Description: {description}")
                current_table_info.append("Columns:")
        elif column_name is not None:  # Skip table-level descriptions here
            # Add column information
            current_table_info.append(f"- {column_name}: {description}")

    # Add the last table's information
    if current_table_info:
        metadata_parts.append('\n'.join(current_table_info))

    print(f"Metadata returned {metadata_parts}")
    return '\n\n'.join(metadata_parts)

def create_prompt(user_question: str, metadata: str) -> str:
    """Create a prompt for the LLM that includes database schema and user question."""
    print("\n=== Creating Prompt ===")
    print(f"User Question: {user_question}")
    prompt = f"""You are a SQL expert. Given the following database schema and user question, generate a SQL query.

Database Schema:
{metadata}

User Question: {user_question}

Generate a SQL query that answers the user's question. Return ONLY the raw SQL query without any explanation, markdown formatting, or code blocks.
The query should be compatible with DuckDB SQL dialect.
DO NOT include any markdown formatting like ```sql or ```.

IMPORTANT SQL RULES:
1. ALWAYS prefix column names with their table name (e.g., use 'orders.product_id' instead of just 'product_id')
2. Use table aliases when joining tables (e.g., 'FROM orders o JOIN products p')
3. When referencing columns in SELECT, WHERE, or JOIN conditions, always use the full table reference
4. If a column exists in multiple tables, you MUST specify which table it comes from

Example of correct column references:
- orders.product_id (correct)
- products.product_id (correct)
- product_id (incorrect - ambiguous)
"""
    print(f"Generated prompt length: {len(prompt)} characters")
    return prompt

def get_sql_from_openai(prompt: str) -> str:
    """Send prompt to OpenAI API and get SQL query response."""
    print("\n=== Sending to OpenAI API ===")
    print(f"Prompt: {(prompt)}")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Generate only the SQL query without any explanation or markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1  # Low temperature for more deterministic SQL generation
        )
        sql = response.choices[0].message.content.strip()
        print("Successfully received SQL query:")
        print(sql)
        return sql
    except Exception as e:
        print(f"Error from OpenAI API: {str(e)}")
        raise Exception(f"Error from OpenAI API: {str(e)}")

def execute_query(sql: str) -> pl.DataFrame:
    """Execute SQL query and return results as a Polars DataFrame."""
    print("\n=== Executing Query ===")
    print(f"SQL Query: {sql}")
    result = conn.execute(sql).fetchdf()
    print(f"Query returned {len(result)} rows")
    print(f"Columns: {result.columns.tolist()}")
    return pl.from_pandas(result)

def main():
    print("\n=== Starting Natural Language to SQL Converter ===")
    # Get database metadata
    metadata = get_table_metadata()

    print("\nWelcome to Natural Language to SQL Converter!")
    print("Type 'exit' to quit.")

    while True:
        # Get user question
        user_question = input("\nEnter your question about the data: ")
        if user_question.lower() == 'exit':
            print("\nExiting...")
            break

        try:
            # Generate SQL from question
            prompt = create_prompt(user_question, metadata)
            sql = get_sql_from_openai(prompt)

            # Execute query and show results
            result = execute_query(sql)
            print("\nQuery Results:")
            print(result)

        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main() 