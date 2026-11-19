import os
from pathlib import Path
import hashlib
from collections import defaultdict

ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")

folders = [d for d in ROOT.iterdir() if d.is_dir()]
print("Folders found in REAL TIME DATASETS:")
for f in folders:
    imgs = [x for x in f.iterdir() if x.suffix.lower() in [".jpg", ".jpeg", ".png"]]
    print(f"  {f.name}: {len(imgs)} images")

print("\nDe-duplicating across all folders:")
seen_hashes = {}
folder_counts = defaultdict(int)
unique_files_by_folder = defaultdict(list)

for f in folders:
    for img_path in sorted(f.iterdir()):
        if img_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            with open(img_path, "rb") as b:
                h = hashlib.sha256(b.read()).hexdigest()
            if h not in seen_hashes:
                seen_hashes[h] = (f.name, img_path.name)
                unique_files_by_folder[f.name].append(img_path)

print("Unique files by first-seen folder:")
for folder_name, lst in unique_files_by_folder.items():
    print(f"  {folder_name}: {len(lst)} unique images")
