import os
import hashlib
from pathlib import Path
import cv2
from collections import defaultdict
from backend.ai_engine.material_classifier import MaterialClassifier

DATASET_ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")
clf = MaterialClassifier()

# 1. Collect all unique images
unique_images = {}
for root, dirs, files in os.walk(DATASET_ROOT):
    for f in sorted(files):
        if f.lower().endswith(('.jpeg', '.jpg', '.png')):
            fp = Path(root) / f
            with open(fp, "rb") as b:
                sha = hashlib.sha256(b.read()).hexdigest()
            if sha not in unique_images:
                unique_images[sha] = {
                    "path": fp,
                    "folder": Path(root).name,
                    "filename": f
                }

print(f"Total Unique Images Collected: {len(unique_images)}\n")

# 2. Run analysis on each unique image
category_counts = defaultdict(int)
folder_category_breakdown = defaultdict(lambda: defaultdict(int))
detailed_records = []

for sha, meta in unique_images.items():
    img = cv2.imread(str(meta["path"]))
    res = clf.predict(img)
    cat = res["category"]
    conf = res["confidence"]
    valid = res["is_valid"]
    
    category_counts[cat] += 1
    folder_category_breakdown[meta["folder"]][cat] += 1
    
    detailed_records.append({
        "folder": meta["folder"],
        "filename": meta["filename"],
        "category": cat,
        "confidence": conf,
        "is_valid": valid
    })

print("="*80)
print("MATERIAL CATEGORY DISTRIBUTION ACROSS ALL 213 UNIQUE REAL-TIME IMAGES")
print("="*80)
for cat, cnt in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
    pct = round((cnt / len(unique_images)) * 100, 1)
    print(f" - {cat:<35}: {cnt:>3} images ({pct}%)")

print("\n" + "="*80)
print("PER-FOLDER CATEGORY BREAKDOWN")
print("="*80)
for folder, cats in folder_category_breakdown.items():
    print(f"\n[Folder: {folder}]")
    for cat, cnt in sorted(cats.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat:<32}: {cnt} images")

