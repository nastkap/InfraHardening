import psycopg2
import os

# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "infrahardening"
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_PORT = "5432"

def load_schema():
    """Load database schema from SQL file"""
    try:
        # First connect to default postgres database to create the target database
        conn = psycopg2.connect(
            host=DB_HOST,
            database="postgres",  # Connect to default database first
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if database exists, create if not
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database '{DB_NAME}' created successfully!")
        else:
            print(f"Database '{DB_NAME}' already exists.")
        
        cur.close()
        conn.close()
        
        # Now connect to the target database
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Execute schema
        cur = conn.cursor()
        cur.execute(schema_sql)
        conn.commit()
        
        print("Schema loaded successfully!")
        print(f"Connected to database: {DB_NAME}")
        print(f"Host: {DB_HOST}:{DB_PORT}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error loading schema: {e}")
        raise

if __name__ == "__main__":
    load_schema()
