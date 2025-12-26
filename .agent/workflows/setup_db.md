
# Apply Schema and Seed Data

## 1. Install Dependencies
// turbo
pip install psycopg2-binary requirements-parser

## 2. Apply Schema
```python
import psycopg2
import os

# Database connection details
db_url = "postgresql://vultradmin:AVNS_1Z4yRiK79Yz3CDRzoFH@vultr-prod-38e84cab-c270-41d6-abee-23155df25ebd-vultr-prod-795c.vultrdb.com:16751/defaultdb"
schema_file = r"c:/dev/Agentic-Analytics-Studio/instructions for Antigravity/instructions27/sql/aas_schema.sql"

print(f"Connecting to {db_url}...")
try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    print(f"Reading schema from {schema_file}...")
    with open(schema_file, 'r') as f:
        sql = f.read()
        print("Executing SQL...")
        cur.execute(sql)
        
    conn.commit()
    cur.close()
    conn.close()
    print("Schema applied successfully.")
except Exception as e:
    print(f"Error: {e}")
```

## 3. Seed Data
// turbo
python "c:/dev/Agentic-Analytics-Studio/instructions for Antigravity/instructions27/scripts/seed_demo_data.py" --database-url "postgresql://vultradmin:AVNS_1Z4yRiK79Yz3CDRzoFH@vultr-prod-38e84cab-c270-41d6-abee-23155df25ebd-vultr-prod-795c.vultrdb.com:16751/defaultdb" --rows 800

## 4. Update Requirements
Add `psycopg2-binary` to `requirements.txt` if not presenting.
