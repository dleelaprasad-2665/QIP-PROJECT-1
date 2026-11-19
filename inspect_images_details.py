import cv2
import numpy as np
from pathlib import Path

ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")

def inspect_folder(folder_name):
    print(f"\n{'='*70}\nINSPECTING FOLDER: {folder_name}\n{'='*70}")
    folder = ROOT / folder_name
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            img = cv2.imread(str(f))
            if img is None: continue
            h, w = img.shape[:2]
            hsv = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2HSV)
            mean_h, mean_s, mean_v = np.mean(hsv, axis=(0, 1))
            gray = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            micro = float(np.mean(cv2.absdiff(gray, blur)))
            print(f"{f.name[:45]:<45} | HSV=({mean_h:4.1f},{mean_s:4.1f},{mean_v:4.1f}) | Micro={micro:4.1f}")

if __name__ == "__main__":
    inspect_folder("CEMENT & STEEL")
    inspect_folder("CEMENT BRICKS")
