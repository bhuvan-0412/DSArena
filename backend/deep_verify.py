"""Deep verify: check video IDs match expected Excel entries for key nodes."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal
from app.models.roadmap import RoadmapNode

# Expected: node_title -> expected_video_id (from Excel)
EXPECTED = {
    "User Input / Output":            "h3uDCJ5mvgw",   # S.No 2
    "Data Types":                     "EAR7De6Goz4",   # S.No 3
    "If Else Statements":             "EAR7De6Goz4",   # S.No 3
    "Switch Statement":               "EAR7De6Goz4",   # S.No 3
    "Time & Space Complexity":        "FPu9Uld7W-E",   # S.No 4
    "Pattern Problems":               "tNm_NNSB3_w",   # S.No 5
    "C++ STL / Java Collections":     "RRVYpIET_RU",   # S.No 6
    "Count Digits":                   "1xNbjMdbjug",   # S.No 7
    "GCD or HCF":                     "1xNbjMdbjug",   # S.No 7
    "Armstrong Number":               "1xNbjMdbjug",   # S.No 7
    "Prime Numbers":                  "1xNbjMdbjug",   # S.No 7
    "Selection Sort":                 "HGk_ypEuS24",   # S.No 14
    "Merge Sort":                     "ogjf7ORKfd8",   # S.No 15
    "Quick Sort":                     "WIrA4YexLRQ",   # S.No 16
    "Two Sum":                        "UXDSeD9mN-k",   # S.No 21
    "Binary Search":                  "MHf6awe89xw",   # S.No 45
    "Koko Eating Bananas":            "qyfekrNni90",   # S.No 56
    "Aggressive Cows":                "R_Mfw4ew-Vo",   # S.No 61
    "Median of Two Sorted Arrays":    "C2rRzz-JDk8",   # S.No 65
}

db = SessionLocal()
nodes = {n.title: n for n in db.query(RoadmapNode).all()}

print("\n=== VIDEO ID VERIFICATION ===\n")
all_ok = True
for title, expected_id in EXPECTED.items():
    node = nodes.get(title)
    if not node:
        print(f"  [MISSING] Node '{title}' not found in DB")
        all_ok = False
        continue
    actual_id = node.youtube_video_id or ""
    status = "OK" if actual_id == expected_id else "MISMATCH"
    if status == "MISMATCH":
        all_ok = False
    meta = node.node_metadata or {}
    src  = meta.get("source","?") if isinstance(meta,dict) else "?"
    tier = meta.get("match_tier","?") if isinstance(meta,dict) else "?"
    print(f"  [{status}] {title}")
    print(f"         Expected: {expected_id}")
    print(f"         Actual  : {actual_id}  (T{tier}, src={src})")
    print()

print("=" * 50)
print(f"All correct: {all_ok}")
db.close()
