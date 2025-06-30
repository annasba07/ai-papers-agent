import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print(f"DEBUG: DATABASE_URL read from .env: {DATABASE_URL}")

if not DATABASE_URL:
    print("DATABASE_URL environment variable not set.")
else:
    print(f"Attempting to connect to: {DATABASE_URL}")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Successfully connected to the database!")
            # Optional: Try a simple query
            result = connection.execute("SELECT 1").scalar()
            print(f"Query result: {result}")
        engine.dispose()
    except OperationalError as e:
        print(f"Failed to connect to the database. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
