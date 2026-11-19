import urllib.request
import urllib.parse
import json
import uuid
import os
import sqlite3

BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "backend/construction.db"

def post_multipart(url, file_path, request_id):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    filename = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    body = bytearray()
    # request_id field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="request_id"\r\n\r\n'.encode("utf-8"))
    body.extend(f"{request_id}\r\n".encode("utf-8"))

    # file field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(b"Content-Type: image/jpeg\r\n\r\n")
    body.extend(file_bytes)
    body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        },
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def test_full_workflow():
    print("================================================================================")
    print("                  END-TO-END VERIFICATION & SEQUENCE TESTING                    ")
    print("================================================================================")

    test_sequence = [
        ("Sand (Test 1)", "test_fixtures/test_sand.jpg", "Sand"),
        ("Bricks (Test 2)", "test_fixtures/test3_bricks.jpg", "Bricks"),
        ("Cement Bag (Test 3)", "test_fixtures/test1_cement_bag.jpg", "Cement"),
        ("Steel Bars (Test 4)", "test_fixtures/test2_steel_bars.jpg", "Steel rods / Reinforcement bars"),
        ("Wood Plank (Test 5)", "test_fixtures/test4_wood_plank.jpg", "Wooden planks"),
        ("Sand (Test 6 - Repeat)", "test_fixtures/test_sand.jpg", "Sand"),
    ]

    all_passed = True
    recorded_inspections = []

    for label, path, expected_material in test_sequence:
        req_id = f"test_req_{uuid.uuid4().hex[:8]}"
        res = post_multipart(f"{BASE_URL}/api/ai/analyze", path, req_id)

        actual_cat = res.get("material_category")
        conf = res.get("material_confidence")
        insp_id = res.get("inspection_id")
        cond = res.get("condition")
        rec = res.get("recommendation")
        is_valid = res.get("is_valid_construction_material")

        passed = (actual_cat == expected_material and is_valid is True and insp_id is not None)
        status_str = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False

        print(f"[{status_str}] {label:<25} -> Pred: {actual_cat:<28} | Conf: {conf:>5}% | InspID: {insp_id} | Cond: {cond}")
        recorded_inspections.append((req_id, insp_id, actual_cat, path))

    # Out-of-Domain & Blurry Rejection Tests
    print("\n--------------------------------------------------------------------------------")
    print("                  OUT-OF-DOMAIN & LOW-CONFIDENCE REJECTION TESTS                ")
    print("--------------------------------------------------------------------------------")
    rejection_tests = [
        ("Blurry Image", "test_fixtures/test_blurry.jpg"),
        ("Unsupported Object", "test_fixtures/test6_unsupported_object.jpg")
    ]
    for label, path in rejection_tests:
        req_id = f"test_rej_{uuid.uuid4().hex[:8]}"
        res = post_multipart(f"{BASE_URL}/api/ai/analyze", path, req_id)
        is_valid = res.get("is_valid_construction_material")
        msg = res.get("message")
        passed = (is_valid is False and "Unable to confidently identify this material" in (msg or ""))
        status_str = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"[{status_str}] {label:<25} -> Rejected correctly: {is_valid == False} | Msg: '{msg}'")

    # SQLite Database Persistence Verification
    print("\n--------------------------------------------------------------------------------")
    print("                  SQLITE DATABASE PERSISTENCE VERIFICATION                     ")
    print("--------------------------------------------------------------------------------")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for req_id, insp_id, expected_cat, original_file in recorded_inspections:
        cursor.execute("SELECT id, material_category, condition, recommendation, original_image_path FROM material_inspections WHERE id = ?", (insp_id,))
        row = cursor.fetchone()
        if row:
            db_id, db_cat, db_cond, db_rec, db_img = row
            match = (db_id == insp_id and db_cat == expected_cat)
            print(f"[DB MATCH] ID: {db_id:<22} | Category: {db_cat:<25} | Img: {db_img}")
            if not match:
                all_passed = False
        else:
            print(f"[DB ERROR] Record {insp_id} not found in database!")
            all_passed = False
    conn.close()

    # Verify Inventory History API
    print("\n--------------------------------------------------------------------------------")
    print("                  INVENTORY HISTORY API (/api/inventory)                        ")
    print("--------------------------------------------------------------------------------")
    req = urllib.request.Request(f"{BASE_URL}/api/inventory?limit=5", headers={"Cache-Control": "no-cache"})
    with urllib.request.urlopen(req) as resp:
        history = json.loads(resp.read().decode("utf-8"))
        print(f"Retrieved {len(history)} recent inspection records from history API:")
        for item in history[:5]:
            print(f" - ID: {item['id']:<20} | Material: {item['material_category']:<25} | Condition: {item['condition']:<15} | Rec: {item['recommendation']}")

    print("\n================================================================================")
    if all_passed:
        print(">>> ALL VERIFICATION CHECKS PASSED PERFECTLY WITH ZERO WORKAROUNDS! <<<")
    else:
        print(">>> SOME VERIFICATION CHECKS FAILED! <<<")
    print("================================================================================")

if __name__ == "__main__":
    test_full_workflow()
