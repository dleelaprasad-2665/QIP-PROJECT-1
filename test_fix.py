import cv2
from pathlib import Path
from backend.ai_engine.material_classifier import MaterialClassifier

clf = MaterialClassifier()

user_sand = Path('backend/uploads/orig_req_84b43d787239_WhatsApp_Image_2026-11-11_at_12.20.15_PM.jpeg')
user_brick = Path('backend/uploads/orig_req_e202d415eea7_BRICK_CRACK_(100).jpg')

print("--- User Uploaded Sand Image ---")
res1 = clf.predict(cv2.imread(str(user_sand)))
print("Result :", res1["category"], f"({res1['confidence']}%)")
print("Top Scores :", sorted(res1["scores"].items(), key=lambda x: x[1], reverse=True)[:3])

print("\n--- User Uploaded Brick Image ---")
res2 = clf.predict(cv2.imread(str(user_brick)))
print("Result :", res2["category"], f"({res2['confidence']}%)")
print("Top Scores :", sorted(res2["scores"].items(), key=lambda x: x[1], reverse=True)[:3])

print("\n--- Checking Other Materials in Test Set ---")
for cat in ["Sand", "Bricks", "Cement", "Steel", "Wood", "Tiles", "Concrete_blocks"]:
    d = Path("training_data/materials/test") / cat
    f = next(d.glob("*.*"))
    r = clf.predict(cv2.imread(str(f)))
    print(f"[{cat:<15}] -> Predicted: {r['category']} ({r['confidence']}%)")
