
from sqlalchemy import text
from app.core.database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        version = result.fetchone()

        print("Successfully connected to PostgreSQL!")
        print("Database:", engine.url.database)
        print("PostgreSQL version:", version[0])

except Exception as e:
    print("Database connection failed!")
    print("Error:", e)
