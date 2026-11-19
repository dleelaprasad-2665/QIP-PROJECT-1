import cv2
import torch
from PIL import Image
from pathlib import Path
from backend.ai_engine.material_classifier import MaterialClassifier

clf = MaterialClassifier()

def inspect_img(path):
    p = Path(path)
    img = cv2.imread(str(p))
    res = clf.predict(img)
    pil = Image.open(p).convert("RGB")
    tensor = clf.eval_transform(pil).unsqueeze(0)
    with torch.no_grad():
        logits = clf.torch_model(tensor)
        probs = torch.softmax(logits, dim=1)[0].numpy()
    
    print(f"=== {p.name} ===")
    print(f"  Predicted: {res['category']} ({res['confidence']}%)")
    print(f"  Scores   : {res['scores']}")
    print("  Raw Model Probs:")
    for i, c in enumerate(clf.trained_classes):
        print(f"    {c:<15}: {probs[i]*100:.2f}% (logit={logits[0][i]:.3f})")

inspect_img("backend/uploads/orig_req_79a6acfcca92_MAA-Brick.jpg")
print()
inspect_img("backend/uploads/orig_req_120101b40e6a_WhatsApp_Image_2026-11-11_at_12.21.19_PM.jpeg")
