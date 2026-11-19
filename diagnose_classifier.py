import cv2
from pathlib import Path
from backend.ai_engine.material_classifier import MaterialClassifier

clf = MaterialClassifier()
print("PyTorch model loaded:", clf.torch_model is not None)
print("Trained classes:", clf.trained_classes)
print("Trained class to idx:", clf.trained_class_to_idx)

print("\n" + "="*80)
print("TESTING SAND TEST IMAGES:")
print("="*80)
sand_dir = Path("training_data/materials/test/Sand")
for img_path in list(sand_dir.glob("*.*")):
    img = cv2.imread(str(img_path))
    res = clf.predict(img)
    print(f"{img_path.name[:45]:<45} -> {res['category']:<25} ({res['confidence']}%)")
    top3 = sorted(res['scores'].items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"    Top scores: {top3}")

print("\n" + "="*80)
print("TESTING BRICK TEST IMAGES:")
print("="*80)
brick_dir = Path("training_data/materials/test/Bricks")
for img_path in list(brick_dir.glob("*.*"))[:8]:
    img = cv2.imread(str(img_path))
    res = clf.predict(img)
    print(f"{img_path.name[:45]:<45} -> {res['category']:<25} ({res['confidence']}%)")
    top3 = sorted(res['scores'].items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"    Top scores: {top3}")

print("\n" + "="*80)
print("TESTING USER DESKTOP REAL TIME DATASET IMAGES:")
print("="*80)
desktop_path = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS")
for sub in desktop_path.iterdir():
    if sub.is_dir():
        imgs = [f for f in sub.iterdir() if f.suffix.lower() in [".jpg", ".jpeg", ".png"]][:2]
        for f in imgs:
            img = cv2.imread(str(f))
            res = clf.predict(img)
            print(f"[{sub.name[:18]}] {f.name[:35]:<35} -> {res['category']:<25} ({res['confidence']}%)")
