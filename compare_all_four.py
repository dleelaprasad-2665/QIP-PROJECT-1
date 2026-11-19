import cv2
import numpy as np
from pathlib import Path

files = [
    ("USER STEEL", "backend/uploads/orig_req_f8cfe72b6d9a_WhatsApp_Image_2026-11-11_at_12.21.03_PM_(1).jpeg"),
    ("USER SAND ", "backend/uploads/orig_req_84b43d787239_WhatsApp_Image_2026-11-11_at_12.20.15_PM.jpeg"),
    ("USER BRICK", "backend/uploads/orig_req_79a6acfcca92_MAA-Brick.jpg"),
    ("USER CEMENT", "backend/uploads/orig_req_120101b40e6a_WhatsApp_Image_2026-11-11_at_12.21.19_PM.jpeg"),
    ("USER CEMENT 2", "backend/uploads/orig_req_df6f46923156_WhatsApp_Image_2026-11-11_at_12.21.27_PM.jpeg"),
    ("USER CEMENT 3", "backend/uploads/orig_req_3aafa8194b8c_WhatsApp_Image_2026-11-11_at_12.21.26_PM_(1).jpeg")
]

print(f"{'Label':<15} | {'Filename':<30} | {'HSV (H, S, V)':<20} | {'RGB (R, G, B)':<20} | {'Micro':<6} | {'Edges':<6}")
print("-" * 110)

for label, fpath in files:
    p = Path(fpath)
    if not p.exists(): continue
    img = cv2.imread(str(p))
    if img is None: continue
    
    img_std = cv2.resize(img, (256, 256))
    hsv = cv2.cvtColor(img_std, cv2.COLOR_BGR2HSV)
    h, s, v = np.mean(hsv, axis=(0, 1))
    
    b, g, r = np.mean(img_std, axis=(0, 1))
    
    gray = cv2.cvtColor(img_std, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    micro = float(np.mean(cv2.absdiff(gray, blur)))
    
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.count_nonzero(edges)) / (256 * 256)
    
    print(f"{label:<15} | {p.name[:30]:<30} | ({h:5.1f}, {s:5.1f}, {v:5.1f}) | ({r:5.1f}, {g:5.1f}, {b:5.1f}) | {micro:5.1f} | {edge_density:5.3f}")
