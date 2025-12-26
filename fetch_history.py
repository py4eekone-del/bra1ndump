"""
Fetch channel history — загрузка существующих постов с канала.
Использует Telethon (user API) для доступа к истории.

Для работы нужны API_ID и API_HASH:
1. Зайди на https://my.telegram.org
2. Войди по номеру телефона
3. Перейди в API Development Tools
4. Создай приложение и получи api_id + api_hash
5. Добавь в .env:
   TELEGRAM_API_ID=12345678
   TELEGRAM_API_HASH=abcdef1234567890

Запуск:
    python fetch_history.py
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "py4e2k0ne")
POSTS_FILE = Path(__file__).parent / "posts.json"
PHOTOS_DIR = Path(__file__).parent / "dist" / "photos"
SESSION_FILE = Path(__file__).parent / "session"

# How many messages to fetch (None = all)
LIMIT = 100


async def load_posts() -> list:
    """Load existing posts from JSON."""
    if POSTS_FILE.exists():
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            return json.loads(content) if content else []
    return []


async def save_posts(posts: list):
    """Save posts to JSON."""
    with open(POSTS_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, ensure_ascii=False, indent=2, fp=f)


async def main():
    if not API_ID or not API_HASH:
        print("[ERROR] TELEGRAM_API_ID and TELEGRAM_API_HASH not set!")
        print("Get them from https://my.telegram.org")
        return
    
    print(f"Connecting to Telegram...")
    
    client = TelegramClient(str(SESSION_FILE), int(API_ID), API_HASH)
    await client.start()
    
    print(f"Connected! Fetching posts from @{CHANNEL_USERNAME}...")
    
    # Get channel entity
    channel = await client.get_entity(CHANNEL_USERNAME)
    
    # Fetch messages
    posts = await load_posts()
    existing_ids = {p.get("id") for p in posts}
    
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    
    new_count = 0
    async for message in client.iter_messages(channel, limit=LIMIT):
        if message.id in existing_ids:
            continue
        
        post_data = {
            "id": message.id,
            "date": message.date.strftime("%d.%m.%Y %H:%M:%S"),
            "type": "text",
            "content": message.text or ""
        }
        
        # Handle photo
        if message.photo:
            post_data["type"] = "image"
            filename = f"post_{message.id}.jpg"
            photo_path = PHOTOS_DIR / filename
            
            await client.download_media(message.photo, file=photo_path)
            post_data["image"] = f"photos/{filename}"
            print(f"  [IMG] Downloaded: {filename}")
        
        # Skip empty
        if not post_data["content"] and not post_data.get("image"):
            continue
        
        posts.append(post_data)
        new_count += 1
        print(f"  + Post {message.id}: {post_data['type']}")
    
    # Sort by ID (chronological)
    posts.sort(key=lambda x: x.get("id", 0))
    
    await save_posts(posts)
    
    print(f"\nDone! Added {new_count} new posts.")
    print(f"Total posts in {POSTS_FILE.name}: {len(posts)}")
    
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
