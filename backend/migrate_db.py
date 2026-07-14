"""
Migration script: Adds missing columns to existing complaint table.
Run this once to fix the schema mismatch without losing existing data.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'civic_system.db')

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Run app.py first to create it.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    migrations = [
        ("complaint", "photo_path",           "ALTER TABLE complaint ADD COLUMN photo_path VARCHAR(255)"),
        ("complaint", "photo_data",           "ALTER TABLE complaint ADD COLUMN photo_data BLOB"),
        ("complaint", "evidence_path",        "ALTER TABLE complaint ADD COLUMN evidence_path VARCHAR(255)"),
        ("complaint", "priority",             "ALTER TABLE complaint ADD COLUMN priority VARCHAR(10) DEFAULT 'medium'"),
        ("complaint", "verified_by",          "ALTER TABLE complaint ADD COLUMN verified_by INTEGER REFERENCES user(id)"),
        ("complaint", "assigned_to",          "ALTER TABLE complaint ADD COLUMN assigned_to INTEGER REFERENCES user(id)"),
        ("complaint", "resolved_at",          "ALTER TABLE complaint ADD COLUMN resolved_at DATETIME"),
        ("complaint", "resolution_notes",     "ALTER TABLE complaint ADD COLUMN resolution_notes TEXT"),
        ("complaint", "is_fake",              "ALTER TABLE complaint ADD COLUMN is_fake BOOLEAN DEFAULT 0"),
        ("complaint", "forwarded_department", "ALTER TABLE complaint ADD COLUMN forwarded_department VARCHAR(100)"),
        ("complaint", "resolved_photo_path",  "ALTER TABLE complaint ADD COLUMN resolved_photo_path VARCHAR(255)"),
        ("complaint", "resolved_coordinates", "ALTER TABLE complaint ADD COLUMN resolved_coordinates VARCHAR(50)"),
        ("complaint", "phone",                "ALTER TABLE complaint ADD COLUMN phone VARCHAR(15)"),
        ("complaint", "reporter_name",        "ALTER TABLE complaint ADD COLUMN reporter_name VARCHAR(100)"),
    ]

    added = []
    skipped = []

    for table, col, sql in migrations:
        if not column_exists(cursor, table, col):
            cursor.execute(sql)
            added.append(f"{table}.{col}")
        else:
            skipped.append(f"{table}.{col}")

    conn.commit()
    conn.close()

    if added:
        print(f"✅ Added columns: {', '.join(added)}")
    if skipped:
        print(f"⏭️  Already exist (skipped): {', '.join(skipped)}")
    print("Migration complete! Restart your Flask app.")

if __name__ == '__main__':
    migrate()
