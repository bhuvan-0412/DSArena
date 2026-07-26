import sqlite3

conn = sqlite3.connect("backend/dsarena.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. Check Ordering Issues
cursor.execute("SELECT * FROM roadmap_nodes ORDER BY parent_id, order_index")
nodes = [dict(r) for r in cursor.fetchall()]

children_by_parent = {}
for n in nodes:
    children_by_parent.setdefault(n['parent_id'], []).append(n)

fixed_orders = 0
for pid, children in children_by_parent.items():
    # Fix order_index to be 1-based sequential integers
    for idx, c in enumerate(children, start=1):
        if c['order_index'] != idx:
            cursor.execute("UPDATE roadmap_nodes SET order_index = ? WHERE id = ?", (idx, c['id']))
            fixed_orders += 1

conn.commit()
print(f"Fixed {fixed_orders} order_index values to be strictly sequential (1, 2, 3...).")

# 2. Check the 2 unassigned Excel videos
import pandas as pd
df_excel = pd.read_excel("Striver_A2Z_Playlist_Links.xlsx")
excel_vids = set(df_excel['Video ID'].dropna().astype(str).tolist())

cursor.execute("SELECT youtube_video_id FROM roadmap_nodes WHERE youtube_video_id IS NOT NULL")
db_vids = set([r[0] for r in cursor.fetchall()])

unassigned = excel_vids - db_vids
print(f"Unassigned Excel Video IDs ({len(unassigned)}):")
for vid in unassigned:
    row = df_excel[df_excel['Video ID'] == vid].iloc[0]
    print(f"  S.No {row['S.No']}: {row['Title']} (ID: {vid})")

conn.close()
