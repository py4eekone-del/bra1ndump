import json
import os
from datetime import datetime

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_text_content(msg):
    text_obj = msg.get('text', '')
    if isinstance(text_obj, list):
        # Extract text from list of entities/strings
        content = ""
        for item in text_obj:
            if isinstance(item, str):
                content += item
            elif isinstance(item, dict) and 'text' in item:
                content += item['text']
        return content
    return str(text_obj)

def main():
    archive_path = 'archive.json'
    export_path = 'ChatExport_2025-12-24/result.json' # adjusted path based on previous `dir` command which showed it in ../ChatExport but I'll use absolute logic if needed. 
    # Actually, the user's workspace is `c:\Users\0n1\Desktop\viewGEN\digital_brain_dump`.
    # The export is in `c:\Users\0n1\Desktop\viewGEN\ChatExport_2025-12-24\result.json`.
    # So relative to the workspace, it is `../ChatExport_2025-12-24/result.json`.
    
    # Let's use absolute paths to be safe.
    base_dir = r'c:\Users\0n1\Desktop\viewGEN'
    archive_full_path = os.path.join(base_dir, 'digital_brain_dump', 'archive.json')
    export_full_path = os.path.join(base_dir, 'ChatExport_2025-12-24', 'result.json')

    print(f"Loading archive from: {archive_full_path}")
    archive = load_json(archive_full_path)
    
    print(f"Loading export from: {export_full_path}")
    export = load_json(export_full_path)

    # Create a set of existing texts to avoid duplicates
    existing_texts = set()
    for item in archive:
        if item.get('content') and item.get('type') == 'text':
             existing_texts.add(item['content'].strip())

    new_posts = []
    
    print(f"Found {len(existing_texts)} existing text posts in archive.")

    for msg in export.get('messages', []):
        if msg['type'] != 'message':
            continue
            
        # Skip if it has a photo (handled separate)
        if 'photo' in msg:
            continue
            
        text_content = get_text_content(msg).strip()
        
        if not text_content:
            continue
            
        # Check duplicates
        if text_content in existing_texts:
            continue
            
        # Prepare new entry
        date_str = msg['date'].replace('T', ' ')
        
        new_entry = {
            "type": "text",
            "content": text_content,
            "date": date_str,
            "image": None
        }
        
        new_posts.append(new_entry)
        existing_texts.add(text_content) # Prevent duplicates within the import itself

    if new_posts:
        print(f"Found {len(new_posts)} NEW text posts.")
        archive.extend(new_posts)
        # Sort by date
        archive.sort(key=lambda x: x['date'])
        
        save_json(archive_full_path, archive)
        print("Archive updated successfully.")
    else:
        print("No new text posts found.")

if __name__ == "__main__":
    main()
