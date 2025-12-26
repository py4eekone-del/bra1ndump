# Digital Brain Dump — Architecture & Usage

## 🧠 Overview
This project visualizes a Telegram channel as a "Digital Brain Dump" — an interactive, chaotic memory board.
It automatically syncing new posts from Telegram to a GitHub Pages website.

## 📁 Critical Files
*   **`channel_bot.py`**: The "Hands". Runs 24/7. Listens for new posts in the channel, saves them to `posts.json`, and triggers `generator.py`.
*   **`generator.py`**: The "Brain". Reads posts from three sources and rebuilds `index.html`:
    1.  `posts.json` (New live posts from bot)
    2.  `archive.json` (Restored history from older versions)
    3.  `ChatExport_*` folders (Telegram exports)
    *   *Do NOT delete `archive.json` unless you have a full fresh export!*
*   **`posts.json`**: Temporary storage for the bot's latest posts.
*   **`archive.json`**: Contains historical posts rescued from previous site versions.

## 🚀 How It Works
1.  **You post in Telegram** -> Bot sees it.
2.  Bot saves to `posts.json`.
3.  Bot runs `generator.py`.
4.  Generator merges all sources, fixes duplicates, processes images (renaming to `img_TIMESTAMP_HASH.jpg`), and builds `index.html`.
5.  Generator runs `git push` to deploy to GitHub Pages.

## 🛠 Usage
### Starting the Bot
```bash
python channel_bot.py
```
Ensure your `.env` has `BOT_TOKEN`.

### Manual Rebuild
If you want to force an update without a new post:
```bash
python generator.py
```

## 🔧 Maintenance
*   **GitHub Pages**: `dist/` is the web root. `index.html` + `photos/` folder.
*   **Images**: Stored in `dist/photos`. Do not manually rename them; the generator handles this to prevent collisions.
