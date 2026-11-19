import os
import json
import urllib.request
import urllib.parse
import mimetypes
import uuid

API_URL = "http://localhost:8000/api/ai/analyze"

def post_multipart(url, file_path, request_id=None):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    filename = os.path.basename(file_path)
    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    body = bytearray()
    
    # file field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
    body.extend(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
    with open(file_path, "rb") as f:
        body.extend(f.read())
    body.extend(b"\r\n")

    # request_id field
    if request_id:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="request_id"\r\n\r\n'.encode("utf-8"))
        body.extend(f"{request_id}\r\n".encode("utf-8"))

    # site_location field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="site_location"\r\n\r\n'.encode("utf-8"))
    body.extend(b"Central Yard A\r\n")

    # project_name field
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(f'Content-Disposition: form-data; name="project_name"\r\n\r\n'.encode("utf-8"))
    body.extend(b"EcoBuild Site 1\r\n")

    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(url, data=bytes(body), method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Cache-Control", "no-cache, no-store, must-revalidate")

    with urllib.request.urlopen(req) as resp:
        headers = dict(resp.headers)
        res_data = json.loads(resp.read().decode("utf-8"))
        return res_data, headers

def run_all_tests():
    print("=" * 70)
    print("RUNNING CRITICAL AI PREDICTION VERIFICATION TESTS")
    print("=" * 70)

    results = []

    # Test 1: Cement bag image -> Cement
    req1_id = f"req_test1_{uuid.uuid4().hex[:6]}"
    res1, hdr1 = post_multipart(API_URL, "test_fixtures/test1_cement_bag.jpg", req1_id)
    is_cement = (res1.get("material_category") == "Cement" and res1.get("is_valid_construction_material") is True)
    results.append(("Test 1: Cement bag", is_cement, res1.get("material_category"), res1.get("material_confidence"), res1.get("request_id")))
    print(f"[TEST 1] Cement Bag Upload:")
    print(f"  Category: {res1.get('material_category')} (Expected: Cement)")
    print(f"  Confidence: {res1.get('material_confidence')}%")
    print(f"  Valid Material: {res1.get('is_valid_construction_material')}")
    print(f"  Request ID: {res1.get('request_id')} (Echoed: {res1.get('request_id') == req1_id})")
    print(f"  Cache-Control Header: {hdr1.get('cache-control')}")
    print(f"  Result: {'PASS' if is_cement else 'FAIL'}\n")

    # Test 2: Steel reinforcement image -> Steel bars
    req2_id = f"req_test2_{uuid.uuid4().hex[:6]}"
    res2, hdr2 = post_multipart(API_URL, "test_fixtures/test2_steel_bars.jpg", req2_id)
    is_steel = ("Steel" in res2.get("material_category", "") and res2.get("is_valid_construction_material") is True)
    results.append(("Test 2: Steel bars", is_steel, res2.get("material_category"), res2.get("material_confidence"), res2.get("request_id")))
    print(f"[TEST 2] Steel Reinforcement Upload:")
    print(f"  Category: {res2.get('material_category')} (Expected: Steel rods / Reinforcement bars)")
    print(f"  Confidence: {res2.get('material_confidence')}%")
    print(f"  Valid Material: {res2.get('is_valid_construction_material')}")
    print(f"  Request ID: {res2.get('request_id')}")
    print(f"  Result: {'PASS' if is_steel else 'FAIL'}\n")

    # Test 3: Brick image -> Bricks
    req3_id = f"req_test3_{uuid.uuid4().hex[:6]}"
    res3, hdr3 = post_multipart(API_URL, "test_fixtures/test3_bricks.jpg", req3_id)
    is_brick = (res3.get("material_category") == "Bricks" and res3.get("is_valid_construction_material") is True)
    results.append(("Test 3: Bricks", is_brick, res3.get("material_category"), res3.get("material_confidence"), res3.get("request_id")))
    print(f"[TEST 3] Brick Upload:")
    print(f"  Category: {res3.get('material_category')} (Expected: Bricks)")
    print(f"  Confidence: {res3.get('material_confidence')}%")
    print(f"  Valid Material: {res3.get('is_valid_construction_material')}")
    print(f"  Result: {'PASS' if is_brick else 'FAIL'}\n")

    # Test 4: Wooden plank image -> Wood
    req4_id = f"req_test4_{uuid.uuid4().hex[:6]}"
    res4, hdr4 = post_multipart(API_URL, "test_fixtures/test4_wood_plank.jpg", req4_id)
    is_wood = ("Wood" in res4.get("material_category", "") and res4.get("is_valid_construction_material") is True)
    results.append(("Test 4: Wooden planks", is_wood, res4.get("material_category"), res4.get("material_confidence"), res4.get("request_id")))
    print(f"[TEST 4] Wooden Plank Upload:")
    print(f"  Category: {res4.get('material_category')} (Expected: Wooden planks)")
    print(f"  Confidence: {res4.get('material_confidence')}%")
    print(f"  Valid Material: {res4.get('is_valid_construction_material')}")
    print(f"  Result: {'PASS' if is_wood else 'FAIL'}\n")

    # Test 5: Tile image -> Tiles
    req5_id = f"req_test5_{uuid.uuid4().hex[:6]}"
    res5, hdr5 = post_multipart(API_URL, "test_fixtures/test5_tiles.jpg", req5_id)
    is_tile = (res5.get("material_category") == "Tiles" and res5.get("is_valid_construction_material") is True)
    results.append(("Test 5: Tiles", is_tile, res5.get("material_category"), res5.get("material_confidence"), res5.get("request_id")))
    print(f"[TEST 5] Tile Upload:")
    print(f"  Category: {res5.get('material_category')} (Expected: Tiles)")
    print(f"  Confidence: {res5.get('material_confidence')}%")
    print(f"  Valid Material: {res5.get('is_valid_construction_material')}")
    print(f"  Result: {'PASS' if is_tile else 'FAIL'}\n")

    # Test 6: Unsupported / Non-construction object -> Unknown / Not recognized
    req6_id = f"req_test6_{uuid.uuid4().hex[:6]}"
    res6, hdr6 = post_multipart(API_URL, "test_fixtures/test6_unsupported_object.jpg", req6_id)
    is_unsupported = (res6.get("is_valid_construction_material") is False and "Unable to confidently identify this material" in res6.get("message", ""))
    results.append(("Test 6: Unsupported Object", is_unsupported, res6.get("material_category"), res6.get("message"), res6.get("request_id")))
    print(f"[TEST 6] Unsupported Non-Construction Object Upload:")
    print(f"  Valid Material: {res6.get('is_valid_construction_material')} (Expected: False)")
    print(f"  Message: {res6.get('message')}")
    print(f"  Condition: {res6.get('condition')}")
    print(f"  Recommendation: {res6.get('recommendation')}")
    print(f"  Result: {'PASS' if is_unsupported else 'FAIL'}\n")

    # Blurry image test
    res_blur, _ = post_multipart(API_URL, "test_fixtures/test_blurry.jpg")
    is_blur_rejected = (res_blur.get("is_valid_construction_material") is False and "Unable to confidently identify this material" in res_blur.get("message", ""))
    print(f"[TEST 6B] Blurry Image Upload:")
    print(f"  Valid Material: {res_blur.get('is_valid_construction_material')} (Expected: False)")
    print(f"  Message: {res_blur.get('message')}")
    print(f"  Result: {'PASS' if is_blur_rejected else 'FAIL'}\n")

    # Test 7: Upload sequence: Cement -> Steel -> Cement again
    print("[TEST 7] Sequence Upload Test (Cement -> Steel -> Cement):")
    seq_res1, _ = post_multipart(API_URL, "test_fixtures/test1_cement_bag.jpg", "seq_1")
    print(f"  Step 1 Upload Cement: Category = {seq_res1.get('material_category')}")

    seq_res2, _ = post_multipart(API_URL, "test_fixtures/test2_steel_bars.jpg", "seq_2")
    print(f"  Step 2 Upload Steel:  Category = {seq_res2.get('material_category')}")

    seq_res3, _ = post_multipart(API_URL, "test_fixtures/test1_cement_bag.jpg", "seq_3")
    print(f"  Step 3 Upload Cement: Category = {seq_res3.get('material_category')}")

    is_seq_valid = (
        seq_res1.get("material_category") == "Cement" and
        "Steel" in seq_res2.get("material_category", "") and
        seq_res3.get("material_category") == "Cement" and
        seq_res1.get("request_id") == "seq_1" and
        seq_res2.get("request_id") == "seq_2" and
        seq_res3.get("request_id") == "seq_3"
    )
    results.append(("Test 7: Sequence (Cement->Steel->Cement)", is_seq_valid, f"{seq_res1.get('material_category')} -> {seq_res2.get('material_category')} -> {seq_res3.get('material_category')}", None, None))
    print(f"  Result: {'PASS' if is_seq_valid else 'FAIL'}\n")

    print("=" * 70)
    print("SUMMARY OF TEST RESULTS")
    print("=" * 70)
    all_passed = True
    for name, passed, cat, conf, req_id in results:
        status_str = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"  {status_str:4s} | {name:40s} | Category: {str(cat):20s} | Conf: {str(conf)}")

    print(f"\nOVERALL RESULT: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

if __name__ == "__main__":
    run_all_tests()
