import urllib.request
import uuid
import json
from pathlib import Path

def test_upload(path: Path):
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
        print(f"File: {path.name}")
        print(f"  -> Predicted Category  : {res['material_category']}")
        print(f"  -> Confidence          : {res['material_confidence']}%")
        print(f"  -> Condition           : {res['condition']}")
        print(f"  -> Recommendation      : {res['recommendation']}")
        print(f"  -> Request ID          : {res['request_id']}")
        print(f"  -> Inspection ID       : {res.get('inspection_id')}")

if __name__ == "__main__":
    print("Testing Live API on User's Uploaded Images:")
    print("=" * 60)
    p_sand = Path("backend/uploads/orig_req_84b43d787239_WhatsApp_Image_2026-11-11_at_12.20.15_PM.jpeg")
    p_brick = Path("backend/uploads/orig_req_e202d415eea7_BRICK_CRACK_(100).jpg")
    
    test_upload(p_sand)
    print("-" * 60)
    test_upload(p_brick)
    print("=" * 60)
