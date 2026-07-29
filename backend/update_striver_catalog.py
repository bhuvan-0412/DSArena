"""
update_striver_catalog.py
-------------------------
Updates app/services/striver_catalog.py to include all 316 Striver A2Z playlist videos.
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dsarena.db")
CATALOG_PATH = os.path.join(BASE_DIR, "app", "services", "striver_catalog.py")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT n.id, n.title, n.youtube_url, n.youtube_video_id, n.thumbnail_url, p.title as section_title
    FROM roadmap_nodes n
    LEFT JOIN roadmap_nodes p ON n.parent_id = p.id
    WHERE n.youtube_video_id IS NOT NULL
""")
rows = cursor.fetchall()
conn.close()

catalog_entries = []
for r in rows:
    entry = {
        "id": r["id"],
        "title": r["title"],
        "aliases": [r["title"]],
        "youtube_url": r["youtube_url"],
        "video_id": r["youtube_video_id"],
        "thumbnail_url": r["thumbnail_url"],
        "estimated_duration": 15,
        "section": r["section_title"] or "General",
        "source": "TakeUForward"
    }
    catalog_entries.append(entry)

file_content = f'"""\nOfficial Striver (TakeUForward) A2Z DSA Sheet Video Catalog.\nServes as the primary source of truth for matching roadmap nodes with official video lessons.\n"""\n\nfrom typing import Dict, Any, List\n\nSTRIVER_A2Z_CATALOG: List[Dict[str, Any]] = {repr(catalog_entries)}\n'

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    f.write(file_content)

print(f"Updated striver_catalog.py with {len(catalog_entries)} entries.")
