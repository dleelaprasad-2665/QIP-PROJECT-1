import urllib.request
import uuid
import json
from pathlib import Path

def test_api_upload(path: Path, label: str):
    boundary = uuid.uuid4().hex
    with open(path, "rb") as f:
        data = f.read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/ai/analyze",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req) as r:
        res = json.loads(r.read().decode())
        print(f"[{label:<15}] {path.name[:35]:<35} -> {res['material_category']} ({res['material_confidence']}%) | Cond: {res['condition']}, Rec: {res['recommendation']}")

if __name__ == "__main__":
    print("=" * 95)
    print("TESTING LIVE SERVER (PORT 8000) WITH USER'S REAL UPLOADS & DATASETS")
    print("=" * 95)
    
    # 1. The exact Steel image the user uploaded that previously showed Tiles
    p_steel_user = Path("backend/uploads/orig_req_f8cfe72b6d9a_WhatsApp_Image_2026-11-11_at_12.21.03_PM_(1).jpeg")
    test_api_upload(p_steel_user, "USER STEEL (Prev Tiles)")
    
    # 2. More Steel images from STEEL folder
    steel_dir = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS\STEEL")
    for f in list(steel_dir.glob("*.jpeg"))[:3]:
        test_api_upload(f, "STEEL DATASET")
        
    print("-" * 95)
    # 3. User's Sand image
    p_sand_user = Path("backend/uploads/orig_req_84b43d787239_WhatsApp_Image_2026-11-11_at_12.20.15_PM.jpeg")
    test_api_upload(p_sand_user, "USER SAND")
    
    # 4. More Sand images from CEMENT BRICKS folder
    sand_dir = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS\CEMENT BRICKS")
    for f in [x for x in sand_dir.glob("*.jpeg") if "12.20.1" in x.name][:2]:
        test_api_upload(f, "SAND DATASET")
        
    print("-" * 95)
    # 5. User's Brick image
    p_brick_user = Path("backend/uploads/orig_req_e202d415eea7_BRICK_CRACK_(100).jpg")
    test_api_upload(p_brick_user, "USER BRICK")
    
    # 6. Cement bricks from CEMENT BRICKS folder
    for f in [x for x in sand_dir.glob("*.jpeg") if "12.20.3" in x.name][:2]:
        test_api_upload(f, "CEMENT BRICK")
        
    print("-" * 95)
    # 7. Cement bags from CEMENT & STEEL folder
    cement_dir = Path(r"c:\Users\91855\Desktop\QIP NOTES\Project\REAL TIME DATASETS\CEMENT & STEEL")
    for f in [x for x in cement_dir.glob("*.jpeg") if "12.21.18" in x.name or "12.21.19" in x.name][:2]:
        test_api_upload(f, "CEMENT BAGS")
        
    print("=" * 95)
