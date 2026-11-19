import cv2
import numpy as np
from pathlib import Path

ROOT = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")

# Let's inspect images in CEMENT & STEEL between 12.21.18 and 12.21.25 (Cement bags)
print("=== CEMENT BAGS CHECK ===")
for p in sorted((ROOT / "CEMENT & STEEL").iterdir()):
    if any(k in p.name for k in ["12.21.18", "12.21.19", "12.21.20", "12.21.21", "12.21.22", "12.21.23", "12.21.24", "12.21.25"]):
        img = cv2.imread(str(p))
        if img is None: continue
        hsv = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2HSV)
        h, s, v = np.mean(hsv, axis=(0, 1))
        print(f"Cement candidate: {p.name[:40]:<40} -> HSV=({h:.1f}, {s:.1f}, {v:.1f})")

print("\n=== SAND CHECK ===")
for p in sorted((ROOT / "CEMENT & STEEL").iterdir()):
    if any(k in p.name for k in ["12.21.26", "12.21.27"]):
        img = cv2.imread(str(p))
        if img is None: continue
        hsv = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2HSV)
        h, s, v = np.mean(hsv, axis=(0, 1))
        print(f"Sand candidate (in CEMENT & STEEL): {p.name[:40]:<40} -> HSV=({h:.1f}, {s:.1f}, {v:.1f})")

for p in sorted((ROOT / "CEMENT BRICKS").iterdir()):
    if any(k in p.name for k in ["12.20.12", "12.20.13", "12.20.14", "12.20.15", "12.20.16", "12.20.17"]):
        img = cv2.imread(str(p))
        if img is None: continue
        hsv = cv2.cvtColor(cv2.resize(img, (256, 256)), cv2.COLOR_BGR2HSV)
        h, s, v = np.mean(hsv, axis=(0, 1))
        print(f"Sand candidate (in CEMENT BRICKS): {p.name[:40]:<40} -> HSV=({h:.1f}, {s:.1f}, {v:.1f})")
