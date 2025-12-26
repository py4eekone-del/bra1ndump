import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTOS_DIR = os.path.join(BASE_DIR, "photos")
ARCHIVE_JSON = os.path.join(BASE_DIR, "archive.json")

def check_paths():
    print(f"Scanning {PHOTOS_DIR}...")
    try:
        real_files = os.listdir(PHOTOS_DIR)
        print(f"Found {len(real_files)} files in photos dir.")
    except Exception as e:
        print(f"Error listing photos dir: {e}")
        return

    print(f"Reading {ARCHIVE_JSON}...")
    try:
        with open(ARCHIVE_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading archive: {e}")
        return

    print("Checking matches...")
    for item in data:
        content = item.get('content')
        if content and content.startswith('photos/'):
            # Extract filename from "photos/filename"
            json_fname = os.path.basename(content)
            
            if json_fname in real_files:
                print(f"[OK] Found: {json_fname}")
            else:
                print(f"[MISSING] {json_fname}")
                print(f"   JSON repr: {repr(json_fname)}")
                # Find candidates
                prefix = json_fname.split('@')[0]
                for rf in real_files:
                    if rf.startswith(prefix):
                        print(f"   Candidate on disk: {rf}")
                        print(f"   Disk repr:         {repr(rf)}")
                        if len(rf) != len(json_fname):
                             print(f"   Length mistmatch: {len(rf)} vs {len(json_fname)}")
                        for i, (c1, c2) in enumerate(zip(rf, json_fname)):
                             if c1 != c2:
                                 print(f"   Diff at index {i}: '{c1}' ({ord(c1)}) vs '{c2}' ({ord(c2)})")
                                 break
    
    print("Done.")

if __name__ == "__main__":
    check_paths()
