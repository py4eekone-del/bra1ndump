import json
import os

# Absolute paths to be safe
BASE_DIR = r"c:\Users\0n1\Desktop\viewGEN"
EXPORT_PATH = os.path.join(BASE_DIR, "ChatExport_2025-12-24", "result.json")
ARCHIVE_PATH = os.path.join(BASE_DIR, "digital_brain_dump", "archive.json")

def analyze_data():
    print(f"--- ANALYZING SOURCE DATA ---")
    
    # 1. Load Source (Telegram Export)
    if not os.path.exists(EXPORT_PATH):
        print(f"ERROR: Export file not found at {EXPORT_PATH}")
        return

    with open(EXPORT_PATH, 'r', encoding='utf-8') as f:
        export_data = json.load(f)

    messages = export_data.get('messages', [])
    print(f"Total entries in result.json: {len(messages)}")

    valid_export_posts = 0
    skipped_service = 0
    skipped_empty = 0
    
    potential_content = []

    for msg in messages:
        if msg.get('type') != 'message':
            skipped_service += 1
            continue

        # Extract content
        text_content = ""
        text_entity = msg.get('text', "")
        if isinstance(text_entity, list):
            for part in text_entity:
                if isinstance(part, str): text_content += part
                elif isinstance(part, dict): text_content += part.get('text', "")
        else:
            text_content = str(text_entity)

        has_photo = 'photo' in msg
        has_text = bool(text_content.strip())
        
        if not has_photo and not has_text:
            skipped_empty += 1
            continue

        valid_export_posts += 1
        
        # We use date as a rough unique key if ID isn't relied upon (though ID is better)
        potential_content.append({
            'id': msg.get('id'),
            'date': msg.get('date'),
            'has_photo': has_photo,
            'has_text': has_text,
            'text_snippet': text_content[:30].replace('\n', ' ')
        })

    print(f"Service messages (skipped): {skipped_service}")
    print(f"Empty messages (skipped): {skipped_empty}")
    print(f"VALID POST CANDIDATES in Export: {valid_export_posts}")
    print(f"  - With Photos: {sum(1 for x in potential_content if x['has_photo'])}")
    print(f"  - Text Only: {sum(1 for x in potential_content if not x['has_photo'] and x['has_text'])}")

    print(f"\n--- ANALYZING CURRENT ARCHIVE ---")
    if not os.path.exists(ARCHIVE_PATH):
        print("Archive not found.")
        return

    with open(ARCHIVE_PATH, 'r', encoding='utf-8') as f:
        archive_data = json.load(f)

    print(f"Total entries in archive.json: {len(archive_data)}")
    
    # Basic deduplication check
    archive_dates = set(entry.get('date') for entry in archive_data)
    
    missing_count = 0
    for p in potential_content:
        # Note: Export format "2025-05-21T11:23:17" vs Archive "2025-05-21 11:23:17"
        normalized_date = p['date'].replace('T', ' ')
        if normalized_date not in archive_dates:
            missing_count += 1
            # print(f"MISSING IN ARCHIVE: [ID {p['id']}] {normalized_date} - {p['text_snippet']}...")

    print(f"Potential Missing Posts (by exact date match): {missing_count}")

if __name__ == "__main__":
    analyze_data()
