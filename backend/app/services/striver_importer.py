"""
Official Striver (TakeUForward) Video Importer & Multi-Tier Matching Engine.
Traverses all roadmap nodes and matches them with official Striver video tutorials.
"""

import json
import re
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.roadmap import RoadmapNode
from app.services.striver_catalog import STRIVER_A2Z_CATALOG, DEFAULT_STRIVER_VIDEO

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("StriverImporter")

STOP_WORDS = {
    "learn", "basic", "basics", "in", "the", "a", "an", "and", "or", "to", "for", "of", "with",
    "statements", "statement", "technique", "techniques", "algorithm", "algorithms",
    "problem", "problems", "topic", "section", "step", "easy", "medium", "hard"
}

def normalize_text(text: Optional[str]) -> str:
    """Normalizes string by lowercasing, stripping punctuation, and removing filler stop words."""
    if not text:
        return ""
    # Lowercase & replace non-alphanumeric with spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    tokens = [t for t in cleaned.split() if t not in STOP_WORDS and len(t) > 1]
    return " ".join(tokens)

def extract_youtube_video_id(url: Optional[str]) -> Optional[str]:
    """Extracts 11-character YouTube video ID from various URL formats."""
    if not url:
        return None
    short_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
    if short_match:
        return short_match.group(1)
    watch_match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
    if watch_match:
        return watch_match.group(1)
    embed_match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', url)
    if embed_match:
        return embed_match.group(1)
    return None

def generate_thumbnail_url(video_id: Optional[str]) -> Optional[str]:
    """Generates standard YouTube HQ thumbnail URL."""
    if not video_id:
        return None
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

def calculate_match_score(node_title: str, catalog_title: str, aliases: List[str]) -> float:
    """Calculates token similarity score between node title and catalog entry."""
    norm_node = set(normalize_text(node_title).split())
    if not norm_node:
        return 0.0

    all_cat_titles = [catalog_title] + aliases
    best_score = 0.0

    for cat_t in all_cat_titles:
        norm_cat = set(normalize_text(cat_t).split())
        if not norm_cat:
            continue
        
        intersection = norm_node.intersection(norm_cat)
        if not intersection:
            continue

        # Jaccard + Overlap blend
        jaccard = len(intersection) / len(norm_node.union(norm_cat))
        overlap = len(intersection) / min(len(norm_node), len(norm_cat))
        score = 0.6 * jaccard + 0.4 * overlap
        if score > best_score:
            best_score = score

    return best_score

class StriverVideoImporter:
    def __init__(self, db: Session, force: bool = False, output_json_path: str = "unmatched_nodes.json"):
        self.db = db
        self.force = force
        self.output_json_path = output_json_path

        # Metrics
        self.total_nodes = 0
        self.matched_nodes = 0
        self.unmatched_nodes = 0
        self.duplicate_matches = 0
        self.invalid_urls = 0
        self.missing_videos = 0

        self.unmatched_records: List[Dict[str, Any]] = []

    def find_best_catalog_match(self, node: RoadmapNode) -> Tuple[Optional[Dict[str, Any]], float, List[str]]:
        """Multi-tiered matching engine to pair roadmap node with catalog lesson."""
        possible_matches = []
        best_item = None
        best_score = 0.0

        for item in STRIVER_A2Z_CATALOG:
            # Tier 1: Exact Title or Alias Match
            if node.title.strip().lower() == item["title"].strip().lower():
                return item, 1.0, [item["title"]]

            for alias in item.get("aliases", []):
                if node.title.strip().lower() == alias.strip().lower():
                    return item, 1.0, [alias]

            # Tier 2 & 3: Token Similarity Score
            score = calculate_match_score(node.title, item["title"], item.get("aliases", []))
            if score >= 0.4:
                possible_matches.append(f"{item['title']} (score: {score:.2f})")
                if score > best_score:
                    best_score = score
                    best_item = item

        return best_item, best_score, possible_matches

    def run_import(self) -> Dict[str, Any]:
        """Executes full import pipeline across all roadmap nodes."""
        logger.info("Starting official Striver (TakeUForward) Video Importer pipeline...")
        
        all_nodes = self.db.query(RoadmapNode).all()
        self.total_nodes = len(all_nodes)

        for node in all_nodes:
            # Container nodes (step / section) have videos attached to their child topic nodes
            if node.type in ["step", "section"]:
                self.unmatched_nodes += 1
                self.unmatched_records.append({
                    "node_id": node.id,
                    "title": node.title,
                    "type": node.type,
                    "reason": f"Container {node.type} node (learning videos attached to child topic nodes)",
                    "possible_matches": []
                })
                continue

            # Check if video already exists and --force is not specified
            if node.youtube_url and not self.force:
                yt_id = node.youtube_video_id or extract_youtube_video_id(node.youtube_url)
                if yt_id:
                    self.matched_nodes += 1
                    continue

            # Perform multi-tiered catalog match
            match, score, possible = self.find_best_catalog_match(node)

            if match:
                yt_url = match["youtube_url"]
                yt_id = match.get("video_id") or extract_youtube_video_id(yt_url)
                
                if not yt_id:
                    self.invalid_urls += 1
                    logger.warning(f"Invalid YouTube URL found for node '{node.id}': {yt_url}")
                    yt_url = DEFAULT_STRIVER_VIDEO["youtube_url"]
                    yt_id = DEFAULT_STRIVER_VIDEO["video_id"]

                thumb_url = generate_thumbnail_url(yt_id)

                # Update node record
                node.youtube_url = yt_url
                node.youtube_video_id = yt_id
                node.thumbnail_url = thumb_url
                if match.get("estimated_duration"):
                    node.estimated_time = match["estimated_duration"]

                # Store source metadata
                existing_meta = node.node_metadata or {}
                if isinstance(existing_meta, str):
                    try:
                        existing_meta = json.loads(existing_meta)
                    except Exception:
                        existing_meta = {}
                existing_meta["source"] = "TakeUForward"
                existing_meta["striver_catalog_id"] = match["id"]
                node.node_metadata = existing_meta

                self.matched_nodes += 1
                if len(possible) > 1:
                    self.duplicate_matches += 1
            else:
                # Assign default fallback Striver DSA video so every node has a working video
                fallback_url = DEFAULT_STRIVER_VIDEO["youtube_url"]
                fallback_id = DEFAULT_STRIVER_VIDEO["video_id"]
                fallback_thumb = generate_thumbnail_url(fallback_id)

                node.youtube_url = fallback_url
                node.youtube_video_id = fallback_id
                node.thumbnail_url = fallback_thumb

                existing_meta = node.node_metadata or {}
                if isinstance(existing_meta, str):
                    try:
                        existing_meta = json.loads(existing_meta)
                    except Exception:
                        existing_meta = {}
                existing_meta["source"] = "TakeUForward"
                existing_meta["is_fallback"] = True
                node.node_metadata = existing_meta

                self.unmatched_nodes += 1
                self.missing_videos += 1
                self.unmatched_records.append({
                    "node_id": node.id,
                    "title": node.title,
                    "type": node.type,
                    "reason": "No exact or fuzzy match found in catalog (assigned default Striver video fallback)",
                    "possible_matches": possible
                })

        self.db.commit()

        # Write unmatched_nodes.json report
        self.export_unmatched_json()

        # Return summary dictionary
        summary = {
            "total_nodes": self.total_nodes,
            "matched_nodes": self.matched_nodes,
            "unmatched_nodes": self.unmatched_nodes,
            "duplicate_matches": self.duplicate_matches,
            "invalid_urls": self.invalid_urls,
            "missing_videos": self.missing_videos,
            "json_report_path": self.output_json_path
        }

        self.print_report(summary)
        return summary

    def export_unmatched_json(self):
        """Exports unmatched node records to JSON file."""
        try:
            with open(self.output_json_path, "w", encoding="utf-8") as f:
                json.dump(self.unmatched_records, f, indent=2)
            logger.info(f"Exported unmatched nodes report to: {self.output_json_path}")
        except Exception as e:
            logger.error(f"Failed to export unmatched nodes JSON: {e}")

    def print_report(self, summary: Dict[str, Any]):
        """Prints a clean, formatted report to stdout."""
        print("\n" + "=" * 60)
        print("        OFFICIAL STRIVER A2Z VIDEO IMPORT REPORT        ")
        print("=" * 60)
        print(f" Total Roadmap Nodes Processed : {summary['total_nodes']}")
        print(f" Matched Topic Nodes          : {summary['matched_nodes']}")
        print(f" Unmatched / Container Nodes   : {summary['unmatched_nodes']}")
        print(f" Duplicate Candidates Found    : {summary['duplicate_matches']}")
        print(f" Invalid URLs Detected         : {summary['invalid_urls']}")
        print(f" Missing Videos (Fallback Used): {summary['missing_videos']}")
        print(f" JSON Unmatched Report Location: {summary['json_report_path']}")
        print("=" * 60 + "\n")
