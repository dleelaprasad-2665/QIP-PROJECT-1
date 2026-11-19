import os
import cv2
import numpy as np
import hashlib
from pathlib import Path
from collections import defaultdict

ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")

# Collect unique images
unique_imgs = {}
for folder in ["STEEL", "CEMENT & STEEL", "CEMENT BRICKS", "CEMENT,BRICKS,STEEL", "DATA"]:
    f_path = ROOT / folder
    if not f_path.exists(): continue
    for p in sorted(f_path.iterdir()):
        if p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            with open(p, "rb") as b:
                sha = hashlib.sha256(b.read()).hexdigest()
            if sha not in unique_imgs:
                unique_imgs[sha] = (folder, p)

print(f"Total unique images: {len(unique_imgs)}")

# Let's inspect features for clustering
stats = []
for sha, (folder, p) in unique_imgs.items():
    img = cv2.imread(str(p))
    if img is None: continue
    
    hsv = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2HSV)
    h, s, v = np.mean(hsv, axis=(0, 1))
    
    gray = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    micro = float(np.mean(cv2.absdiff(gray, blur)))
    
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.count_nonzero(edges)) / (256 * 256)
    
    stats.append({
        "path": p,
        "folder": folder,
        "name": p.name,
        "h": round(h, 1),
        "s": round(s, 1),
        "v": round(v, 1),
        "micro": round(micro, 1),
        "edge_density": round(edge_density, 3)
    })

print(f"Computed stats for {len(stats)} images.")
