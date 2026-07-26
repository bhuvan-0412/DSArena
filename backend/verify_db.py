"""Verify DB: show youtube_video_id for every topic and problem node."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal
from app.models.roadmap import RoadmapNode

db = SessionLocal()
nodes = db.query(RoadmapNode).filter(RoadmapNode.type.in_(["topic","problem"])).all()
nodes.sort(key=lambda n: (n.type, n.order_index))

with_video    = [n for n in nodes if n.youtube_video_id]
without_video = [n for n in nodes if not n.youtube_video_id]

print(f"\nTotal topic/problem nodes : {len(nodes)}")
print(f"With youtube_video_id     : {len(with_video)}")
print(f"Without youtube_video_id  : {len(without_video)}")
print()

if without_video:
    print("--- Nodes WITHOUT video ---")
    for n in without_video:
        print(f"  [{n.type}] {n.id}: {n.title}")

print()
print("--- Sample: first 10 nodes WITH video ---")
for n in with_video[:10]:
    meta = n.node_metadata or {}
    src  = meta.get("source","?") if isinstance(meta,dict) else "?"
    tier = meta.get("match_tier","?") if isinstance(meta,dict) else "?"
    print(f"  [{n.type}] {n.title[:50]} => {n.youtube_video_id} (T{tier}, src={src})")

db.close()
