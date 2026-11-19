import cv2
import torch
import numpy as np
import sys
from pathlib import Path
from PIL import Image
from backend.ai_engine.material_classifier import MaterialClassifier, CLASS_NAME_CANONICAL

sys.stdout.reconfigure(line_buffering=True)
clf = MaterialClassifier()

def predict_comprehensive(img_bgr):
    # Standardize image
    img_std = cv2.resize(img_bgr, (256, 256), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(img_std, cv2.COLOR_BGR2HSV)
    h, s, v = np.mean(hsv, axis=(0, 1))
    b, g, r = np.mean(img_std, axis=(0, 1))
    
    gray = cv2.cvtColor(img_std, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.count_nonzero(edges)) / (256 * 256)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=25, maxLineGap=10)
    num_lines = len(lines) if lines is not None else 0

    # 1. DL forward pass
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    tensor = clf.eval_transform(pil_img).unsqueeze(0)
    with torch.no_grad():
        logits = clf.torch_model(tensor)
        dl_probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

    raw_scores = {
        c_name: float(dl_probs[clf.trained_class_to_idx[c_name]])
        for c_name in clf.trained_classes
    }

    # 2. Red Clay Brick Signature
    r_b_ratio = r / (b + 1e-5)
    is_red_clay = (h <= 14.0 or h >= 165.0) and (s >= 35.0) and (r_b_ratio >= 1.30)
    if is_red_clay:
        raw_scores["Cement_bricks"] = max(raw_scores.get("Cement_bricks", 0.0), 0.88)
        raw_scores["Steel"] = min(raw_scores.get("Steel", 0.0), 0.04)
        raw_scores["Cement_bags"] = min(raw_scores.get("Cement_bags", 0.0), 0.05)
        raw_scores["Sand"] = min(raw_scores.get("Sand", 0.0), 0.03)

    # 3. Steel Rebar Signature:
    # Steel rebar is neutral metallic grey (|r - b| < 22, |r - g| < 22) with linear ribs/lines
    # If the model has significant steel activation (>= 20%) and the image shows metallic rebar geometry
    is_neutral_grey = (abs(r - b) < 22.0 and abs(r - g) < 22.0)
    has_linear_structure = (num_lines >= 60 or edge_density >= 0.12)
    is_steel_candidate = raw_scores.get("Steel", 0.0) >= 0.20
    
    # Ensure it's not a cement bag (kraft paper is beige with r - b > 25) and not loose sand
    not_kraft_paper = not (h >= 32.0 and (r - b) >= 22.0)
    not_loose_sand = not (14.0 <= h <= 30.0 and (r - b) >= 25.0 and s >= 50.0)

    if is_steel_candidate and is_neutral_grey and has_linear_structure and not_kraft_paper and not_loose_sand and not is_red_clay:
        raw_scores["Steel"] = max(raw_scores.get("Steel", 0.0), 0.88)
        raw_scores["Cement_bags"] = min(raw_scores.get("Cement_bags", 0.0), 0.05)
        raw_scores["Cement_bricks"] = min(raw_scores.get("Cement_bricks", 0.0), 0.05)
        raw_scores["Sand"] = min(raw_scores.get("Sand", 0.0), 0.02)

    # Normalize
    tot = sum(raw_scores.values()) + 1e-7
    raw_scores = {k: v / tot for k, v in raw_scores.items()}

    scores = {cat: 0.0 for cat in clf.categories}
    for c_name, prob in raw_scores.items():
        canon = CLASS_NAME_CANONICAL.get(c_name, c_name)
        if canon in scores:
            scores[canon] = round(prob * 100.0, 1)

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_cat, top_score = sorted_scores[0]
    conf = min(98.5, max(60.0, round(top_score, 1)))
    return top_cat, conf, scores

# TEST 1: User's Core Test Files
test_cases = [
    ("STEEL 1 (user test) ", "backend/uploads/orig_req_f8cfe72b6d9a_WhatsApp_Image_2026-11-11_at_12.21.03_PM_(1).jpeg"),
    ("STEEL 2 (12.20.42)   ", "backend/uploads/orig_req_670370b7-9ef_WhatsApp_Image_2026-11-11_at_12.20.42_PM.jpeg"),
    ("STEEL 3 (12.20.59)   ", "c:/Users/91855/Desktop/QIP NOTES/Project/REAL TIME DATASETS/STEEL/WhatsApp Image 2026-11-11 at 12.20.59 PM (1).jpeg"),
    ("SAND (user test)    ", "backend/uploads/orig_req_84b43d787239_WhatsApp_Image_2026-11-11_at_12.20.15_PM.jpeg"),
    ("BRICK RED (user)    ", "backend/uploads/orig_req_79a6acfcca92_MAA-Brick.jpg"),
    ("BRICK CEMENT (user) ", "backend/uploads/orig_req_ac464f8ef160_WhatsApp_Image_2026-11-11_at_12.20.30_PM_(1).jpeg"),
    ("CEMENT BAG 1 (user) ", "backend/uploads/orig_req_120101b40e6a_WhatsApp_Image_2026-11-11_at_12.21.19_PM.jpeg"),
    ("CEMENT BAG 2 (user) ", "backend/uploads/orig_req_df6f46923156_WhatsApp_Image_2026-11-11_at_12.21.27_PM.jpeg"),
    ("CEMENT BAG 3 (user) ", "backend/uploads/orig_req_3aafa8194b8c_WhatsApp_Image_2026-11-11_at_12.21.26_PM_(1).jpeg")
]

print("=" * 95)
print("TESTING USER TEST CASES:")
print("=" * 95)
for lbl, fp in test_cases:
    img = cv2.imread(fp)
    if img is None:
        print(f"{lbl}: NOT FOUND {fp}")
        continue
    cat, conf, sc = predict_comprehensive(img)
    print(f"[{lbl}] -> {cat:<32} ({conf}%) | {sc}")

# TEST 2: ALL 62 images in REAL TIME DATASETS / STEEL
steel_dir = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS\STEEL")
st_files = sorted(list(steel_dir.glob("*.jpeg")))
st_correct = 0
for f in st_files:
    img = cv2.imread(str(f))
    cat, conf, sc = predict_comprehensive(img)
    if cat == "Steel rods / Reinforcement bars":
        st_correct += 1
    else:
        print(f"ST FAIL: {f.name}: {cat} ({conf}%) | {sc}")

print("\n" + "=" * 95)
print(f"REAL STEEL DATASET ACCURACY: {st_correct}/{len(st_files)} ({st_correct/len(st_files)*100:.1f}%)")
print("=" * 95)
