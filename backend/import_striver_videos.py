"""
CLI Runner for Striver A2Z Video Importer.

Modes
-----
Default (catalog-based):
    python import_striver_videos.py [--force] [--output-json PATH]

Excel-based (uses Striver_A2Z_Playlist_Links.xlsx as source of truth):
    python import_striver_videos.py --excel PATH/TO/Striver_A2Z_Playlist_Links.xlsx [--force] [--output-json PATH]
"""

import argparse
import sys
import os

# Add backend directory to python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal


def main():
    parser = argparse.ArgumentParser(
        description="Import Striver A2Z YouTube videos into DSArena roadmap nodes."
    )
    parser.add_argument(
        "--excel",
        type=str,
        default=None,
        metavar="PATH",
        help=(
            "Path to Striver_A2Z_Playlist_Links.xlsx. "
            "When provided, uses the ExcelVideoImporter instead of the catalog-based importer."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing YouTube URLs on roadmap nodes.",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="unmatched_nodes.json",
        help="Path to save the unmatched nodes report JSON.",
    )

    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.excel:
            # ── Excel-based import ────────────────────────────────────────
            excel_path = os.path.abspath(args.excel)
            if not os.path.exists(excel_path):
                print(f"[ERROR] Excel file not found: {excel_path}", file=sys.stderr)
                sys.exit(1)

            from app.services.excel_video_importer import ExcelVideoImporter

            importer = ExcelVideoImporter(
                db=db,
                excel_path=excel_path,
                force=args.force,
                output_json_path=args.output_json,
            )
        else:
            # ── Catalog-based import (original behaviour) ─────────────────
            from app.services.striver_importer import StriverVideoImporter

            importer = StriverVideoImporter(
                db=db,
                force=args.force,
                output_json_path=args.output_json,
            )

        summary = importer.run_import()
        sys.exit(0)

    except Exception as exc:
        print(f"[ERROR] Import failed: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
