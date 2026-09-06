from pathlib import Path
import sqlite3


ROOT_DIR = Path(__file__).resolve().parent.parent

DB_PATH = ROOT_DIR / "restaurant.db"
SCHEMA_PATH = ROOT_DIR / "schema.sql"
SEED_PATH = ROOT_DIR / "seed.sql"


def reset_database():
    # Remove the existing database
    if DB_PATH.exists():
        DB_PATH.unlink()

    # Create a fresh database
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        # Create tables
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        connection.executescript(schema_sql)

        # Insert seed data
        seed_sql = SEED_PATH.read_text(encoding="utf-8")
        connection.executescript(seed_sql)

        connection.commit()

    finally:
        connection.close()

    print("Database reset: PASS")


if __name__ == "__main__":
    reset_database()
