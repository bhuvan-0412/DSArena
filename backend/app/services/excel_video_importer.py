"""
excel_video_importer.py
-----------------------
Populates RoadmapNode rows with YouTube video data sourced exclusively from
the Striver A2Z Excel file (Striver_A2Z_Playlist_Links.xlsx).

Architecture
------------
* Reads the Excel file, auto-detects columns, validates every row.
* Runs a 4-tier matching engine against every roadmap node:
    Tier 1 – Exact normalised title match
    Tier 2 – DSA keyword extraction + keyword-in-title search
    Tier 3 – Known alias / compound-video mapping table
    Tier 4 – Jaccard + overlap fuzzy scoring (threshold 0.40)
* Updates youtube_url / youtube_video_id / thumbnail_url / node_metadata.
* Generates unmatched_nodes.json and a printed summary report.
* Is fully re-runnable; skips already-linked nodes unless --force.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from app.models.roadmap import RoadmapNode

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ExcelVideoImporter")

SOURCE_TAG = "Striver A2Z Excel"

# ─────────────────────────────────────────────────────────────────────────────
# Known column name variants (case-insensitive)
# ─────────────────────────────────────────────────────────────────────────────
_COL_ALIASES: Dict[str, List[str]] = {
    "sno":       ["s.no", "sno", "sr", "sr.", "no", "#", "serial", "serial number"],
    "title":     ["title", "video title", "name", "lesson", "topic"],
    "video_url": ["video url", "url", "link", "youtube url", "youtube link", "video link"],
    "video_id":  ["video id", "videoid", "id", "youtube id"],
}

# ─────────────────────────────────────────────────────────────────────────────
# Stop-words stripped from titles before matching
# ─────────────────────────────────────────────────────────────────────────────
_STOP_WORDS: Set[str] = {
    "strivers", "striver", "a2z", "course", "playlist",
    "lecture", "for", "in", "the", "a", "an", "and", "or", "to", "of", "with",
    "on", "by", "is", "it", "all", "using", "how", "part", "shot",
    "learn", "introduction", "intro", "basics", "basic", "complete",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "brute", "better", "optimal", "naive", "force", "approach",
    "approaches", "multiple", "video", "explained", "explanation",
    "notes", "update", "series",
    "g", "re", "l", "dp",                         # prefix labels
}

# ─────────────────────────────────────────────────────────────────────────────
# Compound-video alias table
# Maps (roadmap node title normalised keywords) → preferred Excel S.No values
# A node can match multiple Excel S.No entries; the best is chosen by score.
# Values are Excel 1-based S.No integers.
# ─────────────────────────────────────────────────────────────────────────────
# Each entry: "node_keyword_substring": [list_of_excel_snos_to_try_first]
# The matcher will bias toward these rows when keywords match.
# S.No values verified against Striver_A2Z_Playlist_Links.xlsx
COMPOUND_MAP: Dict[str, List[int]] = {
    # ── Step 1: Learn the Basics ──────────────────────────────────────────
    # S.No 2: VS code setup | Input / Output
    "user input output":              [2],
    "input output":                   [2],
    # S.No 3: C++ Basics in One Shot (covers: data types, if-else, switch, arrays, loops, functions)
    "data types":                     [3],   # "Data Types" -- must point to C++ Basics, not Trees
    "variables types":                [3],
    "primitive data":                 [3],
    "if else":                        [3],
    "switch statement":               [3],
    "switch case":                    [3],
    "arrays strings":                 [3],   # "Arrays & Strings Basics"
    "arrays strings basics":          [3],
    "loops":                          [3],   # "Loops Basics"
    "loops basics":                   [3],
    "functions":                      [3],   # "Functions Basics"
    "functions basics":               [3],
    # S.No 4: Time and Space Complexity
    # NOTE: 'Time & Space Complexity' normalises to '' (all stop words) — handled specially below
    "time space complexity":          [4],
    "time complexity":                [4],
    "space complexity":               [4],   # "Time & Space Complexity"
    # S.No 5: Pattern Problems
    "pattern problems":               [5],
    "pattern":                        [5],
    # S.No 6: C++ STL
    "stl":                            [6],
    "collections":                    [6],
    "cpp stl":                        [6],
    # S.No 7: Basic Maths (covers: count digits, reverse, palindrome, gcd/hcf, armstrong, divisors, prime)
    "count digits":                   [7],
    "reverse number":                 [7],
    "palindrome number":              [7],
    "gcd":                            [7],
    "hcf":                            [7],
    "armstrong":                      [7],
    "divisors":                       [7],
    "prime numbers":                  [7],
    "prime":                          [7],
    # S.No 8-12: Recursion series
    "print name":                     [8],
    "introduction recursion":         [8],
    "print 1 to n":                   [9],
    "print n to 1":                   [9],
    "problems on recursion":          [9],
    "sum of n":                       [10],
    "factorial":                      [10],
    "parameterised functional":       [10],
    "reverse array":                  [11],
    "check palindrome":               [11],
    "fibonacci":                      [12],
    "multiple recursion":             [12],
    # S.No 13: Hashing | Maps
    "number hashing":                 [13],
    "character hashing":              [13],
    "frequency count":                [13],
    "hashing maps":                   [13],
    # ── Step 2: Sorting ───────────────────────────────────────────────────
    # S.No 14: Sorting Part 1 (Selection, Bubble, Insertion + Recursive variants)
    "selection sort":                 [14],
    "bubble sort":                    [14],
    "insertion sort":                 [14],
    "recursive bubble sort":          [14],
    "recursive insertion sort":       [14],
    # S.No 15: Merge Sort
    "merge sort":                     [15],
    # S.No 16: Quick Sort
    "quick sort":                     [16],
    # ── Step 3: Arrays ────────────────────────────────────────────────────
    # S.No 17: Second Largest, Remove Duplicates
    "largest element":                [17],
    "second largest":                 [17],
    "remove duplicates":              [17],
    # S.No 18: Rotate Array, Union/Intersection, Move Zeros, Linear Search
    "check if sorted":                [18],  # "Check if Array is Sorted"
    "check sorted":                   [18],
    "check array sorted":             [18],
    "left rotate":                    [18],
    "move zeros":                     [18],
    "find union":                     [18],
    "linear search":                  [18],
    # S.No 19: Find element once, missing number, max consecutive ones
    "find missing number":            [19],
    "maximum consecutive ones":       [19],
    "find number appears once":       [19],
    "single number":                  [19],
    # S.No 20: Longest Subarray sum K
    "longest subarray sum k":         [20],
    "subarray sum k":                 [20],
    # S.No 21: 2 Sum Problem
    "two sum":                        [21],
    # S.No 22: Sort 0s 1s 2s
    "sort 0s 1s 2s":                  [22],
    # S.No 23: Majority Element (>N/2)
    "majority element n 2":           [23],
    # S.No 24: Kadane's Algorithm
    "kadane":                         [24],
    "max subarray":                   [24],
    # S.No 25: DP 35 - Best Time to Buy/Sell (used as print subarray max sum fallback)
    "print subarray max sum":         [25],
    # S.No 26: Rearrange Array by Sign
    "buy sell stock":                 [26],
    "rearrange array":                [26],
    # S.No 27: Next Permutation
    "next permutation":               [27],
    # S.No 28: Leaders in Array
    "leaders in array":               [28],
    # S.No 29: Longest Consecutive Sequence
    "longest consecutive":            [29],
    # S.No 30: Set Matrix Zeroes
    "set matrix zeros":               [30],
    # S.No 31: Rotate Matrix 90 Degrees
    "rotate matrix":                  [31],
    # S.No 32: Spiral Matrix
    "spiral matrix":                  [32],
    # S.No 33: Count Subarray sum equals K
    "subarray sum equals k":          [33],
    # S.No 34: Pascal's Triangle
    "pascal triangle":                [34],
    # S.No 35: Majority Element II (>N/3)
    "majority element n 3":           [35],
    # S.No 36: 3 Sum
    "three sum":                      [36],
    # S.No 37: 4 Sum
    "four sum":                       [37],
    # S.No 38: Subarrays with XOR K
    "subarrays xor k":                [38],
    "longest subarray zero sum":      [39],
    # S.No 39: Merge Overlapping Intervals
    "merge overlapping":              [39],
    "merge intervals":                [39],
    # S.No 40: Merge Sorted Arrays Without Extra Space
    "merge sorted arrays":            [40],
    # S.No 41: Find Missing and Repeating
    "find missing repeating":         [41],
    # S.No 42: Count Inversions
    "count inversions":               [42],
    # S.No 43: Reverse Pairs
    "reverse pairs":                  [43],
    # S.No 44: Maximum Product Subarray
    "maximum product subarray":       [44],
    # ── Step 4: Binary Search ─────────────────────────────────────────────
    # S.No 45: BS-1 Binary Search Introduction
    "binary search":                  [45],
    # S.No 46: BS-2 Lower/Upper Bound, Search Insert, Floor/Ceil
    "lower upper bound":              [46],
    "search insert position":         [46],
    "floor ceil sorted":              [46],
    # S.No 47: BS-3 First/Last Occurrences, Count Occurrences
    "first last occurrences":         [47],
    "count occurrences":              [47],
    # S.No 48-49: BS-4/5 Search in Rotated Sorted Array I/II
    "search rotated":                 [48, 49],
    # S.No 50: BS-6 Minimum in Rotated Sorted Array
    "find minimum rotated":           [50],
    # S.No 51: BS-7 Find rotation count
    "find rotation count":            [51],
    # S.No 52: BS-8 Single Element in Sorted Array
    "single element sorted":          [52],
    # S.No 53: BS-9 Find Peak Element
    "find peak element":              [53],
    # S.No 54: BS-10 Square Root
    "square root":                    [54],
    # S.No 55: BS-11 Nth Root
    "nth root":                       [55],
    # S.No 56: BS-12 Koko Eating Bananas
    "koko eating":                    [56],
    # S.No 57: BS-13 Minimum days to make M bouquets
    "minimum days bouquets":          [57],
    # S.No 58: BS-14 Smallest Divisor
    "smallest divisor":               [58],
    # S.No 59: BS-15 Capacity to Ship Packages
    "capacity ship packages":         [59],
    # S.No 60: BS-16 Kth Missing Positive
    "kth missing positive":           [60],
    # S.No 61: BS-17 Aggressive Cows
    "aggressive cows":                [61],
    # S.No 62: BS-18 Book Allocation
    "book allocation":                [62],
    # S.No 63: BS-19 Painter's Partition + Split Array Largest Sum
    "split array largest sum":        [63],
    "painters partition":             [63],
    # S.No 64: BS-20 Minimise Max Distance to Gas Stations
    "minimise max distance gas":      [64],
    "minimize max distance":          [64],
    # S.No 65-66: BS-21 Median of two Sorted Arrays
    "median two sorted":              [65, 66],
    # S.No 67: BS-22 K-th Element of Two Sorted Arrays
    "kth element two sorted":         [67],
    # S.No 68: BS-23 Row with max 1s  -- "Find Row with Max 1s" -> norm='find row max 1s'
    "find row max ones":              [68],
    "find row max 1s":                [68],   # actual normalised key
    "row max ones":                   [68],
    "row max 1s":                     [68],   # actual normalised key
    "row maximum ones":               [68],
    "row with max":                   [68],
    # S.No 69: BS-24 Search in 2D Matrix I
    "search 2d matrix":               [69, 70],
    # S.No 71: BS-26 Find Peak Element in 2D
    "find peak element 2d":           [71],
    # S.No 72: BS-27 Median in Row-wise Sorted Matrix
    "median matrix":                  [72],
    # Step 5: Strings
    "count substrings k distinct":    [277],
    "count substrings distinct":      [277],
    "count substrings with k distinct": [277],
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _normalise(text: Optional[str]) -> str:
    """Lowercase, strip punctuation, remove stop-words, collapse whitespace."""
    if not text:
        return ""
    # Strip YouTube-specific noise from playlist titles
    noise_patterns = [
        r"\|\s*strivers?\s+a2z\s+dsa\s+course",
        r"-\s*strivers?\s+a2z\s+dsa\s+course",
        r"strivers?\s+a2z\s+dsa\s+course",
        r"\|\s*strivers?\s+a2z",
        r"-\s*strivers?\s+a2z",
        r"strivers?\s+a2z",
        r"\|\s*dsa\s+course",
        r"-\s*dsa\s+course",
        r"\|\s*playlist",
        r"in one shot",
        r"one shot",
        r"\d+\s+problems\s+in\s+\d+",
        r"part[-\s]*\d+",
        r"\(.*?\)",   # parenthetical content
    ]
    cleaned = text.lower()
    for pat in noise_patterns:
        cleaned = re.sub(pat, " ", cleaned, flags=re.IGNORECASE)
    # Remove non-alphanumeric (keep spaces)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    # Remove stop-words
    tokens = [t for t in cleaned.split() if t not in _STOP_WORDS and len(t) > 1]
    return " ".join(tokens)


def _extract_video_id(url: Optional[str]) -> Optional[str]:
    """Extract 11-char YouTube video ID from any known URL format."""
    if not url:
        return None
    patterns = [
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"[?&]v=([a-zA-Z0-9_-]{11})",
        r"youtube\.com/embed/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def _thumbnail(video_id: Optional[str]) -> Optional[str]:
    if not video_id:
        return None
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


def _is_valid_video_id(vid: Optional[str]) -> bool:
    if not vid:
        return False
    return bool(re.match(r"^[a-zA-Z0-9_-]{11}$", vid))


def _token_similarity(a: str, b: str) -> float:
    """Jaccard + overlap blend for two normalised strings."""
    sa = set(a.split())
    sb = set(b.split())
    if not sa or not sb:
        return 0.0
    inter = sa & sb
    if not inter:
        return 0.0
    jaccard = len(inter) / len(sa | sb)
    overlap = len(inter) / min(len(sa), len(sb))
    return 0.6 * jaccard + 0.4 * overlap


# ─────────────────────────────────────────────────────────────────────────────
# Excel Loader
# ─────────────────────────────────────────────────────────────────────────────

class ExcelRow:
    __slots__ = ("sno", "title", "video_url", "video_id",
                 "norm_title", "is_valid")

    def __init__(self, sno: int, title: str, video_url: str, video_id: str):
        self.sno       = sno
        self.title     = title.strip() if isinstance(title, str) else str(title)
        self.video_url = video_url.strip() if isinstance(video_url, str) else str(video_url)
        self.video_id  = video_id.strip() if isinstance(video_id, str) else str(video_id)
        self.norm_title = _normalise(self.title)
        self.is_valid  = _is_valid_video_id(self.video_id)


def _detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Return a mapping of logical key → actual DataFrame column name."""
    result: Dict[str, str] = {}
    cols_lower = {c.strip().lower(): c for c in df.columns}
    for key, aliases in _COL_ALIASES.items():
        for alias in aliases:
            if alias in cols_lower:
                result[key] = cols_lower[alias]
                break
    return result


def load_excel(path: str) -> List[ExcelRow]:
    """Load and validate all sheets from the Excel file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Excel file not found: {path}")

    rows: List[ExcelRow] = []
    xl = pd.ExcelFile(path)

    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name)
        col_map = _detect_columns(df)

        if "video_url" not in col_map and "video_id" not in col_map:
            logger.warning(f"Sheet '{sheet_name}' has no URL/ID columns — skipping.")
            continue

        for idx, row in df.iterrows():
            try:
                sno        = int(row[col_map["sno"]]) if "sno" in col_map else idx + 1
                title      = str(row[col_map["title"]]) if "title" in col_map else ""
                video_url  = str(row[col_map["video_url"]]) if "video_url" in col_map else ""
                video_id   = str(row[col_map["video_id"]]) if "video_id" in col_map else ""

                # If video_id missing, try to extract from URL
                if not _is_valid_video_id(video_id) and video_url:
                    extracted = _extract_video_id(video_url)
                    if extracted:
                        video_id = extracted

                excel_row = ExcelRow(sno, title, video_url, video_id)

                if not excel_row.is_valid:
                    logger.warning(
                        f"Row {sno} ('{title[:60]}') — invalid video ID '{video_id}' — skipping."
                    )
                    continue

                rows.append(excel_row)

            except Exception as exc:
                logger.warning(f"Row {idx} parse error in sheet '{sheet_name}': {exc}")

    logger.info(f"Loaded {len(rows)} valid Excel rows from {len(xl.sheet_names)} sheet(s).")
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Matching Engine
# ─────────────────────────────────────────────────────────────────────────────

class MatchResult:
    __slots__ = ("excel_row", "score", "tier", "note")

    def __init__(self, excel_row: ExcelRow, score: float, tier: int, note: str = ""):
        self.excel_row = excel_row
        self.score     = score
        self.tier      = tier
        self.note      = note

    def __repr__(self) -> str:
        return (
            f"<Match tier={self.tier} score={self.score:.2f} "
            f"id={self.excel_row.video_id} title='{self.excel_row.title[:50]}'>"
        )


def _tier1_exact(norm_node: str, rows: List[ExcelRow]) -> Optional[MatchResult]:
    """Exact normalised-title match."""
    for r in rows:
        if norm_node == r.norm_title and norm_node:
            return MatchResult(r, 1.0, 1, "exact normalised match")
    return None


def _tier2_compound(norm_node: str, rows: List[ExcelRow],
                    sno_index: Dict[int, ExcelRow]) -> Optional[MatchResult]:
    """Compound-video alias lookup (ordered by key length descending for specificity)."""
    sorted_map = sorted(COMPOUND_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    for keyword, snos in sorted_map:
        # keyword must appear as a contiguous subsequence in the node norm title
        if keyword in norm_node:
            for sno in snos:
                if sno in sno_index:
                    r = sno_index[sno]
                    if r.is_valid:
                        return MatchResult(r, 0.95, 2,
                                           f"compound map '{keyword}' → S.No {sno}")
    return None


def _tier3_keyword(norm_node: str, rows: List[ExcelRow]) -> Optional[MatchResult]:
    """All node keywords must appear in the Excel title."""
    node_tokens = set(norm_node.split())
    if not node_tokens:
        return None

    best: Optional[MatchResult] = None
    for r in rows:
        excel_tokens = set(r.norm_title.split())
        if not excel_tokens:
            continue
        # All short node tokens found in the longer excel title
        if len(node_tokens) >= 1 and node_tokens.issubset(excel_tokens):
            score = len(node_tokens) / max(len(excel_tokens), 1)
            if best is None or score > best.score:
                best = MatchResult(r, score, 3, "all node keywords in excel title")

    return best


def _tier4_fuzzy(norm_node: str, rows: List[ExcelRow],
                 threshold: float = 0.40) -> Optional[MatchResult]:
    """Jaccard + overlap fuzzy score."""
    best: Optional[MatchResult] = None
    best_score = threshold

    for r in rows:
        score = _token_similarity(norm_node, r.norm_title)
        if score >= best_score:
            best_score = score
            best = MatchResult(r, score, 4, f"fuzzy score={score:.2f}")

    return best


def find_best_match(node: RoadmapNode, rows: List[ExcelRow],
                    sno_index: Dict[int, ExcelRow]) -> Optional[MatchResult]:
    """Run the 4-tier matching pipeline for a single roadmap node."""
    norm_node = _normalise(node.title)

    # Special case: if normalisation produces an empty string (all stop-words),
    # fall back to raw-title-substring compound lookup
    if not norm_node:
        title_lower = node.title.lower().replace("&", "and").replace("/", " ")
        title_lower = re.sub(r"[^a-z0-9\s]", " ", title_lower).strip()
        sorted_map = sorted(COMPOUND_MAP.items(), key=lambda x: len(x[0]), reverse=True)
        for keyword, snos in sorted_map:
            if keyword in title_lower:
                for sno in snos:
                    if sno in sno_index and sno_index[sno].is_valid:
                        r = sno_index[sno]
                        return MatchResult(r, 0.90, 2,
                                           f"raw-title compound '{keyword}' → S.No {sno}")
        return None

    result = (
        _tier1_exact(norm_node, rows)
        or _tier2_compound(norm_node, rows, sno_index)
        or _tier3_keyword(norm_node, rows)
        or _tier4_fuzzy(norm_node, rows)
    )

    # Prevent cross-domain false positives (e.g. String node matching Binary Tree video)
    if result:
        title_lower = node.title.lower()
        matched_title = result.excel_row.title.lower()
        if ("string" in title_lower or "parenthes" in title_lower) and (
            "binary tree" in matched_title or "traversal" in matched_title or "l4." in matched_title or "l5." in matched_title or "l6." in matched_title or "l7." in matched_title
        ):
            return None

    return result



# ─────────────────────────────────────────────────────────────────────────────
# Top-3 closest matches (for unmatched report)
# ─────────────────────────────────────────────────────────────────────────────

def top3_matches(norm_node: str, rows: List[ExcelRow]) -> List[str]:
    scored = [(r.title, _token_similarity(norm_node, r.norm_title)) for r in rows]
    scored.sort(key=lambda x: -x[1])
    return [f"{t} (score={s:.2f})" for t, s in scored[:3]]


# ─────────────────────────────────────────────────────────────────────────────
# Main Importer Class
# ─────────────────────────────────────────────────────────────────────────────

class ExcelVideoImporter:
    """
    Reads the Striver A2Z Excel playlist and populates roadmap node
    YouTube fields using intelligent multi-tier matching.
    """

    def __init__(
        self,
        db: Session,
        excel_path: str,
        force: bool = False,
        output_json_path: str = "unmatched_nodes.json",
    ):
        self.db               = db
        self.excel_path       = excel_path
        self.force            = force
        self.output_json_path = output_json_path

        # Counters
        self.total_nodes     = 0
        self.total_excel     = 0
        self.matched         = 0
        self.already_linked  = 0
        self.updated         = 0
        self.skipped_invalid = 0
        self.skipped_container = 0
        self.unmatched       = 0
        self.duplicate_links = 0   # same video ID assigned to 2+ nodes

        self.unmatched_records: List[Dict[str, Any]] = []
        # Track which video IDs have been assigned to detect duplicates
        self._assigned_video_ids: Dict[str, str] = {}  # video_id -> node_id

    # ────────────────────────────────────────────────────────────
    # Public entry point
    # ────────────────────────────────────────────────────────────

    def run_import(self) -> Dict[str, Any]:
        logger.info("=" * 60)
        logger.info("  ExcelVideoImporter — Striver A2Z DSA Playlist")
        logger.info("=" * 60)

        # 1. Load Excel
        excel_rows = load_excel(self.excel_path)
        self.total_excel = len(excel_rows)
        if not excel_rows:
            raise ValueError("No valid rows loaded from Excel file.")

        # Build S.No index for compound-map fast lookup
        sno_index: Dict[int, ExcelRow] = {r.sno: r for r in excel_rows}

        # 2. Fetch all roadmap nodes
        all_nodes: List[RoadmapNode] = self.db.query(RoadmapNode).all()
        self.total_nodes = len(all_nodes)
        logger.info(f"Fetched {self.total_nodes} roadmap nodes from DB.")

        # 3. Match each node
        for node in all_nodes:
            self._process_node(node, excel_rows, sno_index)

        # 4. Persist
        self.db.commit()
        logger.info("Database commit successful.")

        # 5. Write JSON report
        self._export_unmatched_json()

        # 6. Print summary
        summary = self._build_summary()
        self._print_report(summary)
        return summary

    # ────────────────────────────────────────────────────────────
    # Per-node processing
    # ────────────────────────────────────────────────────────────

    def _process_node(
        self,
        node: RoadmapNode,
        rows: List[ExcelRow],
        sno_index: Dict[int, ExcelRow],
    ) -> None:
        # Container nodes (step / section) don't have their own video
        if node.type in ("step", "section"):
            self.skipped_container += 1
            return

        # Already linked — skip unless forced
        if node.youtube_url and not self.force:
            existing_id = node.youtube_video_id or _extract_video_id(node.youtube_url)
            if _is_valid_video_id(existing_id):
                self.already_linked += 1
                logger.debug(f"[SKIP] '{node.title}' already has video {existing_id}")
                return

        # Run matching
        match = find_best_match(node, rows, sno_index)

        if match is None:
            self.unmatched += 1
            norm_node = _normalise(node.title)
            self.unmatched_records.append({
                "node_id":         node.id,
                "title":           node.title,
                "type":            node.type,
                "reason":          "No match found across all 4 tiers",
                "closest_matches": top3_matches(norm_node, rows),
            })
            logger.warning(f"[UNMATCHED] '{node.title}' (type={node.type})")
            return

        ex = match.excel_row
        vid = ex.video_id

        # Track duplicate assignments
        if vid in self._assigned_video_ids and self._assigned_video_ids[vid] != node.id:
            self.duplicate_links += 1
            logger.info(
                f"[DUPLICATE VIDEO] '{vid}' assigned to both "
                f"'{self._assigned_video_ids[vid]}' and '{node.id}' — allowed."
            )
        self._assigned_video_ids[vid] = node.id

        # Write to DB
        node.youtube_url      = ex.video_url
        node.youtube_video_id = vid
        node.thumbnail_url    = _thumbnail(vid)

        existing_meta = node.node_metadata or {}
        if isinstance(existing_meta, str):
            try:
                existing_meta = json.loads(existing_meta)
            except Exception:
                existing_meta = {}
        existing_meta["source"]            = SOURCE_TAG
        existing_meta["excel_sno"]         = ex.sno
        existing_meta["excel_title"]       = ex.title
        existing_meta["match_tier"]        = match.tier
        existing_meta["match_score"]       = round(match.score, 3)
        existing_meta["match_note"]        = match.note
        node.node_metadata = existing_meta

        self.matched += 1
        self.updated += 1
        logger.info(
            f"[MATCH T{match.tier}] '{node.title}' "
            f"→ '{ex.title[:55]}' | ID={vid} | score={match.score:.2f}"
        )

    # ────────────────────────────────────────────────────────────
    # Reporting
    # ────────────────────────────────────────────────────────────

    def _export_unmatched_json(self) -> None:
        try:
            with open(self.output_json_path, "w", encoding="utf-8") as fh:
                json.dump(self.unmatched_records, fh, indent=2, ensure_ascii=False)
            logger.info(f"Unmatched nodes report → {self.output_json_path}")
        except Exception as exc:
            logger.error(f"Failed to write unmatched JSON: {exc}")

    def _build_summary(self) -> Dict[str, Any]:
        matchable = self.total_nodes - self.skipped_container
        total_matched = self.updated + self.already_linked
        match_pct = (
            round(total_matched / matchable * 100, 1) if matchable else 0.0
        )
        return {
            "total_roadmap_nodes":   self.total_nodes,
            "container_nodes":       self.skipped_container,
            "matchable_nodes":       matchable,
            "excel_rows":            self.total_excel,
            "total_matched":         total_matched,
            "updated_in_db":         self.updated,
            "already_linked":        self.already_linked,
            "unmatched":             self.unmatched,
            "duplicate_video_links": self.duplicate_links,
            "match_percentage":      match_pct,
            "json_report":           self.output_json_path,
        }

    def _print_report(self, s: Dict[str, Any]) -> None:
        lines = [
            "",
            "=" * 62,
            "   STRIVER A2Z EXCEL VIDEO IMPORT -- FINAL REPORT   ",
            "=" * 62,
            f"  Excel File Rows            : {s['excel_rows']}",
            f"  Total Roadmap Nodes        : {s['total_roadmap_nodes']}",
            f"  Container (step/section)   : {s['container_nodes']}",
            f"  Matchable Nodes            : {s['matchable_nodes']}",
            "-" * 62,
            f"  [OK] Matched & Updated     : {s['updated_in_db']}",
            f"  [OK] Already Linked (skip) : {s['already_linked']}",
            f"  [OK] Total Matched Nodes   : {s['total_matched']}",
            f"  [!!] Unmatched             : {s['unmatched']}",
            f"  [i]  Duplicate Video Links : {s['duplicate_video_links']}",
            "-" * 62,
            f"  Match Percentage           : {s['match_percentage']}%",
            f"  JSON Report                : {s['json_report']}",
            "=" * 62,
            "",
        ]
        for line in lines:
            # Use errors='replace' to avoid codec issues on Windows consoles
            try:
                print(line)
            except UnicodeEncodeError:
                print(line.encode("ascii", errors="replace").decode("ascii"))
