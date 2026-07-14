from app.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT count(*) FROM profiles"))
    print("profiles count:", result.scalar())