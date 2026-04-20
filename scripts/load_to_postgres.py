import pandas as pd
from sqlalchemy import create_engine

DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "verkeersongevallen"

print("Data inladen...")
df = pd.read_csv("data/processed/ongevallen_cleaned.csv", low_memory=False)
print(f"  {len(df):,} rijen geladen")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

print("Uploaden naar PostgreSQL...")
df.to_sql(
    name="ongevallen",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=5000,
    method="multi"
)

print(f"Klaar! Tabel 'ongevallen' aangemaakt met {len(df):,} rijen.")

with engine.connect() as conn:
    result = conn.execute(__import__("sqlalchemy").text("SELECT COUNT(*) FROM ongevallen"))
    print(f"Verificatie: {result.scalar():,} rijen in database")
