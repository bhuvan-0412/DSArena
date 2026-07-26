"""
audit_curriculum.py
-------------------
Script to perform STEP 1 & STEP 2 audit of DSArena database against Striver A2Z hierarchy & Excel video sources.
"""

import os
import sys
import json
import sqlite3
import pandas as pd
from typing import Dict, List, Set, Tuple

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dsarena.db")
EXCEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "Striver_A2Z_Playlist_Links.xlsx"))

def run_audit():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("========================================================")
    print("STEP 1: AUDIT CURRENT DATABASE STATE (RoadmapNode & Normalized)")
    print("========================================================")

    # Fetch RoadmapNode records
    cursor.execute("SELECT * FROM roadmap_nodes ORDER BY order_index")
    nodes = [dict(r) for r in cursor.fetchall()]

    node_dict = {n['id']: n for n in nodes}
    nodes_by_type = {}
    for n in nodes:
        t = n['type']
        nodes_by_type.setdefault(t, []).append(n)

    steps = nodes_by_type.get('step', [])
    sections = nodes_by_type.get('section', [])
    topics = nodes_by_type.get('topic', [])
    lessons = nodes_by_type.get('lesson', []) + nodes_by_type.get('problem', []) + [n for n in nodes if n['type'] not in ('step', 'section', 'topic')]

    print(f"RoadmapNode Count by Type:")
    for t, l in nodes_by_type.items():
        print(f"  - {t}: {len(l)}")
    print(f"Total RoadmapNode records: {len(nodes)}")

    # Fetch Normalized Tables
    cursor.execute("SELECT COUNT(*) FROM roadmap_steps")
    norm_steps = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM roadmap_sections")
    norm_sections = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM roadmap_topics")
    norm_topics = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM roadmap_lessons")
    norm_lessons = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM lesson_videos")
    norm_videos = cursor.fetchone()[0]

    print("\nNormalized Table Counts:")
    print(f"  - RoadmapStep: {norm_steps}")
    print(f"  - RoadmapSection: {norm_sections}")
    print(f"  - RoadmapTopic: {norm_topics}")
    print(f"  - RoadmapLesson: {norm_lessons}")
    print(f"  - LessonVideo: {norm_videos}")

    # Integrity Checks on RoadmapNode
    print("\n--- Integrity Checks on RoadmapNode ---")

    # 1. Empty Titles
    empty_titles = [n for n in nodes if not n['title'] or not n['title'].strip()]
    print(f"• Empty Titles: {len(empty_titles)}")

    # 2. Duplicate Node IDs
    ids = [n['id'] for n in nodes]
    dup_ids = set([x for x in ids if ids.count(x) > 1])
    print(f"• Duplicate Node IDs: {len(dup_ids)}")

    # 3. Duplicate Slugs
    slugs = [n['slug'] for n in nodes if n.get('slug')]
    dup_slugs = set([x for x in slugs if slugs.count(x) > 1])
    print(f"• Duplicate Slugs: {len(dup_slugs)}")
    if dup_slugs:
        print(f"  Duplicate slug examples: {list(dup_slugs)[:10]}")

    # 4. Duplicate Titles (within same parent or overall)
    titles_by_parent = {}
    dup_nodes_same_parent = []
    for n in nodes:
        key = (n['parent_id'], n['title'].strip().lower())
        if key in titles_by_parent:
            dup_nodes_same_parent.append((n, titles_by_parent[key]))
        else:
            titles_by_parent[key] = n
    print(f"• Duplicate Nodes (Same Parent & Title): {len(dup_nodes_same_parent)}")

    # 5. Missing Parents / Orphan Nodes
    missing_parents = []
    orphan_nodes = []
    for n in nodes:
        pid = n['parent_id']
        if pid:
            if pid not in node_dict:
                missing_parents.append(n)
        else:
            if n['type'] != 'step':
                orphan_nodes.append(n)
    print(f"• Missing Parents (parent_id points to non-existent node): {len(missing_parents)}")
    print(f"• Orphan Nodes (non-step node with parent_id=None): {len(orphan_nodes)}")

    # 6. Ordering Issues
    # Check if children of each parent have gap or non-sequential order_index, or duplicate order_index
    children_by_parent = {}
    for n in nodes:
        children_by_parent.setdefault(n['parent_id'], []).append(n)

    wrong_ordering = []
    for pid, children in children_by_parent.items():
        orders = [c['order_index'] for c in children]
        if len(orders) != len(set(orders)):
            wrong_ordering.append((pid, "Duplicate order_index values", orders))

    print(f"• Parents with Wrong/Duplicate Ordering among children: {len(wrong_ordering)}")

    # 7. Video Integrity Checks
    nodes_with_video = [n for n in nodes if n.get('youtube_video_id') or n.get('youtube_url')]
    missing_videos = [n for n in nodes if n['type'] in ('topic', 'problem', 'lesson') and not n.get('youtube_video_id') and not n.get('youtube_url')]
    invalid_video_ids = []
    for n in nodes:
        vid = n.get('youtube_video_id')
        if vid:
            if len(vid) != 11 or not vid.isalnum() and not any(c in vid for c in '-_'):
                invalid_video_ids.append((n['id'], vid))

    print(f"• Nodes with Video: {len(nodes_with_video)}")
    print(f"• Missing Videos (topics/problems/lessons without video): {len(missing_videos)}")
    print(f"• Invalid Video IDs (length != 11 or bad chars): {len(invalid_video_ids)}")

    print("\n========================================================")
    print("STEP 2: COMPARE AGAINST EXCEL SOURCE OF TRUTH")
    print("========================================================")

    if os.path.exists(EXCEL_PATH):
        df_excel = pd.read_excel(EXCEL_PATH)
        print(f"Excel video count: {len(df_excel)}")
        print(f"Excel Columns: {list(df_excel.columns)}")

        excel_vids = set(df_excel['Video ID'].dropna().astype(str).tolist())

        # Check how many RoadmapNodes use Excel videos vs non-Excel videos
        node_vids = set([n['youtube_video_id'] for n in nodes if n.get('youtube_video_id')])
        matched_vids = node_vids.intersection(excel_vids)
        missing_excel_vids = excel_vids - matched_vids

        print(f"Roadmap Unique Video IDs: {len(node_vids)}")
        print(f"Matched Excel Video IDs: {len(matched_vids)} / {len(excel_vids)}")
        print(f"Excel Videos not assigned to any node: {len(missing_excel_vids)}")

    conn.close()

if __name__ == "__main__":
    run_audit()
