from struct_llm.database import init_db, insert_sample_data

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Inserting sample data...")
    insert_sample_data()
    print("Database setup complete!") 