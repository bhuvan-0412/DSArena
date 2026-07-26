"""
sync_all_striver_steps.py
-------------------------
Populates all 18 Steps of Striver A2Z Roadmap into DSArena database (dsarena.db).
Ensures every node exists, has correct parent, order, title, and YouTube video from Striver_A2Z_Playlist_Links.xlsx.
Preserves user progress and normalized tables.
"""

import os
import sys
import json
import sqlite3
import re
import pandas as pd
from typing import Dict, List, Any, Optional

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "dsarena.db")
EXCEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "Striver_A2Z_Playlist_Links.xlsx"))

# 1. Load Excel Data
df_excel = pd.read_excel(EXCEL_PATH)
sno_to_row = {}
for _, row in df_excel.iterrows():
    sno = row['S.No']
    if pd.notna(sno) and str(sno).strip().isdigit():
        sno_int = int(sno)
        vid = str(row['Video ID']).strip() if pd.notna(row['Video ID']) else ""
        if vid and vid != 'nan':
            sno_to_row[sno_int] = {
                'sno': sno_int,
                'title': str(row['Title']).strip() if pd.notna(row['Title']) else "",
                'url': str(row['Video URL']).strip() if pd.notna(row['Video URL']) else "",
                'video_id': vid
            }

def clean_title(raw_title: str) -> str:
    title = re.sub(r'[\U00010000-\U0010ffff]', '', raw_title)  # Remove emojis
    title = re.sub(r'\|\s*Strivers\s*A2Z\s*DSA\s*Course.*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\|\s*Recursion\s*Tree.*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\|\s*Stack\s*Space.*', '', title, flags=re.IGNORECASE)
    title = re.sub(r'🔥', '', title)
    title = title.strip()
    return title

def make_slug(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    return slug or "node"

# Complete 18-Step Curriculum Mapping
CURRICULUM = [
    # STEP 1
    {
        "id": "step_1",
        "title": "Step 1: Learn the Basics",
        "slug": "learn-the-basics",
        "order": 1,
        "sections": [
            {"id": "sec_1_1", "title": "Things to Know in C++/Java/Python/JS", "slug": "things-to-know", "order": 1, "snos": [2, 3, 4]},
            {"id": "sec_1_2", "title": "Build-up Logical Thinking", "slug": "build-up-logical-thinking", "order": 2, "snos": [5]},
            {"id": "sec_1_3", "title": "Learn STL / Collections", "slug": "learn-stl-collections", "order": 3, "snos": [6]},
            {"id": "sec_1_4", "title": "Know Basic Maths", "slug": "know-basic-maths", "order": 4, "snos": [7, 265, 266, 267, 268, 269, 270, 271]},
            {"id": "sec_1_5", "title": "Learn Basic Recursion", "slug": "learn-basic-recursion", "order": 5, "snos": [8, 9, 10, 11, 12]},
            {"id": "sec_1_6", "title": "Learn Basic Hashing", "slug": "learn-basic-hashing", "order": 6, "snos": [13]}
        ]
    },
    # STEP 2
    {
        "id": "step_2",
        "title": "Step 2: Learn Important Sorting Techniques",
        "slug": "learn-important-sorting-techniques",
        "order": 2,
        "sections": [
            {"id": "sec_2_1", "title": "Sorting-I", "slug": "sorting-i", "order": 1, "snos": [14]},
            {"id": "sec_2_2", "title": "Sorting-II", "slug": "sorting-ii", "order": 2, "snos": [15, 16]}
        ]
    },
    # STEP 3
    {
        "id": "step_3",
        "title": "Step 3: Solve Problems on Arrays [Easy -> Medium -> Hard]",
        "slug": "arrays-easy-medium-hard",
        "order": 3,
        "sections": [
            {"id": "sec_3_1", "title": "Arrays Easy", "slug": "arrays-easy", "order": 1, "snos": [17, 18, 19, 20]},
            {"id": "sec_3_2", "title": "Arrays Medium", "slug": "arrays-medium", "order": 2, "snos": [21, 22, 23, 24, 25, 26, 27]},
            {"id": "sec_3_3", "title": "Arrays Hard", "slug": "arrays-hard", "order": 3, "snos": [28, 29, 30]}
        ]
    },
    # STEP 4
    {
        "id": "step_4",
        "title": "Step 4: Binary Search [1D, 2D Arrays, Search Space]",
        "slug": "binary-search-arrays",
        "order": 4,
        "sections": [
            {"id": "sec_4_1", "title": "BS on 1D Arrays", "slug": "bs-on-1d-arrays", "order": 1, "snos": [31, 32, 33, 34, 35, 36]},
            {"id": "sec_4_2", "title": "BS on Answers", "slug": "bs-on-answers", "order": 2, "snos": [37, 38, 39, 40, 41, 42, 43]},
            {"id": "sec_4_3", "title": "BS on 2D Arrays", "slug": "bs-on-2d-arrays", "order": 3, "snos": [44, 45, 46]}
        ]
    },
    # STEP 5
    {
        "id": "step_5",
        "title": "Step 5: Learn Strings [Easy -> Medium]",
        "slug": "learn-strings",
        "order": 5,
        "sections": [
            {"id": "sec_5_1", "title": "Strings Easy", "slug": "strings-easy", "order": 1, "snos": [47, 48, 49]},
            {"id": "sec_5_2", "title": "Strings Medium", "slug": "strings-medium", "order": 2, "snos": [50, 51, 52, 53]}
        ]
    },
    # STEP 6
    {
        "id": "step_6",
        "title": "Step 6: Learn LinkedList [Single LL, Double LL, Medium, Hard Problems]",
        "slug": "learn-linked-list",
        "order": 6,
        "sections": [
            {"id": "sec_6_1", "title": "Learn 1D LinkedList", "slug": "learn-1d-linkedlist", "order": 1, "snos": [237, 238]},
            {"id": "sec_6_2", "title": "Learn Doubly LinkedList", "slug": "learn-doubly-linkedlist", "order": 2, "snos": [239, 240]},
            {"id": "sec_6_3", "title": "Medium Problems of LL", "slug": "medium-problems-of-ll", "order": 3, "snos": [241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253]},
            {"id": "sec_6_4", "title": "Doubly LinkedList Medium/Hard", "slug": "doubly-linkedlist-medium-hard", "order": 4, "snos": [254, 255, 256, 264]},
            {"id": "sec_6_5", "title": "Hard Problems of LL", "slug": "hard-problems-of-ll", "order": 5, "snos": [257, 258, 259, 260, 261, 262, 263]}
        ]
    },
    # STEP 7
    {
        "id": "step_7",
        "title": "Step 7: Recursion [Patternwise Problems]",
        "slug": "recursion-patternwise",
        "order": 7,
        "sections": [
            {"id": "sec_7_1", "title": "Get a Strong Hold", "slug": "get-a-strong-hold", "order": 1, "snos": [54, 55, 56, 57]},
            {"id": "sec_7_2", "title": "Subsequences Pattern", "slug": "subsequences-pattern", "order": 2, "snos": [58, 59, 60, 61, 62, 63, 64]},
            {"id": "sec_7_3", "title": "Trying out all Combo / Hard Recursion", "slug": "trying-out-all-combo-hard-recursion", "order": 3, "snos": [65, 66, 67, 68]}
        ]
    },
    # STEP 8
    {
        "id": "step_8",
        "title": "Step 8: Bit Manipulation [Concepts & Problems]",
        "slug": "bit-manipulation",
        "order": 8,
        "sections": [
            {"id": "sec_8_1", "title": "Learn Bit Manipulation", "slug": "learn-bit-manipulation", "order": 1, "snos": [69, 70, 71, 72]},
            {"id": "sec_8_2", "title": "Interview Problems", "slug": "bit-interview-problems", "order": 2, "snos": [73, 74, 75, 76, 77]},
            {"id": "sec_8_3", "title": "Advanced Maths & Bit Manipulation", "slug": "advanced-maths-bit-manipulation", "order": 3, "snos": [78, 79, 80]}
        ]
    },
    # STEP 9
    {
        "id": "step_9",
        "title": "Step 9: Stack and Queues [Learning, Pre-In-Post, Monotonic Stack]",
        "slug": "stack-and-queues",
        "order": 9,
        "sections": [
            {"id": "sec_9_1", "title": "Learning Stack & Queue", "slug": "learning-stack-queue", "order": 1, "snos": [297, 298, 300]},
            {"id": "sec_9_2", "title": "Prefix, Infix, Postfix Conversion", "slug": "prefix-infix-postfix-conversion", "order": 2, "snos": [299]},
            {"id": "sec_9_3", "title": "Monotonic Stack / Queue Problems", "slug": "monotonic-stack-queue-problems", "order": 3, "snos": [301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313]},
            {"id": "sec_9_4", "title": "Implementation Problems", "slug": "stack-queue-implementation-problems", "order": 4, "snos": [314, 315]}
        ]
    },
    # STEP 10
    {
        "id": "step_10",
        "title": "Step 10: Sliding Window & Two Pointer Combined Problems",
        "slug": "sliding-window-two-pointer",
        "order": 10,
        "sections": [
            {"id": "sec_10_1", "title": "Medium Problems", "slug": "sliding-window-medium", "order": 1, "snos": [272, 273, 274, 275, 276, 277]},
            {"id": "sec_10_2", "title": "Hard Problems", "slug": "sliding-window-hard", "order": 2, "snos": [278, 279, 280, 281, 282, 283]}
        ]
    },
    # STEP 11
    {
        "id": "step_11",
        "title": "Step 11: Heaps [Learning, Medium, Hard Problems]",
        "slug": "heaps-learning-problems",
        "order": 11,
        "sections": [
            {"id": "sec_11_1", "title": "Learning Heap", "slug": "learning-heap", "order": 1, "custom_topics": [{"title": "Introduction to Priority Queue and Heaps", "video_id": "NKJnHewiGdc"}]},
            {"id": "sec_11_2", "title": "Medium Problems", "slug": "heap-medium-problems", "order": 2, "custom_topics": [{"title": "Kth Largest Element in an Array", "video_id": "yAs3tO5zTBA"}]},
            {"id": "sec_11_3", "title": "Hard Problems", "slug": "heap-hard-problems", "order": 3, "custom_topics": [{"title": "Find Median from Data Stream", "video_id": "1LkBwstvKq4"}]}
        ]
    },
    # STEP 12
    {
        "id": "step_12",
        "title": "Step 12: Greedy Algorithms [Easy, Medium/Hard]",
        "slug": "greedy-algorithms",
        "order": 12,
        "sections": [
            {"id": "sec_12_1", "title": "Easy Problems", "slug": "greedy-easy-problems", "order": 1, "snos": [284, 286]},
            {"id": "sec_12_2", "title": "Medium/Hard Problems", "slug": "greedy-medium-hard-problems", "order": 2, "snos": [285, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296]}
        ]
    },
    # STEP 13
    {
        "id": "step_13",
        "title": "Step 13: Binary Trees [Traversals, Medium, Hard Problems]",
        "slug": "binary-trees",
        "order": 13,
        "sections": [
            {"id": "sec_13_1", "title": "Traversals", "slug": "binary-tree-traversals", "order": 1, "snos": [81, 82, 83, 84, 85, 86, 87, 88, 89]},
            {"id": "sec_13_2", "title": "Medium Problems", "slug": "binary-tree-medium", "order": 2, "snos": [90, 91, 92, 93, 94, 95, 96, 97, 98, 99]},
            {"id": "sec_13_3", "title": "Hard Problems", "slug": "binary-tree-hard", "order": 3, "snos": [100, 101, 102, 103, 104, 105]}
        ]
    },
    # STEP 14
    {
        "id": "step_14",
        "title": "Step 14: Binary Search Trees [Concepts, Practice Problems]",
        "slug": "binary-search-trees",
        "order": 14,
        "sections": [
            {"id": "sec_14_1", "title": "Concepts", "slug": "bst-concepts", "order": 1, "snos": [106, 107]},
            {"id": "sec_14_2", "title": "Practice Problems", "slug": "bst-practice-problems", "order": 2, "snos": [108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125]}
        ]
    },
    # STEP 15
    {
        "id": "step_15",
        "title": "Step 15: Graphs [Learning, BFS/DFS, Topo Sort, Shortest Path, MST]",
        "slug": "graphs",
        "order": 15,
        "sections": [
            {"id": "sec_15_1", "title": "Learning Graph", "slug": "learning-graph", "order": 1, "snos": [126, 127, 128]},
            {"id": "sec_15_2", "title": "Problems on BFS/DFS", "slug": "problems-on-bfs-dfs", "order": 2, "snos": [129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142]},
            {"id": "sec_15_3", "title": "Topo Sort and Problems", "slug": "topo-sort-and-problems", "order": 3, "snos": [143, 144, 145, 146, 147]},
            {"id": "sec_15_4", "title": "Shortest Path Algorithms and Problems", "slug": "shortest-path-algorithms", "order": 4, "snos": [148, 149, 150, 151, 152, 153, 154, 155, 156]},
            {"id": "sec_15_5", "title": "Minimum Spanning Tree / Disjoint Set", "slug": "mst-disjoint-set", "order": 5, "snos": [157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168]},
            {"id": "sec_15_6", "title": "Other Graph Algorithms", "slug": "other-graph-algorithms", "order": 6, "snos": [169, 170, 171, 172, 173]}
        ]
    },
    # STEP 16
    {
        "id": "step_16",
        "title": "Step 16: Dynamic Programming [1D, 2D/3D, Grids, Subsequences, Strings, Stocks, LIS, MCM]",
        "slug": "dynamic-programming",
        "order": 16,
        "sections": [
            {"id": "sec_16_1", "title": "Introduction to DP", "slug": "introduction-to-dp", "order": 1, "snos": [174, 175]},
            {"id": "sec_16_2", "title": "1D DP", "slug": "1d-dp", "order": 2, "snos": [176, 177, 178, 179]},
            {"id": "sec_16_3", "title": "2D/3D DP and DP on Grids", "slug": "2d-3d-dp-grids", "order": 3, "snos": [180, 181, 182, 183, 184, 185, 186]},
            {"id": "sec_16_4", "title": "DP on Subsequences / Sets", "slug": "dp-on-subsequences", "order": 4, "snos": [187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199]},
            {"id": "sec_16_5", "title": "DP on Strings", "slug": "dp-on-strings", "order": 5, "snos": [200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215]},
            {"id": "sec_16_6", "title": "DP on Stocks", "slug": "dp-on-stocks", "order": 6, "snos": [216, 217, 218, 219, 220]},
            {"id": "sec_16_7", "title": "DP on LIS", "slug": "dp-on-lis", "order": 7, "snos": [221, 222, 223, 224, 225, 226, 227]},
            {"id": "sec_16_8", "title": "MCM DP / Partition DP", "slug": "mcm-partition-dp", "order": 8, "snos": [228, 229, 230, 231, 232, 233, 234]},
            {"id": "sec_16_9", "title": "DP on Rectangles / Squares", "slug": "dp-on-rectangles", "order": 9, "snos": [235, 236]}
        ]
    },
    # STEP 17
    {
        "id": "step_17",
        "title": "Step 17: Tries [Theory and Problems]",
        "slug": "tries",
        "order": 17,
        "sections": [
            {"id": "sec_17_1", "title": "Theory & Implementation", "slug": "trie-theory-implementation", "order": 1, "custom_topics": [{"title": "Implement Trie (Prefix Tree)", "video_id": "dBGUmUQhjaM"}]},
            {"id": "sec_17_2", "title": "Problems", "slug": "trie-problems", "order": 2, "custom_topics": [{"title": "Maximum XOR of Two Numbers in an Array", "video_id": "EIhYU2uDChU"}]}
        ]
    },
    # STEP 18
    {
        "id": "step_18",
        "title": "Step 18: Advanced String Algorithms",
        "slug": "advanced-string-algorithms",
        "order": 18,
        "sections": [
            {"id": "sec_18_1", "title": "Advanced String Matching", "slug": "advanced-string-matching", "order": 1, "custom_topics": [{"title": "KMP Algorithm / Z-Function String Matching", "video_id": "V5-7GzOfADQ"}]}
        ]
    }
]

def run_sync():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    nodes_created = 0
    nodes_updated = 0
    videos_attached = 0

    print("Starting full database synchronization...")

    for step in CURRICULUM:
        step_id = step["id"]
        step_title = step["title"]
        step_slug = step["slug"]
        step_order = step["order"]

        # 1. Upsert Step in RoadmapNode
        cursor.execute("SELECT id FROM roadmap_nodes WHERE id = ?", (step_id,))
        if cursor.fetchone():
            cursor.execute("UPDATE roadmap_nodes SET title=?, slug=?, order_index=? WHERE id=?",
                           (step_title, step_slug, step_order, step_id))
            nodes_updated += 1
        else:
            cursor.execute("""
                INSERT INTO roadmap_nodes (id, parent_id, title, slug, type, order_index, estimated_time, xp_reward, difficulty)
                VALUES (?, NULL, ?, ?, 'step', ?, 600, 1000, 'Medium')
            """, (step_id, step_title, step_slug, step_order))
            nodes_created += 1

        # Upsert in RoadmapStep
        cursor.execute("SELECT id FROM roadmap_steps WHERE id = ?", (step_id,))
        if cursor.fetchone():
            cursor.execute("UPDATE roadmap_steps SET title=?, slug=?, order_index=? WHERE id=?",
                           (step_title, step_slug, step_order, step_id))
        else:
            cursor.execute("INSERT INTO roadmap_steps (id, title, slug, order_index) VALUES (?, ?, ?, ?)",
                           (step_id, step_title, step_slug, step_order))

        # 2. Sections
        for sec in step["sections"]:
            sec_id = sec["id"]
            sec_title = sec["title"]
            sec_slug = sec["slug"]
            sec_order = sec["order"]

            # Upsert Section in RoadmapNode
            cursor.execute("SELECT id FROM roadmap_nodes WHERE id = ?", (sec_id,))
            if cursor.fetchone():
                cursor.execute("UPDATE roadmap_nodes SET parent_id=?, title=?, slug=?, order_index=? WHERE id=?",
                               (step_id, sec_title, sec_slug, sec_order, sec_id))
                nodes_updated += 1
            else:
                cursor.execute("""
                    INSERT INTO roadmap_nodes (id, parent_id, title, slug, type, order_index, estimated_time, xp_reward, difficulty)
                    VALUES (?, ?, ?, ?, 'section', ?, 180, 200, 'Easy')
                """, (sec_id, step_id, sec_title, sec_slug, sec_order))
                nodes_created += 1

            # Upsert Section in RoadmapSection
            cursor.execute("SELECT id FROM roadmap_sections WHERE id = ?", (sec_id,))
            if cursor.fetchone():
                cursor.execute("UPDATE roadmap_sections SET step_id=?, parent_id=?, title=?, slug=?, order_index=? WHERE id=?",
                               (step_id, step_id, sec_title, sec_slug, sec_order, sec_id))
            else:
                cursor.execute("INSERT INTO roadmap_sections (id, step_id, parent_id, title, slug, order_index) VALUES (?, ?, ?, ?, ?, ?)",
                               (sec_id, step_id, step_id, sec_title, sec_slug, sec_order))

            # 3. Topics / Lessons
            topic_list = []
            if "snos" in sec and sec["snos"]:
                for idx, sno in enumerate(sec["snos"], start=1):
                    if sno in sno_to_row:
                        r = sno_to_row[sno]
                        topic_list.append({
                            "id": f"topic_{sec_id}_{idx}",
                            "title": clean_title(r["title"]),
                            "slug": make_slug(clean_title(r["title"])),
                            "video_id": r["video_id"],
                            "url": r["url"],
                            "order": idx
                        })
            elif "custom_topics" in sec:
                for idx, ct in enumerate(sec["custom_topics"], start=1):
                    vid = ct["video_id"]
                    topic_list.append({
                        "id": f"topic_{sec_id}_{idx}",
                        "title": ct["title"],
                        "slug": make_slug(ct["title"]),
                        "video_id": vid,
                        "url": f"https://www.youtube.com/watch?v={vid}",
                        "order": idx
                    })

            for t in topic_list:
                top_id = t["id"]
                top_title = t["title"]
                top_slug = t["slug"]
                top_order = t["order"]
                top_vid = t["video_id"]
                top_url = t["url"]
                top_thumb = f"https://img.youtube.com/vi/{top_vid}/hqdefault.jpg"

                # Upsert Topic in RoadmapNode
                cursor.execute("SELECT id FROM roadmap_nodes WHERE id = ?", (top_id,))
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE roadmap_nodes
                        SET parent_id=?, title=?, slug=?, order_index=?, youtube_url=?, youtube_video_id=?, thumbnail_url=?
                        WHERE id=?
                    """, (sec_id, top_title, top_slug, top_order, top_url, top_vid, top_thumb, top_id))
                    nodes_updated += 1
                else:
                    cursor.execute("""
                        INSERT INTO roadmap_nodes (id, parent_id, title, slug, type, order_index, estimated_time, xp_reward, difficulty, youtube_url, youtube_video_id, thumbnail_url)
                        VALUES (?, ?, ?, ?, 'topic', ?, 15, 50, 'Easy', ?, ?, ?)
                    """, (top_id, sec_id, top_title, top_slug, top_order, top_url, top_vid, top_thumb))
                    nodes_created += 1

                videos_attached += 1

                # Upsert RoadmapTopic
                cursor.execute("SELECT id FROM roadmap_topics WHERE id = ?", (top_id,))
                if cursor.fetchone():
                    cursor.execute("UPDATE roadmap_topics SET section_id=?, parent_id=?, title=?, slug=?, order_index=? WHERE id=?",
                                   (sec_id, sec_id, top_title, top_slug, top_order, top_id))
                else:
                    cursor.execute("INSERT INTO roadmap_topics (id, section_id, parent_id, title, slug, order_index) VALUES (?, ?, ?, ?, ?, ?)",
                                   (top_id, sec_id, sec_id, top_title, top_slug, top_order))

                # Upsert RoadmapLesson
                cursor.execute("SELECT id FROM roadmap_lessons WHERE id = ?", (top_id,))
                if cursor.fetchone():
                    cursor.execute("UPDATE roadmap_lessons SET topic_id=?, parent_id=?, title=?, slug=?, order_index=? WHERE id=?",
                                   (top_id, sec_id, top_title, top_slug, top_order, top_id))
                else:
                    cursor.execute("INSERT INTO roadmap_lessons (id, topic_id, parent_id, title, slug, order_index) VALUES (?, ?, ?, ?, ?, ?)",
                                   (top_id, top_id, sec_id, top_title, top_slug, top_order))

                # Upsert LessonVideo
                cursor.execute("SELECT id FROM lesson_videos WHERE lesson_id = ? AND video_id = ?", (top_id, top_vid))
                if cursor.fetchone():
                    cursor.execute("UPDATE lesson_videos SET title=?, url=?, thumbnail=? WHERE lesson_id=? AND video_id=?",
                                   (top_title, top_url, top_thumb, top_id, top_vid))
                else:
                    cursor.execute("""
                        INSERT INTO lesson_videos (lesson_id, title, provider, url, video_id, thumbnail, duration, is_primary, source, order_index)
                        VALUES (?, ?, 'youtube', ?, ?, ?, '15 mins', 1, 'Striver A2Z Excel', 1)
                    """, (top_id, top_title, top_url, top_vid, top_thumb))

    conn.commit()
    conn.close()

    print(f"Synchronization complete!")
    print(f"  - Nodes Created: {nodes_created}")
    print(f"  - Nodes Updated: {nodes_updated}")
    print(f"  - Videos Attached: {videos_attached}")

if __name__ == "__main__":
    run_sync()
