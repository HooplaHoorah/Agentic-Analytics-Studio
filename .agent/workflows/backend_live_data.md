
# Backend Updates for Live Data

## 1. Update requirements.txt
Add `psycopg2-binary` and `PyJWT` to `requirements.txt`.

## 2. Create aas/db.py
Create `aas/db.py` with the helper function `get_conn`.

```python
import os
import psycopg2

def get_conn():
    db = os.getenv("DATABASE_URL")
    if not db:
        raise RuntimeError("DATABASE_URL not set")
    conn = psycopg2.connect(db)
    conn.autocommit = True
    return conn
```

## 3. Identify and Modify Endpoints
- Locate `POST /run/pipeline`.
- In the handler, after generating recommendations, insert `run` and `actions` into Postgres.
- Locate `POST /approve`.
- Update action status and insert execution record.
- Add `GET /context/actions`.
- Add `GET /tableau/jwt` (placeholder or functional if secrets available).

## 4. Environment Variables
Ensure `DATABASE_URL` is set in the environment (or .env for local dev).
