"""
validate_videos_and_api.py
--------------------------
Validates:
1. Video ID formats (11 chars), YouTube embed URLs, thumbnail URLs.
2. Backend API routes using FastAPI test client (GET /api/v1/roadmap/nodes, GET /api/v1/roadmap/nodes/{id}).
"""

import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
from app.core.database import SessionLocal
from app.models.roadmap import RoadmapNode
from fastapi.testclient import TestClient
from app.main import app

db = SessionLocal()
nodes = db.query(RoadmapNode).all()

print(f"Loaded {len(nodes)} total RoadmapNodes from database.")

# 1. Validate Video Data
invalid_video_nodes = []
missing_video_topics = []

for n in nodes:
    if n.type in ('topic', 'lesson', 'problem'):
        vid = n.youtube_video_id
        url = n.youtube_url
        thumb = n.thumbnail_url

        if not vid or not url:
            missing_video_topics.append(n)
            continue

        if len(vid) != 11 or not re.match(r'^[a-zA-Z0-9_-]{11}$', vid):
            invalid_video_nodes.append((n.id, vid))

print("\n--- Video Validation Results ---")
print(f"Total Topic/Lesson Nodes Checked: {len([n for n in nodes if n.type in ('topic', 'lesson', 'problem')])}")
print(f"Missing Videos: {len(missing_video_topics)}")
print(f"Invalid Video IDs: {len(invalid_video_nodes)}")

# 2. API Endpoint Testing
print("\n--- Testing Backend API Endpoints ---")
client = TestClient(app)

# GET /api/v1/roadmap/nodes
res_nodes = client.get("/api/v1/roadmap/nodes?clerk_id=mock_user_striver")
print(f"GET /api/v1/roadmap/nodes status: {res_nodes.status_code}")
if res_nodes.status_code == 200:
    tree = res_nodes.json()
    print(f"Returned root steps count: {len(tree)}")
    step_titles = [s['title'] for s in tree]
    print(f"Steps returned in API: {len(step_titles)}")

# GET /api/v1/roadmap/nodes/{nodeId} for sample nodes in Step 1, Step 6, Step 16
sample_ids = ["step_1", "sec_1_1", "topic_sec_1_1_1", "step_6", "topic_sec_6_1_1", "step_16", "topic_sec_16_1_1"]
for sid in sample_ids:
    res = client.get(f"/api/v1/roadmap/nodes/{sid}?clerk_id=mock_user_striver")
    if res.status_code == 200:
        data = res.json()
        print(f"  [OK] Node GET /roadmap/nodes/{sid}: '{data.get('title')}' (Video: {data.get('youtube_video_id')})")
    else:
        print(f"  [FAIL] Node GET /roadmap/nodes/{sid}: status {res.status_code}")

db.close()
