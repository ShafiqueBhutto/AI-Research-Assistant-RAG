from sqlalchemy import text

from app.db.database import engine


try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("PostgreSQL connection successful!")
        print("Result:", result.scalar())

except Exception as e:
    print("PostgreSQL connection failed!")
    print("Error:", e)