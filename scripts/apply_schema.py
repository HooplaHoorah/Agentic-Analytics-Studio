import os
import sys
import psycopg2

def main():
    db_url = os.environ.get("DATABASE_URL")
    if len(sys.argv) > 1:
        db_url = sys.argv[1]
    
    if not db_url:
        print("Error: DATABASE_URL not set and not provided as argument")
        sys.exit(1)

    print(f"Connecting to {db_url.split('@')[1]}...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    schema_path = os.path.join("sql", "aas_schema.sql")
    if not os.path.exists(schema_path):
        # try absolute path if running from root
        schema_path = os.path.join(os.getcwd(), "sql", "aas_schema.sql")

    print(f"Reading schema from {schema_path}...")
    with open(schema_path, "r") as f:
        sql = f.read()

    print("Executing schema...")
    with conn.cursor() as cur:
        cur.execute(sql)
    
    conn.close()
    print("Schema applied successfully.")

if __name__ == "__main__":
    main()
