import os
import hashlib
from pathlib import Path
import cv2
from backend.ai_engine.material_classifier import MaterialClassifier

DATASET_ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")
clf = MaterialClassifier()

sand_images = []
seen_hashes = set()

for root, dirs, files in os.walk(DATASET_ROOT):
    for f in sorted(files):
        if f.lower().endswith(('.jpeg', '.jpg', '.png')):
            fp = Path(root) / f
            with open(fp, "rb") as b:
                sha = hashlib.sha256(b.read()).hexdigest()
            if sha in seen_hashes:
                continue
            seen_hashes.add(sha)
            
            img = cv2.imread(str(fp))
            if img is not None:
                res = clf.predict(img)
                if res["category"] == "Sand":
                    sand_images.append((fp, res["confidence"], Path(root).name, f))

print(f"Found {len(sand_images)} unique sand images in REAL TIME DATASETS:\n")
for p, conf, folder, name in sand_images:
    print(f"[{folder}] {name} (Conf: {conf}%)")
