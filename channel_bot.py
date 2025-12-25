"""
Channel Bot — автоматический сбор постов с Telegram канала.
Сохраняет посты в posts.json и может отправлять webhook в n8n.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import aiohttp
import aiofiles

# Import our site generator
import generator

# Load environment variables from .env file
load_dotenv()

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "py4e2k0ne")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")  # Optional
POSTS_FILE = Path(__file__).parent / "posts.json"
PHOTOS_DIR = Path(__file__).parent / "dist" / "photos"
VISITORS_LOG = Path(__file__).parent / "visitors_log.txt"
# =======================================================

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def load_posts() -> list:
    """Load existing posts from JSON file."""
    if POSTS_FILE.exists():
        async with aiofiles.open(POSTS_FILE, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content) if content else []
    return []


async def save_posts(posts: list):
    """Save posts to JSON file."""
    async with aiofiles.open(POSTS_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(posts, ensure_ascii=False, indent=2))
    
    # TRIGGER REBUILD AFTER SAVE
    logger.info("Triggering site rebuild...")
    try:
        generator.rebuild_site()
        logger.info("Site rebuild complete.")
    except Exception as e:
        logger.error(f"Rebuild failed: {e}")


async def send_to_n8n(post_data: dict):
    """Send post data to n8n webhook (if configured)."""
    if not N8N_WEBHOOK_URL:
        return
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(N8N_WEBHOOK_URL, json=post_data) as resp:
                if resp.status == 200:
                    logger.info(f"Sent to n8n: {post_data.get('id')}")
                else:
                    logger.error(f"n8n webhook failed: {resp.status}")
    except Exception as e:
        logger.error(f"n8n webhook error: {e}")


async def download_photo(bot: Bot, file_id: str, post_id: int) -> str | None:
    """Download photo from Telegram and save to photos folder."""
    try:
        # Save to dist/photos directly? Or local cache?
        # Generator expects local relative path.
        # Let's save to 'photos_cache' or similar, then generator copies to dist/photos
        # Actually generator handles local_image path.
        
        # Saving relative to root
        local_dir = Path("dist/photos")
        local_dir.mkdir(parents=True, exist_ok=True)
        
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        ext = Path(file_path).suffix or ".jpg"
        # Unique name
        filename = f"bot_img_{post_id}{ext}"
        target_path = local_dir / filename
        
        await bot.download_file(file_path, target_path)
        logger.info(f"Downloaded photo: {filename}")
        
        return f"dist/photos/{filename}"
    except Exception as e:
        logger.error(f"Failed to download photo: {e}")
        return None

WEBAPP_URL = "https://py4eekone-del.github.io/bra1ndump/"

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command"""
    await send_webapp_button(message)

async def send_webapp_button(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(
            text="посмотреть",
            web_app=types.WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    await message.answer(
        "привет! тут плавает жижа",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


@dp.message()
async def handle_web_app_data(message: types.Message):
    """Handle data from Mini App (visitor tracking)."""
    if message.web_app_data:
        try:
            data = json.loads(message.web_app_data.data)
            if data.get('type') == 'visitor_log':
                # Format: timestamp | ID: xxx | @username | Name | lang
                log_line = f"{data.get('timestamp', 'N/A')} | ID: {data.get('id', 'N/A')} | {data.get('username', 'N/A')} | {data.get('name', 'N/A')} | {data.get('language', 'N/A')}\n"
                
                async with aiofiles.open(VISITORS_LOG, "a", encoding="utf-8") as f:
                    await f.write(log_line)
                
                logger.info(f"👁️ Visitor logged: {data.get('username', 'unknown')}")
                
                # Optional: notify the user
                await message.answer("👁️", parse_mode=None)
                return
        except json.JSONDecodeError:
            pass
    
    # Fallback: if not web_app_data, treat as regular message
    if message.chat.type == "private":
        await send_webapp_button(message)


@dp.channel_post()
async def handle_channel_post(message: types.Message):
    """Handle new posts from the channel."""
    logger.info(f"New channel post: {message.message_id}")
    
    post_data = {
        "id": message.message_id,
        "date": message.date.strftime("%d.%m.%Y %H:%M:%S"),
        "type": "text",
        "content": ""
    }
    
    if message.text:
        post_data["type"] = "text"
        post_data["content"] = message.text
    elif message.caption:
        post_data["content"] = message.caption
    
    if message.photo:
        post_data["type"] = "image"
        largest_photo = message.photo[-1]
        photo_path = await download_photo(bot, largest_photo.file_id, message.message_id)
        if photo_path:
            post_data["image"] = photo_path
    
    if not post_data["content"] and not post_data.get("image"):
        return
    
    posts = await load_posts()
    if any(p.get("id") == post_data["id"] for p in posts):
        return
    
    posts.append(post_data)
    await save_posts(posts) # This triggers rebuild
    
    await send_to_n8n(post_data)


@dp.edited_channel_post()
async def handle_edited_post(message: types.Message):
    """Handle edited posts."""
    logger.info(f"Edited channel post: {message.message_id}")
    
    posts = await load_posts()
    
    for post in posts:
        if post.get("id") == message.message_id:
            if message.text:
                post["content"] = message.text
            elif message.caption:
                post["content"] = message.caption
            
            await save_posts(posts) # This triggers rebuild
            break


async def main():
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set!")
        return
    
    logger.info(f"Starting bot for channel @{CHANNEL_USERNAME}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
