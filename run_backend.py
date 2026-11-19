import uvicorn
import os
import sys

# Ensure current directory is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 60)
    print("Starting AI Construction Material Quality Assessment Backend")
    print("Application URL: http://localhost:8000")
    print("API documentation running at: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
