import cv2
import torch
import sys
import numpy as np
from PIL import Image
from backend.ai_engine.material_classifier import MaterialClassifier, CLASS_NAME_CANONICAL

sys.stdout.reconfigure(line_buffering=True)

clf = MaterialClassifier()

def predict_enhanced(img_bgr):
    # DL forward pass
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

    # Physical color signature check
    img_std = cv2.resize(img_bgr, (256, 256), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(img_std, cv2.COLOR_BGR2HSV)
    h, s, v = np.mean(hsv, axis=(0, 1))
    b, g, r = np.mean(img_std, axis=(0, 1))
    r_b_ratio = r / (b + 1e-5)

    is_red_clay = (h <= 14.0 or h >= 165.0) and (s >= 35.0) and (r_b_ratio >= 1.30)
    if is_red_clay:
        raw_scores["Cement_bricks"] = max(raw_scores.get("Cement_bricks", 0.0), 0.88)
        raw_scores["Steel"] = min(raw_scores.get("Steel", 0.0), 0.04)
        raw_scores["Cement_bags"] = min(raw_scores.get("Cement_bags", 0.0), 0.05)
        raw_scores["Sand"] = min(raw_scores.get("Sand", 0.0), 0.03)

    tot = sum(raw_scores.values()) + 1e-7
    raw_scores = {k: v / tot for k, v in raw_scores.items()}

    scores = {cat: 0.0 for cat in clf.categories}
    for c_name, prob in raw_scores.items():
        canon_name = CLASS_NAME_CANONICAL.get(c_name, c_name)
        if canon_name in scores:
            scores[canon_name] = round(prob * 100.0, 1)

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_cat, top_score = sorted_scores[0]
    conf = min(98.5, max(60.0, round(top_score, 1)))
    return top_cat, conf, scores

test_files = [
    ('USER STEEL   ', 'backend/uploads/orig_req_f8cfe72b6d9a_WhatsApp_Image_2026-11-11_at_12.21.03_PM_(1).jpeg'),
    ('USER SAND    ', 'backend/uploads/orig_req_84b43d787239_WhatsApp_Image_2026-11-11_at_12.20.15_PM.jpeg'),
    ('USER BRICK   ', 'backend/uploads/orig_req_79a6acfcca92_MAA-Brick.jpg'),
    ('USER BRICK 2 ', 'backend/uploads/orig_req_ac464f8ef160_WhatsApp_Image_2026-11-11_at_12.20.30_PM_(1).jpeg'),
    ('USER CEMENT 1', 'backend/uploads/orig_req_120101b40e6a_WhatsApp_Image_2026-11-11_at_12.21.19_PM.jpeg'),
    ('USER CEMENT 2', 'backend/uploads/orig_req_df6f46923156_WhatsApp_Image_2026-11-11_at_12.21.27_PM.jpeg'),
    ('USER CEMENT 3', 'backend/uploads/orig_req_3aafa8194b8c_WhatsApp_Image_2026-11-11_at_12.21.26_PM_(1).jpeg'),
    ('USER CEMENT 4', 'backend/uploads/orig_req_d8c391cf0d3d_WhatsApp_Image_2026-11-11_at_12.21.28_PM_(2).jpeg')
]

print("=" * 85)
print("TESTING ENHANCED CLASSIFIER ON ALL USER UPLOADS:")
print("=" * 85)

for lbl, fpath in test_files:
    img = cv2.imread(fpath)
    if img is None:
        continue
    top_cat, conf, scores = predict_enhanced(img)
    print(f"[{lbl}] -> {top_cat:<32} ({conf}%) | {scores}")
