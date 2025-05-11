# Natural Language to SQL Converter

This application demonstrates the conversion of natural language queries into SQL using OpenAI's API. It leverages a database schema to generate accurate SQL queries based on user input.

## Features

- **Natural Language to SQL Conversion**: Converts user questions into SQL queries using OpenAI's gpt-3.5-turbo model.
- **Secure API Key Handling**: Uses environment variables to securely manage the OpenAI API key.
- **Database Integration**: Connects to a DuckDB database to execute generated SQL queries and return results.
- **Upcoming Streamlit UI**: A user-friendly interface is being developed to enhance the user experience.

## Development

- **Co-Pilot**: This app was authored with the assistance of Cursor, an AI-powered code editor, to enhance development efficiency.

## Setup

1. **Environment Variables**: Create a `.env` file in the project root with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

2. **Dependencies**: Install the required packages using `uv`:
   ```bash
   uv pip install duckdb polars requests python-dotenv openai
   ```

3. **Run the Application**: Execute the script to start the converter:
   ```bash
   python nl_to_sql.py
   ```

## Usage

- Enter your natural language question when prompted.
- The application will generate and execute the corresponding SQL query, displaying the results.

## Future Enhancements

- **Streamlit UI**: A web-based interface is under development to provide a more interactive experience.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.

## License

This project is licensed under the MIT License. 