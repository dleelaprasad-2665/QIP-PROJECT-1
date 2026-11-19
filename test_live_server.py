import urllib.request
import json
import os
import sys
import uuid

sys.stdout.reconfigure(line_buffering=True)

URL = "http://localhost:8000/api/ai/analyze"

test_files = [
    ("USER STEEL 1       ", "backend/uploads/orig_req_f8cfe72b6d9a_WhatsApp_Image_2026-11-11_at_12.21.03_PM_(1).jpeg"),
    ("USER STEEL 2       ", "c:/Users/91855/Desktop/QIP NOTES/Project/REAL TIME DATASETS/STEEL/WhatsApp Image 2026-11-11 at 12.20.59 PM (1).jpeg"),
    ("USER SAND          ", "backend/uploads/orig_req_84b43d787239_WhatsApp_Image_2026-11-11_at_12.20.15_PM.jpeg"),
    ("USER RED BRICK     ", "backend/uploads/orig_req_79a6acfcca92_MAA-Brick.jpg"),
    ("USER CEMENT BRICK  ", "backend/uploads/orig_req_ac464f8ef160_WhatsApp_Image_2026-11-11_at_12.20.30_PM_(1).jpeg"),
    ("USER CEMENT BAG 1  ", "backend/uploads/orig_req_120101b40e6a_WhatsApp_Image_2026-11-11_at_12.21.19_PM.jpeg"),
    ("USER CEMENT BAG 2  ", "backend/uploads/orig_req_df6f46923156_WhatsApp_Image_2026-11-11_at_12.21.27_PM.jpeg")
]

def post_multipart(url, file_path):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    filename = os.path.basename(file_path)
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    lines = [
        f"--{boundary}".encode(),
        f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode(),
        b"Content-Type: image/jpeg",
        b"",
        file_bytes,
        f"--{boundary}--".encode(),
        b""
    ]
    body = b"\r\n".join(lines)
    
    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Content-Length", str(len(body)))
    
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.status, json.loads(response.read().decode())

print("=" * 115)
print("FINAL LIVE HTTP VERIFICATION (ALL 4 CORE MATERIALS INCLUDING STEEL)")
print("=" * 115)

for label, fpath in test_files:
    if not os.path.exists(fpath):
        print(f"[{label}] File not found: {fpath}")
        continue
    try:
        status, data = post_multipart(URL, fpath)
        mat = data.get("material_category")
        conf = data.get("material_confidence", 0.0)
        cond = data.get("condition")
        rec = data.get("recommendation")
        insp_id = data.get("inspection_id")
        defects = len(data.get("detected_defects", []))
        print(f"[{label}] -> HTTP {status} | ID: {str(insp_id):<18} | Category: {mat:<32} | Conf: {conf:4.1f}% | Cond: {cond:<10} | Rec: {rec:<7} | Defects: {defects}")
    except Exception as e:
        print(f"[{label}] -> Error: {e}")

print("=" * 115)
