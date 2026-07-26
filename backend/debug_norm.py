"""Debug normalisation for problem nodes."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
STOP_WORDS = {
    "strivers", "striver", "a2z", "dsa", "course", "playlist", "data",
    "structure", "structures", "algorithm", "algorithms", "lecture",
    "for", "in", "the", "a", "an", "and", "or", "to", "of", "with",
    "on", "by", "is", "it", "all", "using", "how", "part", "shot",
    "learn", "introduction", "intro", "basics", "basic", "complete",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "brute", "better", "optimal", "naive", "force", "approach",
    "approaches", "multiple", "video", "explained", "explanation",
    "notes", "time", "complexity", "space", "update", "series",
    "g", "re", "l", "dp",
}

def normalise(text):
    if not text: return ""
    noise = [
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
        r"\(.*?\)",
    ]
    cleaned = text.lower()
    for pat in noise:
        cleaned = re.sub(pat, " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    tokens = [t for t in cleaned.split() if t not in STOP_WORDS and len(t) > 1]
    return " ".join(tokens)

tests = [
    "Data Types",
    "If Else Statements",
    "Time & Space Complexity",
    "Loops Basics",
    "Functions Basics",
    "Arrays & Strings Basics",
    "Find Row with Max 1s",
    "Count substrings with K distinct characters",
]

for t in tests:
    n = normalise(t)
    print(f"  '{t}' -> '{n}'")
