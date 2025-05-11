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

def get_table_metadata() -> Dict:
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
    
    # Organize metadata by table
    tables = {}
    for table_name, column_name, description in metadata_rows:
        if table_name not in tables:
            tables[table_name] = {
                'description': None,
                'columns': []
            }
        if column_name is None:
            tables[table_name]['description'] = description
        else:
            tables[table_name]['columns'].append((column_name, description))
    
    return tables

def create_prompt(user_question: str, metadata: Dict) -> str:
    """Create a prompt for the LLM that includes database schema and user question."""
    # Convert metadata dict to string format
    metadata_str = "\n\n".join([
        f"Table: {table_name}\nDescription: {info['description']}\nColumns:\n" + 
        "\n".join([f"- {col_name}: {col_desc}" for col_name, col_desc in info['columns']])
        for table_name, info in metadata.items()
    ])
    
    prompt = f"""You are a SQL expert. Given the following database schema and user question, generate a SQL query.

Database Schema:
{metadata_str}

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
    return prompt

def get_sql_from_openai(prompt: str) -> str:
    """Send prompt to OpenAI API and get SQL query response."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Generate only the SQL query without any explanation or markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1  # Low temperature for more deterministic SQL generation
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Error from OpenAI API: {str(e)}")

def execute_query(sql: str) -> pl.DataFrame:
    """Execute SQL query and return results as a Polars DataFrame."""
    try:
        result = conn.execute(sql).fetchdf()
        return pl.from_pandas(result)
    except Exception as e:
        raise Exception(f"Error executing query: {str(e)}")

def process_question(user_question: str) -> tuple[str, pl.DataFrame]:
    """Process a user question and return the generated SQL and results."""
    metadata = get_table_metadata()
    prompt = create_prompt(user_question, metadata)
    sql = get_sql_from_openai(prompt)
    result = execute_query(sql)
    return sql, result

if __name__ == "__main__":
    print("\n=== Starting Natural Language to SQL Converter ===")
    metadata = get_table_metadata()
    
    print("\nWelcome to Natural Language to SQL Converter!")
    print("Type 'exit' to quit.")
    
    while True:
        user_question = input("\nEnter your question about the data: ")
        if user_question.lower() == 'exit':
            print("\nExiting...")
            break
            
        try:
            sql, result = process_question(user_question)
            print("\nGenerated SQL:")
            print(sql)
            print("\nQuery Results:")
            print(result)
            
        except Exception as e:
            print(f"\nError: {str(e)}") 