"""Organize data-examples JSON files into subdirectories by type."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


def classify(obj: Any) -> str:
    """Classify JSON object as chatgpt_export_list, chatgpt_single, claude, or other."""
    if isinstance(obj, list):
        return "chatgpt_export_list"
    if isinstance(obj, dict):
        if "chat_messages" in obj and obj.get("platform") == "CLAUDE_AI":
            return "claude"
        if "mapping" in obj and "current_node" in obj:
            return "chatgpt_single"
    return "other"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data-examples")
    ap.add_argument("--apply", action="store_true", help="Actually move files (otherwise dry-run).")
    ap.add_argument("--copy", action="store_true", help="Copy instead of move.")
    ap.add_argument(
        "--write-merged-chatgpt-export",
        action="store_true",
        help="Write chatgpt_export/merged_chatgpt_export.json with generated ids.",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    files = sorted(p for p in root.glob("*.json") if p.is_file())

    out_chatgpt_single = root / "chatgpt_single"
    out_claude = root / "claude"
    out_export = root / "chatgpt_export"
    out_other = root / "other"

    moves: list[tuple[Path, Path]] = []
    merged: list[dict[str, Any]] = []

    for p in files:
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            bucket = "other"
            obj = None
        else:
            bucket = classify(obj)

        if bucket == "chatgpt_single":
            dest_dir = out_chatgpt_single
            if args.write_merged_chatgpt_export and isinstance(obj, dict):
                # Ensure the current CLI can work: needs conversation["id"] (or "conversation_id")
                if not obj.get("id") and not obj.get("conversation_id"):
                    obj["id"] = p.stem  # recommendation: filename-based id
                merged.append(obj)
        elif bucket == "claude":
            dest_dir = out_claude
        elif bucket == "chatgpt_export_list":
            dest_dir = out_export
        else:
            dest_dir = out_other

        dest = dest_dir / p.name
        moves.append((p, dest))

    # Show plan
    print(f"Root: {root}")
    print(f"\nOrganization plan:")
    for src, dst in moves:
        action = "COPY" if args.copy else "MOVE"
        print(f"  {action} {src.name} -> {dst.relative_to(root)}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to perform changes.")
        return

    # Apply moves/copies
    for d in [out_chatgpt_single, out_claude, out_export, out_other]:
        d.mkdir(parents=True, exist_ok=True)

    for src, dst in moves:
        if dst.exists():
            print(f"⚠️  Skipping (exists): {dst.relative_to(root)}")
            continue
        if args.copy:
            shutil.copy2(src, dst)
            print(f"✓ Copied: {src.name} -> {dst.relative_to(root)}")
        else:
            src.rename(dst)
            print(f"✓ Moved: {src.name} -> {dst.relative_to(root)}")

    if args.write_merged_chatgpt_export and merged:
        out_export.mkdir(parents=True, exist_ok=True)
        merged_path = out_export / "merged_chatgpt_export.json"
        merged_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✓ Wrote merged export: {merged_path.relative_to(root)} ({len(merged)} conversations)")


if __name__ == "__main__":
    main()


