import sqlite3
import os

db_paths = [
    os.path.join(os.path.dirname(__file__), "dsarena.db"),
    os.path.join(os.path.dirname(__file__), "..", "dsarena.db")
]

for db_path in db_paths:
    if not os.path.exists(db_path):
        continue
    print(f"Checking database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing columns of daily_activities
    cursor.execute("PRAGMA table_info(daily_activities)")
    columns = [col[1] for col in cursor.fetchall()]
    print("Existing columns in daily_activities:", columns)
    
    if "lessons_completed" not in columns:
        print("Adding lessons_completed column...")
        cursor.execute("ALTER TABLE daily_activities ADD COLUMN lessons_completed INTEGER DEFAULT 0")
        
    if "topics_completed" not in columns:
        print("Adding topics_completed column...")
        cursor.execute("ALTER TABLE daily_activities ADD COLUMN topics_completed INTEGER DEFAULT 0")

    if "streak_active" not in columns:
        print("Adding streak_active column...")
        cursor.execute("ALTER TABLE daily_activities ADD COLUMN streak_active BOOLEAN DEFAULT 1")
        
    conn.commit()
    conn.close()
    print("Migration check complete for:", db_path)
