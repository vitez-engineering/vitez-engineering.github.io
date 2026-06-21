#!/usr/bin/env python3
"""
Generates a thumbnail tier for the photography gallery grid.

Full-resolution images stay in images/ (used by the lightbox).
This script creates smaller, more compressed copies in images/thumbs/
for use in the scrolling grid, where they're rarely displayed wider
than ~600px on screen.

Usage:
    pip install pillow --break-system-packages
    python3 generate_thumbnails.py

Run this from the folder that contains your "images" directory
(i.e. the same folder as your dimensions.json and photography.html).
"""

import os
from pathlib import Path
from PIL import Image

SOURCE_DIR = Path("images")
THUMB_DIR = Path("images/thumbs")
MAX_WIDTH = 1000      # covers retina displays at typical grid column widths
WEBP_QUALITY = 80      # visually near-lossless at this resolution, much smaller file

def main():
    if not SOURCE_DIR.exists():
        print(f"Could not find '{SOURCE_DIR}' — run this script from your site's root folder.")
        return

    THUMB_DIR.mkdir(parents=True, exist_ok=True)

    images = [f for f in SOURCE_DIR.iterdir() if f.is_file() and f.suffix.lower() in (".webp", ".jpg", ".jpeg", ".png")]
    if not images:
        print(f"No images found in '{SOURCE_DIR}'.")
        return

    total_before = 0
    total_after = 0
    skipped = 0

    for i, path in enumerate(images, 1):
        thumb_path = THUMB_DIR / (path.stem + ".webp")

        if thumb_path.exists():
            skipped += 1
            continue

        with Image.open(path) as img:
            img = img.convert("RGB")
            w, h = img.size
            if w > MAX_WIDTH:
                new_h = round(h * (MAX_WIDTH / w))
                img = img.resize((MAX_WIDTH, new_h), Image.LANCZOS)

            img.save(thumb_path, "WEBP", quality=WEBP_QUALITY, method=6)

        before = path.stat().st_size
        after = thumb_path.stat().st_size
        total_before += before
        total_after += after

        print(f"[{i}/{len(images)}] {path.name}: {before/1024:.0f}KB -> {after/1024:.0f}KB")

    print()
    print(f"Done. {len(images) - skipped} thumbnails created, {skipped} already existed.")
    if total_before:
        reduction = 100 * (1 - total_after / total_before)
        print(f"Total: {total_before/1024/1024:.1f}MB -> {total_after/1024/1024:.1f}MB ({reduction:.0f}% smaller)")

if __name__ == "__main__":
    main()
