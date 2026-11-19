import os
import shutil
import hashlib
from pathlib import Path
import random
import cv2

random.seed(42)

REAL_DATA_ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")
PUBLIC_DATA_ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\PUBLIC DATASETS")
OUTPUT_ROOT = Path("training_data/materials_v3")

if OUTPUT_ROOT.exists():
    shutil.rmtree(OUTPUT_ROOT)

CATEGORIES = ["Cement_bags", "Cement_bricks", "Sand", "Steel"]

for split in ["train", "val", "test"]:
    for cat in CATEGORIES:
        (OUTPUT_ROOT / split / cat).mkdir(parents=True, exist_ok=True)

# 1. Collect and classify images
data_by_cat = {cat: [] for cat in CATEGORIES}

# A. CEMENT BAGS:
# In REAL TIME DATASETS/DATA, all 57 images (12.21.14 to 12.21.34) are cement bags
data_dir = REAL_DATA_ROOT / "DATA"
for p in sorted(data_dir.iterdir()):
    if p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        data_by_cat["Cement_bags"].append(p)

# Public cement bags
pub_cement_dir = PUBLIC_DATA_ROOT / "Cement bags.v1i.yolov8" / "train" / "images"
pub_cement_files = sorted(list(pub_cement_dir.glob("*.jpg")))
random.shuffle(pub_cement_files)
data_by_cat["Cement_bags"].extend(pub_cement_files[:35])

# B. STEEL:
# In REAL TIME DATASETS/STEEL, all images are steel rebar
steel_dir = REAL_DATA_ROOT / "STEEL"
for p in sorted(steel_dir.iterdir()):
    if p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        data_by_cat["Steel"].append(p)

# In CEMENT & STEEL, the 11.40 - 11.43 images are steel
cs_dir = REAL_DATA_ROOT / "CEMENT & STEEL"
for p in sorted(cs_dir.iterdir()):
    if any(k in p.name for k in ["11.40", "11.41", "11.42", "11.43"]) and p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        data_by_cat["Steel"].append(p)

# Public steel
pub_steel_dir = PUBLIC_DATA_ROOT / "STEEL" / "train"
pub_steel_files = sorted(list(pub_steel_dir.rglob("*.jpg")))
random.shuffle(pub_steel_files)
data_by_cat["Steel"].extend(pub_steel_files[:25])

# C. CEMENT BRICKS & CLAY BRICKS:
# In CEMENT BRICKS: 12.15 and 12.20.21 to 12.20.42 are concrete masonry blocks/bricks
cb_dir = REAL_DATA_ROOT / "CEMENT BRICKS"
for p in sorted(cb_dir.iterdir()):
    if p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        if "12.15" in p.name or any(f"12.20.{sec}" in p.name for sec in range(21, 45)):
            data_by_cat["Cement_bricks"].append(p)

# Red clay bricks from public dataset
pub_brick_dir = PUBLIC_DATA_ROOT / "BRICKS,STONE,TILES" / "CRACK BRICK"
pub_brick_files = sorted(list(pub_brick_dir.glob("*.jpg")))
random.shuffle(pub_brick_files)
data_by_cat["Cement_bricks"].extend(pub_brick_files[:35])

# MAA-Brick if present
maa_brick = Path("backend/uploads/orig_req_79a6acfcca92_MAA-Brick.jpg")
if maa_brick.exists():
    data_by_cat["Cement_bricks"].append(maa_brick)

# D. SAND:
# In CEMENT BRICKS: 12.20.12 to 12.20.20 are real sand heaps
for p in sorted(cb_dir.iterdir()):
    if p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        if any(f"12.20.{sec}" in p.name for sec in range(12, 21)):
            data_by_cat["Sand"].append(p)

user_sand = Path("backend/uploads/orig_req_84b43d787239_WhatsApp_Image_2026-11-11_at_12.20.15_PM.jpeg")
if user_sand.exists():
    data_by_cat["Sand"].append(user_sand)

print("Collected base images:")
for cat in CATEGORIES:
    print(f"  {cat:<15}: {len(data_by_cat[cat])} images")

# 2. Augment Sand to ensure class balance (~75-80 images total)
sand_base_files = list(data_by_cat["Sand"])
crop_id = 0
for sf in sand_base_files:
    img = cv2.imread(str(sf))
    if img is None: continue
    h, w = img.shape[:2]
    # create 2 non-overlapping crops per image
    if h >= 300 and w >= 300:
        c1 = img[:h//2, :w//2]
        c2 = img[h//2:, w//2:]
        tmp1 = OUTPUT_ROOT / f"sand_crop_{crop_id}_a.jpg"
        tmp2 = OUTPUT_ROOT / f"sand_crop_{crop_id}_b.jpg"
        cv2.imwrite(str(tmp1), c1)
        cv2.imwrite(str(tmp2), c2)
        data_by_cat["Sand"].append(tmp1)
        data_by_cat["Sand"].append(tmp2)
        crop_id += 1
        if len(data_by_cat["Sand"]) >= 80:
            break

print("\nFinal counts after sand balancing:")
for cat in CATEGORIES:
    print(f"  {cat:<15}: {len(data_by_cat[cat])} images")

# 3. Split into Train (70%), Val (15%), Test (15%)
for cat in CATEGORIES:
    imgs = list(data_by_cat[cat])
    random.shuffle(imgs)
    n = len(imgs)
    n_train = int(n * 0.70)
    n_val = int(n * 0.15)
    
    train_imgs = imgs[:n_train]
    val_imgs = imgs[n_train:n_train+n_val]
    test_imgs = imgs[n_train+n_val:]
    
    for split_name, split_list in [("train", train_imgs), ("val", val_imgs), ("test", test_imgs)]:
        dest_dir = OUTPUT_ROOT / split_name / cat
        for idx, src in enumerate(split_list):
            dest_file = dest_dir / f"{cat}_{idx}_{src.name}"
            shutil.copy2(src, dest_file)

# Cleanup temporary crops
for p in OUTPUT_ROOT.glob("sand_crop_*.jpg"):
    p.unlink()

print("\nDataset generation complete!")
for split in ["train", "val", "test"]:
    print(f"=== Split: {split} ===")
    for cat in CATEGORIES:
        count = len(list((OUTPUT_ROOT / split / cat).iterdir()))
        print(f"  {cat:<15}: {count} images")
