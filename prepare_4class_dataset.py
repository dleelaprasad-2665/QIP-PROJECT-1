import os
import shutil
import hashlib
from pathlib import Path
import random
import cv2

random.seed(42)

REAL_DATA_ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")
PUBLIC_DATA_ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\PUBLIC DATASETS")
OUTPUT_ROOT = Path("training_data/materials_v2")

if OUTPUT_ROOT.exists():
    shutil.rmtree(OUTPUT_ROOT)

CATEGORIES = ["Steel", "Cement_bags", "Cement_bricks", "Sand"]

for split in ["train", "val", "test"]:
    for cat in CATEGORIES:
        (OUTPUT_ROOT / split / cat).mkdir(parents=True, exist_ok=True)

# 1. Collect and classify all unique images from REAL TIME DATASETS
all_real_files = []
seen_hashes = {}

for folder in ["STEEL", "CEMENT & STEEL", "CEMENT BRICKS", "CEMENT,BRICKS,STEEL", "DATA"]:
    f_path = REAL_DATA_ROOT / folder
    if not f_path.exists(): continue
    for p in sorted(f_path.iterdir()):
        if p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            with open(p, "rb") as b:
                h = hashlib.sha256(b.read()).hexdigest()
            if h not in seen_hashes:
                seen_hashes[h] = p
                all_real_files.append((folder, p))

print(f"Total unique real images: {len(all_real_files)}")

# Precise mapping of every unique real-time image
real_by_category = {cat: [] for cat in CATEGORIES}

for folder, p in all_real_files:
    name = p.name
    
    # STEEL folder: all 58 images are Steel
    if folder == "STEEL":
        real_by_category["Steel"].append(p)
        continue
        
    # CEMENT & STEEL folder:
    if folder in ["CEMENT & STEEL", "DATA"]:
        # Steel images: 11.40.41 to 11.43.22, and 12.21.28 to 12.21.34
        if any(k in name for k in ["11.40", "11.41", "11.42", "11.43", "12.21.28", "12.21.29", "12.21.30", "12.21.31", "12.21.32", "12.21.33", "12.21.34"]):
            real_by_category["Steel"].append(p)
        # Sand images: 12.21.26 and 12.21.27
        elif any(k in name for k in ["12.21.26", "12.21.27"]):
            real_by_category["Sand"].append(p)
        # Cement bags: 12.21.14 to 12.21.25
        elif any(k in name for k in ["12.21.14", "12.21.15", "12.21.16", "12.21.17", "12.21.18", "12.21.19", "12.21.20", "12.21.21", "12.21.22", "12.21.23", "12.21.24", "12.21.25"]):
            real_by_category["Cement_bags"].append(p)
        else:
            real_by_category["Cement_bags"].append(p)
        continue
        
    # CEMENT BRICKS folder:
    if folder in ["CEMENT BRICKS", "CEMENT,BRICKS,STEEL"]:
        # Sand images: 12.20.12 to 12.20.17
        if any(k in name for k in ["12.20.12", "12.20.13", "12.20.14", "12.20.15", "12.20.16", "12.20.17"]):
            real_by_category["Sand"].append(p)
        # All other images in this folder are Cement Bricks / Concrete Blocks
        else:
            real_by_category["Cement_bricks"].append(p)

print("\nReal-time images mapped per category:")
for cat in CATEGORIES:
    print(f"  {cat:<15}: {len(real_by_category[cat])} images")

# 2. Add public dataset samples to balance and enrich categories
# Cement bags from public dataset
pub_cement_dir = PUBLIC_DATA_ROOT / "Cement bags.v1i.yolov8" / "train" / "images"
pub_cement_files = list(pub_cement_dir.glob("*.jpg"))
random.shuffle(pub_cement_files)
selected_pub_cement = pub_cement_files[:50]

# Brick masonry from public dataset
pub_brick_dir = PUBLIC_DATA_ROOT / "BRICKS,STONE,TILES" / "CRACK BRICK"
pub_brick_files = list(pub_brick_dir.glob("*.jpg"))
random.shuffle(pub_brick_files)
selected_pub_brick = pub_brick_files[:30]

# Steel rebar from public dataset
pub_steel_dir = PUBLIC_DATA_ROOT / "STEEL" / "train"
pub_steel_files = list(pub_steel_dir.rglob("*.jpg"))
random.shuffle(pub_steel_files)
selected_pub_steel = pub_steel_files[:30]

print(f"Selected public additions: Cement={len(selected_pub_cement)}, Bricks={len(selected_pub_brick)}, Steel={len(selected_pub_steel)}")

# 3. Augment Sand to ensure class balance
sand_pool = list(real_by_category["Sand"])
augmented_sand_paths = []
aug_dir = OUTPUT_ROOT / "sand_augmented"
aug_dir.mkdir(parents=True, exist_ok=True)

for i, sp in enumerate(sand_pool):
    img = cv2.imread(str(sp))
    if img is None: continue
    h, w = img.shape[:2]
    # Crop center, flip
    for flip_mode in [0, 1, -1]:
        flipped = cv2.flip(img, flip_mode)
        out_f = aug_dir / f"aug_sand_{i}_{flip_mode}.jpg"
        cv2.imwrite(str(out_f), flipped)
        augmented_sand_paths.append(out_f)
    # Center crop
    crop = img[int(h*0.1):int(h*0.9), int(w*0.1):int(w*0.9)]
    out_c = aug_dir / f"aug_sand_{i}_crop.jpg"
    cv2.imwrite(str(out_c), crop)
    augmented_sand_paths.append(out_c)

print(f"Created {len(augmented_sand_paths)} augmented sand samples.")

# Assemble full dataset pools
full_pools = {
    "Steel": list(real_by_category["Steel"]) + selected_pub_steel,
    "Cement_bags": list(real_by_category["Cement_bags"]) + selected_pub_cement,
    "Cement_bricks": list(real_by_category["Cement_bricks"]) + selected_pub_brick,
    "Sand": sand_pool + augmented_sand_paths
}

print("\nFinal pool counts:")
for cat in CATEGORIES:
    print(f"  {cat:<15}: {len(full_pools[cat])} images")

# 4. Split into Train (70%), Val (15%), Test (15%)
for cat in CATEGORIES:
    pool = full_pools[cat]
    random.shuffle(pool)
    n = len(pool)
    n_train = int(n * 0.70)
    n_val = int(n * 0.15)
    
    train_items = pool[:n_train]
    val_items = pool[n_train:n_train + n_val]
    test_items = pool[n_train + n_val:]
    
    for idx, p in enumerate(train_items):
        dest = OUTPUT_ROOT / "train" / cat / f"{cat}_{idx}_{p.name}"
        shutil.copy2(p, dest)
        
    for idx, p in enumerate(val_items):
        dest = OUTPUT_ROOT / "val" / cat / f"{cat}_{idx}_{p.name}"
        shutil.copy2(p, dest)
        
    for idx, p in enumerate(test_items):
        dest = OUTPUT_ROOT / "test" / cat / f"{cat}_{idx}_{p.name}"
        shutil.copy2(p, dest)

print("\nDataset preparation complete! Splits created in training_data/materials_v2:")
for split in ["train", "val", "test"]:
    counts = {cat: len(list((OUTPUT_ROOT / split / cat).glob("*.*"))) for cat in CATEGORIES}
    print(f"  {split.upper():<5}: Total={sum(counts.values())}, {counts}")
