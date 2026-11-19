import os
import hashlib
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from collections import defaultdict

DATASET_ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")

folders = ["CEMENT & STEEL", "CEMENT BRICKS", "CEMENT,BRICKS,STEEL", "DATA", "STEEL"]

print("="*80)
print("FORENSIC ANALYSIS OF REAL TIME DATASET FOLDERS")
print("="*80)

folder_file_hashes = {}
all_hashes = defaultdict(list)
corrupted_files = []
image_resolutions = defaultdict(int)

for folder_name in folders:
    folder_path = DATASET_ROOT / folder_name
    files = list(folder_path.glob("*.jpeg")) + list(folder_path.glob("*.jpg")) + list(folder_path.glob("*.png"))
    folder_file_hashes[folder_name] = {}
    print(f"\n--- Folder: {folder_name} (Total image files: {len(files)}) ---")
    
    for f in sorted(files):
        # Compute SHA256
        with open(f, "rb") as fp:
            data = fp.read()
            sha = hashlib.sha256(data).hexdigest()
        
        folder_file_hashes[folder_name][f.name] = sha
        all_hashes[sha].append((folder_name, f.name, f.stat().st_size))
        
        # Test image decoding
        try:
            img = cv2.imread(str(f))
            if img is None:
                corrupted_files.append((folder_name, f.name, "cv2.imread returned None"))
            else:
                h, w, c = img.shape
                image_resolutions[(w, h)] += 1
        except Exception as e:
            corrupted_files.append((folder_name, f.name, str(e)))

print("\n" + "="*80)
print("DUPLICATE AND OVERLAP ANALYSIS ACROSS FOLDERS")
print("="*80)

print(f"Total image files across all 5 folders: {sum(len(f) for f in folder_file_hashes.values())}")
print(f"Total UNIQUE images (by SHA-256 hash): {len(all_hashes)}")

# Check pairwise overlap
for i in range(len(folders)):
    for j in range(i+1, len(folders)):
        f1, f2 = folders[i], folders[j]
        hashes1 = set(folder_file_hashes[f1].values())
        hashes2 = set(folder_file_hashes[f2].values())
        overlap = hashes1.intersection(hashes2)
        print(f"Overlap between '{f1}' and '{f2}': {len(overlap)} duplicate images")

print("\n" + "="*80)
print("IMAGE RESOLUTIONS AND CORRUPTIONS")
print("="*80)
print(f"Corrupted or unreadable image files: {len(corrupted_files)}")
for c in corrupted_files:
    print(" -", c)

print("\nMost common image resolutions (width x height):")
for res, count in sorted(image_resolutions.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {res[0]}x{res[1]}: {count} images")

