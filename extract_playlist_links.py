"""
extract_playlist_links.py
--------------------------
Extracts all video metadata from a YouTube playlist using yt-dlp,
stores it in a pandas DataFrame, and exports to an Excel file with
auto-adjusted column widths.
"""

import subprocess
import sys
import json
import os
import warnings


# ──────────────────────────────────────────────
# Step 1: Ensure required packages are installed
# ──────────────────────────────────────────────
def ensure_package(package: str) -> None:
    """Install a package via pip if it is not already importable."""
    try:
        __import__(package)
        print(f"  [OK] {package} is already installed.")
    except ImportError:
        print(f"  [INFO] {package} not found – installing …")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"  [OK] {package} installed successfully.")


print("=" * 60)
print("Checking / installing required packages …")
print("=" * 60)
ensure_package("yt_dlp")   # importable name differs from pip name
ensure_package("pandas")
ensure_package("openpyxl")

import pandas as pd  # noqa: E402  (import after install check)

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLgUwDviBIf0oF6QL8m22w1hIDC1vJ_BHz"
OUTPUT_FILE  = os.path.join(os.getcwd(), "Striver_A2Z_Playlist_Links.xlsx")


# ──────────────────────────────────────────────
# Step 2: Fetch playlist metadata via yt-dlp
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("Fetching playlist metadata with yt-dlp …")
print("(This may take a minute – please wait)")
print("=" * 60)

cmd = [
    sys.executable, "-m", "yt_dlp",
    "--flat-playlist",
    "--dump-json",
    "--no-warnings",
    PLAYLIST_URL,
]

try:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=600,          # 10-minute hard timeout
    )
except subprocess.TimeoutExpired:
    print("[ERROR] yt-dlp timed out after 10 minutes. Exiting.")
    sys.exit(1)

raw_output = result.stdout.strip()

if not raw_output:
    print("[ERROR] yt-dlp produced no output.")
    if result.stderr:
        print("stderr:", result.stderr[:500])
    sys.exit(1)


# ──────────────────────────────────────────────
# Step 3: Parse JSON output line-by-line
# ──────────────────────────────────────────────
print("\nParsing video metadata …")

rows        = []
serial_no   = 0   # tracks successfully parsed entries
skipped     = 0

for line_num, line in enumerate(raw_output.splitlines(), start=1):
    line = line.strip()
    if not line:
        continue

    serial_no += 1  # increment before try so warning shows correct position

    try:
        data = json.loads(line)
    except json.JSONDecodeError as exc:
        warnings.warn(
            f"[WARNING] Skipping entry at position {serial_no} – "
            f"JSON decode error: {exc}"
        )
        skipped += 1
        serial_no -= 1  # don't count this slot
        continue

    try:
        video_id  = data.get("id", "")
        title     = data.get("title", "Untitled")
        video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else ""

        if not video_id:
            warnings.warn(
                f"[WARNING] Entry at position {serial_no} has no video ID – skipping."
            )
            skipped += 1
            serial_no -= 1
            continue

        rows.append({
            "S.No":      serial_no,
            "Title":     title,
            "Video URL": video_url,
            "Video ID":  video_id,
        })

    except Exception as exc:  # noqa: BLE001
        warnings.warn(
            f"[WARNING] Skipping entry at position {serial_no} – "
            f"unexpected error: {exc}"
        )
        skipped += 1
        serial_no -= 1

print(f"  Parsed {len(rows)} videos  |  Skipped {skipped} entries.")


# ──────────────────────────────────────────────
# Step 4: Build pandas DataFrame
# ──────────────────────────────────────────────
df = pd.DataFrame(rows, columns=["S.No", "Title", "Video URL", "Video ID"])


# ──────────────────────────────────────────────
# Step 5: Export to Excel with auto-adjusted column widths
# ──────────────────────────────────────────────
print("\nExporting to Excel …")

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Playlist")

    # Auto-adjust column widths
    worksheet = writer.sheets["Playlist"]
    for col_cells in worksheet.columns:
        max_len = 0
        col_letter = col_cells[0].column_letter
        for cell in col_cells:
            try:
                cell_len = len(str(cell.value)) if cell.value is not None else 0
                max_len = max(max_len, cell_len)
            except Exception:
                pass
        # Add a small padding; cap at 80 to avoid absurdly wide columns
        adjusted_width = min(max_len + 4, 80)
        worksheet.column_dimensions[col_letter].width = adjusted_width


# ──────────────────────────────────────────────
# Step 6: Print summary
# ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("DONE!")
print(f"  Total videos extracted : {len(df)}")
print(f"  Entries skipped        : {skipped}")
print(f"  Output file            : {OUTPUT_FILE}")
print(f"  File exists            : {os.path.exists(OUTPUT_FILE)}")
print("=" * 60)
