import cv2
import numpy as np
from pathlib import Path

ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")

def sample_images(folder, time_prefixes):
    print(f"\n--- Sampling {folder} for prefixes {time_prefixes} ---")
    p = ROOT / folder
    for prefix in time_prefixes:
        matches = [f for f in sorted(p.iterdir()) if prefix in f.name and f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        if matches:
            f = matches[0]
            img = cv2.imread(str(f))
            h, w = img.shape[:2]
            hsv = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2HSV)
            mean_h, mean_s, mean_v = np.mean(hsv, axis=(0, 1))
            gray = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            micro = float(np.mean(cv2.absdiff(gray, blur)))
            print(f"[{prefix}] {f.name[:35]:<35} -> HSV=({mean_h:4.1f},{mean_s:4.1f},{mean_v:4.1f}), Micro={micro:4.1f}")

sample_images("CEMENT BRICKS", ["12.15.32", "12.15.37", "12.20.13", "12.20.15", "12.20.18", "12.20.22", "12.20.26", "12.20.30", "12.20.35", "12.20.41"])
sample_images("STEEL", ["12.20.42", "12.20.52", "12.21.00", "12.21.03", "12.21.08", "12.21.11"])
sample_images("CEMENT & STEEL", ["11.40.41", "11.41.39", "12.21.14", "12.21.18", "12.21.22", "12.21.26", "12.21.30", "12.21.34"])
