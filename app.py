import streamlit as st
from nl_to_sql import get_table_metadata, process_question
from datetime import datetime
import json
import os

# Initialize session state for query history if it doesn't exist
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Function to save query history to a file
def save_query_history():
    with open('query_history.json', 'w') as f:
        json.dump(st.session_state.query_history, f)

# Function to load query history from file
def load_query_history():
    if os.path.exists('query_history.json'):
        with open('query_history.json', 'r') as f:
            return json.load(f)
    return []

# Load existing query history
if not st.session_state.query_history:
    st.session_state.query_history = load_query_history()

# Streamlit app
st.title("Natural Language to SQL Converter")

st.write("This application converts natural language queries into SQL using OpenAI's API. It leverages a database schema to generate accurate SQL queries based on user input.")

# Sidebar for query history
with st.sidebar:
    st.header("Query History")
    if st.session_state.query_history:
        for idx, query in enumerate(reversed(st.session_state.query_history)):
            with st.expander(f"{query['timestamp']} - {query['question'][:50]}..."):
                st.write(f"**Question:** {query['question']}")
                st.write(f"**SQL:** ```sql\n{query['sql']}\n```")
                st.write(f"**Status:** {'✅ Success' if query['success'] else '❌ Failed'}")
                if query['error']:
                    st.error(query['error'])
                if st.button("Rerun Query", key=f"rerun_{idx}"):
                    st.session_state.rerun_query = query['question']
    else:
        st.write("No query history yet.")

# Chat interface
user_question = st.text_input("Ask a question about your data:", 
                            placeholder="e.g., What is the total premium amount for all active policies?",
                            value=st.session_state.get('rerun_query', ''))

if user_question:
    try:
        # Process the question and get results
        sql, result = process_question(user_question)
        
        # Display SQL
        st.subheader("Generated SQL")
        st.code(sql, language="sql")
        
        # Execute and display results
        st.subheader("Query Results")
        st.dataframe(result)
        
        # Add to query history
        query_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'question': user_question,
            'sql': sql,
            'success': True,
            'error': None
        }
        st.session_state.query_history.append(query_entry)
        save_query_history()
        
    except Exception as e:
        error_msg = str(e)
        st.error(error_msg)
        
        # Add failed query to history
        query_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'question': user_question,
            'sql': None,
            'success': False,
            'error': error_msg
        }
        st.session_state.query_history.append(query_entry)
        save_query_history()

# Clear rerun query state
if 'rerun_query' in st.session_state:
    del st.session_state.rerun_query

# Database Schema section
st.header("Database Schema")
metadata = get_table_metadata()

# Create three columns for the tables
col1, col2, col3 = st.columns(3)

# Display tables in columns
for i, (table_name, info) in enumerate(metadata.items()):
    # Assign to appropriate column
    col = [col1, col2, col3][i]
    
    with col:
        with st.expander(f"📊 {table_name}", expanded=False):  # Start collapsed
            if info['description']:
                st.markdown(f"*{info['description']}*")
            
            # Create a table for columns
            if info['columns']:
                st.markdown("**Columns:**")
                for col_name, col_desc in info['columns']:
                    st.markdown(f"- **{col_name}**: {col_desc}") 