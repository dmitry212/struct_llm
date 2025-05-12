# Natural Language to SQL Converter

This application demonstrates the conversion of natural language queries into SQL using OpenAI's API. It leverages a database schema to generate accurate SQL queries based on user input.

## Features

- **Natural Language to SQL Conversion**: Converts user questions into SQL queries using OpenAI's gpt-3.5-turbo model.
- **Secure API Key Handling**: Uses environment variables to securely manage the OpenAI API key.
- **Database Integration**: Connects to a DuckDB database to execute generated SQL queries and return results.
- **Streamlit UI**: A user-friendly web interface that provides an interactive experience for querying the database.


## Development

- **Co-Pilot**: This app was authored with the assistance of Cursor, an AI-powered code editor, to enhance development efficiency.

## Setup

1. **Environment Variables**: Create a `.env` file in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

2. **Dependencies**: Install the required packages using `uv`:
   ```bash
   uv pip install duckdb polars requests python-dotenv openai streamlit
   ```

3. **Run the Application**: Start the Streamlit interface:
   ```bash
   streamlit run app.py
   ```

## Usage

- Open your web browser and navigate to the provided Streamlit URL (typically http://localhost:8501)
- Enter your natural language question in the text input field
- View the generated SQL query and results in the interactive interface

## Future Enhancements

### High Priority TODOs
- **Query History System**
  - Implement persistent storage of previous queries and results
  - Add a sidebar interface to browse and rerun historical queries
  - Include timestamps and success/failure status for each query

- **Dynamic Data Visualization**
  - Automatically detect appropriate visualization types based on query results
  - Implement scatter plots, bar charts, and line graphs for numerical data
  - Add interactive filtering and sorting capabilities
  - Support time-series visualizations for temporal data

- **Data Profiling and Metadata Enhancement**
  - Create comprehensive data profiles including:
    - Statistical summaries (min, max, mean, median, etc.)
    - Data type distributions
    - Value ranges and cardinality
    - Missing value analysis
  - Store profiling results in metadata for LLM context
  - Implement automatic metadata updates when data changes
  - Add data quality metrics and anomaly detection

### Additional Potential Features
- **Query Export**: Ability to export query results to various formats (CSV, Excel, etc.)
- **Custom Schema Support**: Allow users to define and use their own database schemas
- **Query Templates**: Pre-built templates for common query patterns
- **Collaboration Features**: Share and comment on queries with team members

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.

## License

This project is licensed under the MIT License. 