import os
import cv2
import sys
from pathlib import Path
from backend.ai_engine.material_classifier import MaterialClassifier

sys.stdout.reconfigure(line_buffering=True)
clf = MaterialClassifier()

print("=" * 85)
print("1. CEMENT & STEEL (11.40 to 11.43):")
print("=" * 85)
cs_dir = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS\CEMENT & STEEL")
for f in sorted(cs_dir.glob("*.jpeg")):
    if any(k in f.name for k in ["11.40", "11.41", "11.42", "11.43"]):
        img = cv2.imread(str(f))
        res = clf.predict(img)
        print(f"CS {f.name[:35]:<35}: {res['category']:<30} ({res['confidence']}%) | {res['scores']}")

print("\n" + "=" * 85)
print("2. REAL TIME DATASETS / STEEL (first 10 and last 10):")
print("=" * 85)
steel_dir = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS\STEEL")
st_files = sorted(list(steel_dir.glob("*.jpeg")))
for f in st_files[:5] + st_files[25:30] + st_files[-5:]:
    img = cv2.imread(str(f))
    res = clf.predict(img)
    print(f"ST {f.name[:35]:<35}: {res['category']:<30} ({res['confidence']}%) | {res['scores']}")

print("\n" + "=" * 85)
print("3. PUBLIC DATASETS / STEEL (10 samples):")
print("=" * 85)
pub_dir = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\PUBLIC DATASETS\STEEL\train")
for f in list(pub_dir.rglob("*.jpg"))[:10]:
    img = cv2.imread(str(f))
    res = clf.predict(img)
    print(f"PUB {f.name[:35]:<35}: {res['category']:<30} ({res['confidence']}%) | {res['scores']}")
