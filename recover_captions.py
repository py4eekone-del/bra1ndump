import json
import os
import re
from bs4 import BeautifulSoup

# Paths
BASE_DIR = r"c:\Users\0n1\Desktop\viewGEN"
EXPORT_PATH = os.path.join(BASE_DIR, "ChatExport_2025-12-24", "result.json")
ARCHIVE_PATH = os.path.join(BASE_DIR, "digital_brain_dump", "archive.json")
INDEX_PATH = os.path.join(BASE_DIR, "digital_brain_dump", "index.html")

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_text_from_msg(msg):
    text_obj = msg.get('text', '')
    if isinstance(text_obj, list):
        content = ""
        for item in text_obj:
            if isinstance(item, str):
                content += item
            elif isinstance(item, dict) and 'text' in item:
                content += item['text']
        return content
    return str(text_obj)

def normalize_date(d):
    # Archive: "2025-05-23 11:09:23"
    # Export: "2025-05-23T11:09:23"
    return d.replace('T', ' ')

def main():
    print("Loading data...")
    export = load_json(EXPORT_PATH)
    archive = load_json(ARCHIVE_PATH)
    
    # Map export messages by date for quick lookup
    export_map = {}
    for msg in export.get('messages', []):
        if msg.get('type') == 'message':
            d = normalize_date(msg['date'])
            export_map[d] = msg

    start_update_count = 0
    
    # 1. Update archive.json
    for entry in archive:
        if entry.get('type') == 'image':
            date_key = entry.get('date')
            if date_key in export_map:
                msg = export_map[date_key]
                caption = get_text_from_msg(msg).strip()
                if caption:
                    print(f"Found caption for {date_key}: {caption[:30]}...")
                    entry['caption'] = caption
                    start_update_count += 1
    
    if start_update_count > 0:
        print(f"Updating {start_update_count} entries in archive.json...")
        save_json(ARCHIVE_PATH, archive)
    else:
        print("No new captions found.")

    # 2. Update index.html directly
    print("Updating index.html...")
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    blocks = soup.find_all('div', class_='memory-block')
    
    html_updates = 0
    for block in blocks:
        ts = block.get('data-ts')
        if not ts:
            # Try to find timestamp inside span
            ts_span = block.find('span', class_='timestamp')
            if ts_span:
                ts = ts_span.get_text().strip()
                # Normalize format if needed, but usually it matches
        
        if ts:
            # 2025-12-19 22:24:40
            # Look up in our updated archive (or export map)
            if ts in export_map:
                msg = export_map[ts]
                caption = get_text_from_msg(msg).strip()
                
                # Only inject if there is caption AND the block has an image (to avoid duping text posts)
                # Text posts typically don't have an img tag in this structure, or already have text.
                # Let's check if the .memory-text div is empty.
                text_div = block.find('div', class_='memory-text')
                img_tag = block.find('img')

                if text_div and not text_div.get_text(strip=True) and caption:
                     # Check if it is an image post (img tag exists) or just missing text
                     # Actually, if text div is empty and we found text, we should probably add it regardless,
                     # assuming it's the missing caption.
                     text_div.string = caption
                     html_updates += 1
                     # print(f"HTML injected caption for {ts}")

    if html_updates > 0:
        print(f"Injected {html_updates} captions into index.html")
        with open(INDEX_PATH, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    else:
        print("No HTML updates needed.")

if __name__ == "__main__":
    main()
