import os
import glob
from pathlib import Path
from PIL import Image
import cv2

DATASET_ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")

print(f"=== INSPECTING ROOT: {DATASET_ROOT} ===\n")

if not DATASET_ROOT.exists():
    print(f"ERROR: Root path {DATASET_ROOT} does not exist!")
    exit(1)

# List top-level items
top_items = list(DATASET_ROOT.iterdir())
print(f"Found {len(top_items)} items in dataset root:\n")
for item in top_items:
    print(f" - {item.name} ({'DIR' if item.is_dir() else 'FILE'})")

print("\n" + "="*80)
print("RECURSIVE DIRECTORY STRUCTURE & IMAGE COUNTS")
print("="*80)

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff'}
ANNOT_EXTENSIONS = {'.txt', '.xml', '.json', '.csv'}

all_dirs = []
stats = {}

for root, dirs, files in os.walk(DATASET_ROOT):
    root_path = Path(root)
    img_files = [f for f in files if Path(f).suffix.lower() in IMAGE_EXTENSIONS]
    annot_files = [f for f in files if Path(f).suffix.lower() in ANNOT_EXTENSIONS]
    other_files = [f for f in files if Path(f).suffix.lower() not in IMAGE_EXTENSIONS and Path(f).suffix.lower() not in ANNOT_EXTENSIONS]
    
    if img_files or annot_files or not dirs:
        rel_path = root_path.relative_to(DATASET_ROOT)
        stats[str(rel_path)] = {
            "path": root_path,
            "images": len(img_files),
            "annotations": len(annot_files),
            "other": len(other_files),
            "sample_images": img_files[:3],
            "sample_annots": annot_files[:3]
        }
        print(f"\n[Folder] {rel_path}:")
        print(f"   Images: {len(img_files)} | Annotations: {len(annot_files)} | Other files: {len(other_files)}")
        if img_files:
            print(f"   Sample Images: {img_files[:3]}")
        if annot_files:
            print(f"   Sample Annots: {annot_files[:3]}")

print("\n" + "="*80)
print("TOTAL SUMMARY")
print("="*80)
total_images = sum(s["images"] for s in stats.values())
total_annots = sum(s["annotations"] for s in stats.values())
print(f"Total Folders with content: {len(stats)}")
print(f"Total Images: {total_images}")
print(f"Total Annotations: {total_annots}")
