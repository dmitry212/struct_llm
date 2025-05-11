import streamlit as st
from nl_to_sql import get_table_metadata, process_question

# Streamlit app
st.title("Natural Language to SQL Converter")

st.write("This application converts natural language queries into SQL using OpenAI's API. It leverages a database schema to generate accurate SQL queries based on user input.")

# Chat interface
user_question = st.text_input("Ask a question about your data:", placeholder="e.g., What is the total premium amount for all active policies?")

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
        
    except Exception as e:
        st.error(str(e))

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