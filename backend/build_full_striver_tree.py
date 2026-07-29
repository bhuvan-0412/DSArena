"""
build_full_striver_tree.py
--------------------------
Constructs the complete 18-Step Striver A2Z DSA Curriculum data structure,
associates all 316 Excel playlist videos to their corresponding step, section,
and topic nodes, and synchronizes the database safely.
"""

import os
import sys
import json
import re
import pandas as pd
from typing import Dict, List, Any, Optional

# Ensure UTF-8
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "Striver_A2Z_Playlist_Links.xlsx"))

# 18 Steps Definition
STEPS_DEF = [
    {"id": "step_1", "title": "Step 1: Learn the Basics", "slug": "learn-the-basics", "order": 1, "time": 360, "xp": 500, "difficulty": "Easy"},
    {"id": "step_2", "title": "Step 2: Learn Important Sorting Techniques", "slug": "learn-important-sorting-techniques", "order": 2, "time": 180, "xp": 300, "difficulty": "Easy"},
    {"id": "step_3", "title": "Step 3: Solve Problems on Arrays [Easy -> Medium -> Hard]", "slug": "arrays-easy-medium-hard", "order": 3, "time": 720, "xp": 1000, "difficulty": "Medium"},
    {"id": "step_4", "title": "Step 4: Binary Search [1D, 2D Arrays, Search Space]", "slug": "binary-search-arrays", "order": 4, "time": 600, "xp": 800, "difficulty": "Medium"},
    {"id": "step_5", "title": "Step 5: Learn Strings [Easy -> Medium]", "slug": "learn-strings", "order": 5, "time": 480, "xp": 600, "difficulty": "Medium"},
    {"id": "step_6", "title": "Step 6: Learn LinkedList [Single LL, Double LL, Medium, Hard Problems]", "slug": "learn-linked-list", "order": 6, "time": 720, "xp": 900, "difficulty": "Medium"},
    {"id": "step_7", "title": "Step 7: Recursion [Patternwise Problems]", "slug": "recursion-patternwise", "order": 7, "time": 600, "xp": 800, "difficulty": "Hard"},
    {"id": "step_8", "title": "Step 8: Bit Manipulation [Concepts & Problems]", "slug": "bit-manipulation", "order": 8, "time": 480, "xp": 600, "difficulty": "Medium"},
    {"id": "step_9", "title": "Step 9: Stack and Queues [Learning, Pre-In-Post, Monotonic Stack]", "slug": "stack-and-queues", "order": 9, "time": 720, "xp": 900, "difficulty": "Medium"},
    {"id": "step_10", "title": "Step 10: Sliding Window & Two Pointer Combined Problems", "slug": "sliding-window-two-pointer", "order": 10, "time": 480, "xp": 700, "difficulty": "Medium"},
    {"id": "step_11", "title": "Step 11: Heaps [Learning, Medium, Hard Problems]", "slug": "heaps-learning-problems", "order": 11, "time": 420, "xp": 600, "difficulty": "Medium"},
    {"id": "step_12", "title": "Step 12: Greedy Algorithms [Easy, Medium/Hard]", "slug": "greedy-algorithms", "order": 12, "time": 480, "xp": 600, "difficulty": "Medium"},
    {"id": "step_13", "title": "Step 13: Binary Trees [Traversals, Medium, Hard Problems]", "slug": "binary-trees", "order": 13, "time": 900, "xp": 1200, "difficulty": "Hard"},
    {"id": "step_14", "title": "Step 14: Binary Search Trees [Concepts, Practice Problems]", "slug": "binary-search-trees", "order": 14, "time": 600, "xp": 800, "difficulty": "Hard"},
    {"id": "step_15", "title": "Step 15: Graphs [Learning, BFS/DFS, Topo Sort, Shortest Path, MST]", "slug": "graphs", "order": 15, "time": 1200, "xp": 1500, "difficulty": "Hard"},
    {"id": "step_16", "title": "Step 16: Dynamic Programming [1D, 2D/3D, Grids, Subsequences, Strings, Stocks, LIS, MCM]", "slug": "dynamic-programming", "order": 16, "time": 1500, "xp": 2000, "difficulty": "Hard"},
    {"id": "step_17", "title": "Step 17: Tries [Theory and Problems]", "slug": "tries", "order": 17, "time": 360, "xp": 500, "difficulty": "Hard"},
    {"id": "step_18", "title": "Step 18: Advanced String Algorithms", "slug": "advanced-string-algorithms", "order": 18, "time": 360, "xp": 500, "difficulty": "Hard"},
]

def load_excel_mapping():
    df = pd.read_excel(EXCEL_PATH)
    rows = []
    for _, r in df.iterrows():
        sno = r['S.No']
        title = str(r['Title']).strip() if pd.notna(r['Title']) else ""
        vurl = str(r['Video URL']).strip() if pd.notna(r['Video URL']) else ""
        vid = str(r['Video ID']).strip() if pd.notna(r['Video ID']) else ""
        if sno and vid and vid != 'nan':
            rows.append({
                "sno": int(sno),
                "title": title,
                "video_url": vurl,
                "video_id": vid,
            })
    return rows

print("Script template ready.")
