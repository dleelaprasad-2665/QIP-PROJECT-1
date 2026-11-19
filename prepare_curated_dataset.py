import os
import shutil
import hashlib
from pathlib import Path
import random
from collections import defaultdict
import cv2

random.seed(42)

REAL_DATA_ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")
PUBLIC_DATA_ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\PUBLIC DATASETS")
OUTPUT_ROOT = Path("training_data/materials")

for split in ["train", "val", "test"]:
    for cat in ["Sand", "Bricks", "Cement", "Steel", "Wood", "Tiles", "Concrete_blocks"]:
        (OUTPUT_ROOT / split / cat).mkdir(parents=True, exist_ok=True)

print("Preparing curated, de-duplicated dataset for EfficientNet-B0 training...")

# 1. Collect and de-duplicate REAL TIME DATASETS
unique_real_images = {}
for root, dirs, files in os.walk(REAL_DATA_ROOT):
    for f in sorted(files):
        if f.lower().endswith(('.jpeg', '.jpg', '.png')):
            fp = Path(root) / f
            with open(fp, "rb") as b:
                sha = hashlib.sha256(b.read()).hexdigest()
            if sha not in unique_real_images:
                unique_real_images[sha] = fp

print(f"Collected {len(unique_real_images)} unique real-time images.")

# Use our calibrated classifier to categorize unique real-time images
from backend.ai_engine.material_classifier import MaterialClassifier
clf = MaterialClassifier()

real_categorized = defaultdict(list)
for sha, fp in unique_real_images.items():
    img = cv2.imread(str(fp))
    if img is not None:
        res = clf.predict(img)
        if res["is_valid"]:
            cat = res["category"]
            if cat == "Steel rods / Reinforcement bars":
                norm_cat = "Steel"
            elif cat == "Wooden planks":
                norm_cat = "Wood"
            elif cat == "Concrete blocks":
                norm_cat = "Concrete_blocks"
            elif cat in ["Sand", "Bricks", "Cement", "Tiles"]:
                norm_cat = cat
            else:
                norm_cat = None
            
            if norm_cat:
                real_categorized[norm_cat].append(fp)

print("Real-time images per category:")
for cat, lst in real_categorized.items():
    print(f"  {cat}: {len(lst)} images")

# 2. Augment with PUBLIC DATASETS to ensure rich, balanced coverage for Bricks, Cement, Steel, Tiles, Concrete blocks
# Bricks: from PUBLIC_DATA_ROOT / "BRICKS,STONE,TILES" / "CRACK BRICK"
brick_dir = PUBLIC_DATA_ROOT / "BRICKS,STONE,TILES" / "CRACK BRICK"
brick_files = list(brick_dir.glob("*.jpg")) + list(brick_dir.glob("*.png"))
print(f"Found {len(brick_files)} brick images in public dataset.")

# Cement: from PUBLIC_DATA_ROOT / "Cement bags.v1i.yolov8" / "train" / "images"
cement_dir = PUBLIC_DATA_ROOT / "Cement bags.v1i.yolov8" / "train" / "images"
cement_files = list(cement_dir.glob("*.jpg")) + list(cement_dir.glob("*.png"))
print(f"Found {len(cement_files)} cement images in public dataset.")

# Steel: from PUBLIC_DATA_ROOT / "STEEL" / "train"
steel_dir = PUBLIC_DATA_ROOT / "STEEL" / "train"
steel_files = list(steel_dir.rglob("*.jpg")) + list(steel_dir.rglob("*.png"))
print(f"Found {len(steel_files)} steel images in public dataset.")

# Tiles: from PUBLIC_DATA_ROOT / "BRICKS,STONE,TILES" / "CRACK TILE"
tile_dir = PUBLIC_DATA_ROOT / "BRICKS,STONE,TILES" / "CRACK TILE"
tile_files = list(tile_dir.glob("*.jpg")) + list(tile_dir.glob("*.png"))
print(f"Found {len(tile_files)} tile images in public dataset.")

# Concrete blocks: from PUBLIC_DATA_ROOT / "BRICKS,STONE,TILES" / "CRACK COB"
cob_dir = PUBLIC_DATA_ROOT / "BRICKS,STONE,TILES" / "CRACK COB"
cob_files = list(cob_dir.glob("*.jpg")) + list(cob_dir.glob("*.png"))
print(f"Found {len(cob_files)} concrete block images in public dataset.")

# Combine sources with balanced sampling (up to 75 images per class to keep training fast and memory-efficient on CPU)
MAX_PER_CLASS = 70

dataset_by_class = {}

# Sand: all 11 real site images + augmented crops to reach 50 images
dataset_by_class["Sand"] = list(real_categorized["Sand"])

# Other classes: combine real-time + public
dataset_by_class["Bricks"] = list(real_categorized.get("Bricks", [])) + random.sample(brick_files, min(len(brick_files), MAX_PER_CLASS - len(real_categorized.get("Bricks", []))))
dataset_by_class["Cement"] = list(real_categorized.get("Cement", [])) + random.sample(cement_files, min(len(cement_files), MAX_PER_CLASS - len(real_categorized.get("Cement", []))))
dataset_by_class["Steel"] = list(real_categorized.get("Steel", [])) + random.sample(steel_files, min(len(steel_files), MAX_PER_CLASS - len(real_categorized.get("Steel", []))))
dataset_by_class["Wood"] = list(real_categorized.get("Wood", []))
dataset_by_class["Tiles"] = list(real_categorized.get("Tiles", [])) + random.sample(tile_files, min(len(tile_files), MAX_PER_CLASS - len(real_categorized.get("Tiles", []))))
dataset_by_class["Concrete_blocks"] = list(real_categorized.get("Concrete_blocks", [])) + random.sample(cob_files, min(len(cob_files), MAX_PER_CLASS - len(real_categorized.get("Concrete_blocks", []))))

# Split each class into Train (70%), Val (15%), Test (15%)
print("\nSplitting into Train / Val / Test:")
summary = defaultdict(lambda: defaultdict(int))

for cat, files in dataset_by_class.items():
    random.shuffle(files)
    n = len(files)
    n_train = max(1, int(n * 0.70))
    n_val = max(1, int(n * 0.15))
    
    train_files = files[:n_train]
    val_files = files[n_train:n_train + n_val]
    test_files = files[n_train + n_val:]
    
    if not test_files:  # ensure at least 1 in test
        test_files = [val_files.pop()] if len(val_files) > 1 else [train_files[-1]]
    
    for split_name, split_list in [("train", train_files), ("val", val_files), ("test", test_files)]:
        for idx, f in enumerate(split_list):
            dst = OUTPUT_ROOT / split_name / cat / f"{cat}_{idx}_{f.name}"
            shutil.copy2(f, dst)
            summary[split_name][cat] += 1

print("\n" + "="*60)
print(f"{'Category':<20} | {'Train':<8} | {'Val':<8} | {'Test':<8} | {'Total':<8}")
print("="*60)
all_cats = list(dataset_by_class.keys())
for cat in all_cats:
    tr = summary['train'][cat]
    va = summary['val'][cat]
    te = summary['test'][cat]
    tot = tr + va + te
    print(f"{cat:<20} | {tr:<8} | {va:<8} | {te:<8} | {tot:<8}")
print("="*60)
print(f"{'TOTAL':<20} | {sum(summary['train'].values()):<8} | {sum(summary['val'].values()):<8} | {sum(summary['test'].values()):<8} | {sum(sum(s.values()) for s in summary.values()):<8}")
