import cv2
import sys
from pathlib import Path
from backend.ai_engine.material_classifier import MaterialClassifier

sys.stdout.reconfigure(line_buffering=True)
clf = MaterialClassifier()

tests = [
    ('USER STEEL 1 ', 'backend/uploads/orig_req_f8cfe72b6d9a_WhatsApp_Image_2026-11-11_at_12.21.03_PM_(1).jpeg'),
    ('USER STEEL 2 ', 'c:/Users/91855/Desktop/QIP NOTES/Project/REAL TIME DATASETS/STEEL/WhatsApp Image 2026-11-11 at 12.20.59 PM (1).jpeg'),
    ('HIGH RES STEEL', 'c:/Users/91855/Desktop/QIP NOTES/Project/PUBLIC DATASETS/STEEL/train/rolled-in_scale/000018.jpg'),
    ('USER SAND    ', 'backend/uploads/orig_req_84b43d787239_WhatsApp_Image_2026-11-11_at_12.20.15_PM.jpeg'),
    ('USER BRICK R ', 'backend/uploads/orig_req_79a6acfcca92_MAA-Brick.jpg'),
    ('USER BRICK C ', 'backend/uploads/orig_req_ac464f8ef160_WhatsApp_Image_2026-11-11_at_12.20.30_PM_(1).jpeg'),
    ('USER CEMENT 1', 'backend/uploads/orig_req_120101b40e6a_WhatsApp_Image_2026-11-11_at_12.21.19_PM.jpeg'),
    ('USER CEMENT 2', 'backend/uploads/orig_req_df6f46923156_WhatsApp_Image_2026-11-11_at_12.21.27_PM.jpeg'),
    ('USER CEMENT 3', 'backend/uploads/orig_req_3aafa8194b8c_WhatsApp_Image_2026-11-11_at_12.21.26_PM_(1).jpeg')
]

print("=" * 80)
print("TESTING MATERIAL CLASSIFIER WITH STEEL FIX:")
print("=" * 80)
for lbl, fp in tests:
    img = cv2.imread(fp)
    if img is None:
        print(f"[{lbl}] -> File not found: {fp}")
        continue
    res = clf.predict(img)
    print(f"[{lbl}] -> {res['category']:<32} ({res['confidence']}%) | valid={res['is_valid']}")
