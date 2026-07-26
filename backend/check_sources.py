"""Check source metadata on all topic nodes."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal
from app.models.roadmap import RoadmapNode

db = SessionLocal()
nodes = db.query(RoadmapNode).filter(RoadmapNode.type == "topic").all()

by_source = {}
for n in nodes:
    meta = n.node_metadata or {}
    src = meta.get("source","unknown") if isinstance(meta,dict) else "unknown"
    by_source.setdefault(src,[]).append(n)

for src, ns in by_source.items():
    print(f"\n[Source: {src}] ({len(ns)} nodes)")
    for n in ns[:5]:
        print(f"  {n.title} => {n.youtube_video_id}")
    if len(ns) > 5:
        print(f"  ... and {len(ns)-5} more")

db.close()
