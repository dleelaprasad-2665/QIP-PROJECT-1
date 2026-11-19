import cv2
import numpy as np
from pathlib import Path

folder = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS\CEMENT BRICKS")
files = sorted(list(folder.glob("*.jpeg")))[:10]

print("Inspecting first 10 images from 'CEMENT BRICKS':\n")
for f in files:
    img = cv2.imread(str(f))
    h, w, c = img.shape
    hsv = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2HSV)
    mean_hsv = np.mean(hsv, axis=(0, 1))
    gray = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2GRAY)
    lap_std = float(np.std(cv2.Laplacian(gray, cv2.CV_64F)))
    print(f"File: {f.name}")
    print(f"  Shape: {w}x{h} | Mean HSV: H={mean_hsv[0]:.1f}, S={mean_hsv[1]:.1f}, V={mean_hsv[2]:.1f} | Roughness: {lap_std:.1f}")
