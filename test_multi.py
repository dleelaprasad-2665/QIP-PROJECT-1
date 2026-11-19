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
        print(f"[{path.parent.name:<8}] {path.name[:35]:<35} -> {res['material_category']} ({res['material_confidence']}%)")

if __name__ == "__main__":
    print("Verifying Multiple Sand and Brick Images on Port 8000:")
    print("=" * 70)
    for p in list(Path("training_data/materials/test/Sand").glob("*.*")):
        test_upload(p)
    print("-" * 70)
    for p in list(Path("training_data/materials/test/Bricks").glob("*.*"))[:4]:
        test_upload(p)
    print("=" * 70)
