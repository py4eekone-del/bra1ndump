import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_JSON = os.path.join(BASE_DIR, "archive.json")
PHOTOS_DIR = os.path.join(BASE_DIR, "photos")

def cleanup():
    print(f"Reading {ARCHIVE_JSON}...")
    try:
        with open(ARCHIVE_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading archive: {e}")
        return

    real_files = set(os.listdir(PHOTOS_DIR))
    print(f"Found {len(real_files)} files on disk.")

    new_data = []
    removed_count = 0
    
    for item in data:
        if item.get('type') == 'image':
            content = item.get('content')
            if content and content.startswith('photos/'):
                fname = os.path.basename(content)
                if fname in real_files:
                    new_data.append(item)
                else:
                    print(f"Removing missing photo: {fname}")
                    removed_count += 1
            else:
                # Keep images without local path (if any?) or handle logic
                # Assuming all local images have photos/ prefix
                new_data.append(item) 
        else:
            # Keep text posts
            new_data.append(item)

    print(f"Removed {removed_count} missing items.")
    print(f"Remaining items: {len(new_data)}")

    with open(ARCHIVE_JSON, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    print("Archive updated.")

if __name__ == "__main__":
    cleanup()
