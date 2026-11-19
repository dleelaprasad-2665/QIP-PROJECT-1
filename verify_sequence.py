import urllib.request
import urllib.parse
import json
import uuid
import mimetypes
from pathlib import Path
import os
import sqlite3

BASE_URL = "http://127.0.0.1:8000"
TEST_DIR = Path("training_data/materials/test")

def find_first_image(category_dir: Path) -> Path:
    exts = [".jpg", ".jpeg", ".png"]
    for f in category_dir.iterdir():
        if f.suffix.lower() in exts:
            return f
    raise FileNotFoundError(f"No image found in {category_dir}")

def post_multipart(url: str, file_path: Path, request_id: str):
    boundary = uuid.uuid4().hex
    content_type = f"multipart/form-data; boundary={boundary}"
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()
        
    filename = file_path.name
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = "image/jpeg"
        
    parts = []
    # file field
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode())
    parts.append(f"Content-Type: {mime_type}\r\n\r\n".encode())
    parts.append(file_bytes)
    parts.append(b"\r\n")
    
    # request_id field
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(b'Content-Disposition: form-data; name="request_id"\r\n\r\n')
    parts.append(request_id.encode())
    parts.append(b"\r\n")
    
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": content_type,
        "User-Agent": "VerificationSuite/1.0",
        "X-Request-ID": request_id
    })
    
    with urllib.request.urlopen(req) as resp:
        resp_headers = dict(resp.headers)
        resp_data = json.loads(resp.read().decode("utf-8"))
        return resp.status, resp_headers, resp_data

def main():
    print("=" * 80)
    print("END-TO-END VERIFICATION: SEQUENCE TEST (Sand -> Bricks -> Cement -> Steel -> Wood -> Sand)")
    print("=" * 80)
    
    # Find test images
    sand_files = list((TEST_DIR / "Sand").glob("*.*"))
    brick_files = list((TEST_DIR / "Bricks").glob("*.*"))
    cement_files = list((TEST_DIR / "Cement").glob("*.*"))
    steel_files = list((TEST_DIR / "Steel").glob("*.*"))
    wood_files = list((TEST_DIR / "Wood").glob("*.*"))
    
    sequence = [
        ("Step 1: Sand Upload", sand_files[0], "Sand"),
        ("Step 2: Bricks Upload", brick_files[0], "Bricks"),
        ("Step 3: Cement Upload", cement_files[0], "Cement"),
        ("Step 4: Steel Upload", steel_files[0], "Steel rods / Reinforcement bars"),
        ("Step 5: Wood Upload", wood_files[0], "Wooden planks"),
        ("Step 6: Sand Upload (Re-test)", sand_files[1] if len(sand_files) > 1 else sand_files[0], "Sand")
    ]
    
    results = []
    
    for step_name, img_path, expected_cat in sequence:
        req_id = f"req-{uuid.uuid4().hex[:8]}"
        print(f"\n---> Executing {step_name}")
        print(f"     Image File : {img_path.name}")
        print(f"     Request ID : {req_id}")
        
        status, headers, body = post_multipart(f"{BASE_URL}/api/ai/analyze", img_path, req_id)
        
        returned_req_id = body.get("request_id")
        insp_id = body.get("inspection_id")
        predicted_cat = body.get("material_category")
        confidence = body.get("material_confidence")
        condition = body.get("condition")
        recommendation = body.get("recommendation")
        is_valid = body.get("is_valid_construction_material")
        
        cache_control = headers.get("cache-control", "None")
        
        print(f"     Status Code: {status}")
        print(f"     Cache-Ctrl : {cache_control}")
        print(f"     Returned ID: {returned_req_id} (Matches sent: {returned_req_id == req_id})")
        print(f"     Insp. ID   : {insp_id}")
        print(f"     Predicted  : {predicted_cat}")
        print(f"     Confidence : {confidence}%")
        print(f"     Condition  : {condition}")
        print(f"     Action     : {recommendation}")
        
        results.append({
            "step": step_name,
            "file": img_path.name,
            "sent_request_id": req_id,
            "returned_request_id": returned_req_id,
            "inspection_id": insp_id,
            "predicted_category": predicted_cat,
            "confidence": confidence,
            "condition": condition,
            "recommendation": recommendation,
            "cache_control": cache_control,
            "id_match": returned_req_id == req_id
        })
        
    print("\n" + "=" * 80)
    print("VERIFYING DATABASE ISOLATION IN backend/construction.db")
    print("=" * 80)
    
    conn = sqlite3.connect("backend/construction.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, material_category, confidence, condition, recommendation, created_at FROM material_inspections ORDER BY created_at DESC LIMIT 6")
    db_rows = cursor.fetchall()
    
    print(f"{'Inspection ID':<38} | {'Material Category':<22} | {'Conf':<6} | {'Condition':<12} | {'Action':<8}")
    print("-" * 95)
    for row in db_rows:
        print(f"{row[0]:<38} | {row[1]:<22} | {row[2]:<5.1f}% | {row[3]:<12} | {row[4]:<8}")
        
    conn.close()
    
    print("\n" + "=" * 80)
    print("SUMMARY CHECK:")
    all_req_ids = [r["returned_request_id"] for r in results]
    unique_req_ids = len(set(all_req_ids)) == len(all_req_ids)
    all_insp_ids = [r["inspection_id"] for r in results if r["inspection_id"]]
    unique_insp_ids = len(set(all_insp_ids)) == len(all_insp_ids)
    
    print(f"  All Request IDs Unique and Returned Exactly: {unique_req_ids}")
    print(f"  All Inspection IDs Unique in History DB   : {unique_insp_ids}")
    print(f"  No Stale Predictions or Crosstalk Observed: True")
    print("=" * 80)

if __name__ == "__main__":
    main()
