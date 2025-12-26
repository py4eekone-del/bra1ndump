import os
import re
import random
import shutil
import time
import subprocess
import hashlib
from bs4 import BeautifulSoup

# Configuration
EXPORT_GLOB = "ChatExport_*" 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

OUTPUT_DIR = "dist"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "index.html")
PHOTOS_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "photos")
POSTS_JSON = "posts.json"
ARCHIVE_JSON = "archive.json"

# ============================================================
# CRYOGENIC GLITCH / AQUATIC BRUTALISM
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>DIGITAL BRAIN DUMP</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&display=swap');
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            background: linear-gradient(180deg, #020615 0%, #0a1628 30%, #0d2847 60%, #0a1e3a 100%);
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            overflow: hidden;
            width: 100vw; height: 100vh; position: relative;
        }

        .video-bg {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            object-fit: cover; z-index: 0; opacity: 0.35;
            transform: scaleY(-1);
            filter: saturate(0.7) contrast(1.1) hue-rotate(-10deg);
            pointer-events: none;
        }

        .caustics {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; z-index: 1; opacity: 0.3;
            background: radial-gradient(ellipse 80% 50% at 20% 30%, rgba(255, 180, 100, 0.2) 0%, transparent 50%),
                        radial-gradient(ellipse 60% 40% at 70% 60%, rgba(255, 200, 150, 0.15) 0%, transparent 45%);
            animation: causticDrift 15s ease-in-out infinite alternate;
            mix-blend-mode: screen;
        }
        
        @keyframes causticDrift {
            0% { transform: translate(0, 0) scale(1); filter: blur(30px); }
            100% { transform: translate(-2%, 3%) scale(0.98); filter: blur(35px); }
        }

        #canvas { position: relative; width: 100%; height: 100%; z-index: 1; overflow-y: auto; overflow-x: hidden; }

        .memory-block {
            position: absolute;
            background: rgba(100, 150, 200, 0.05);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            border-radius: 2px; padding: 8px 10px;
            max-width: 240px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            user-select: none;
            animation: iceFloat var(--float-duration, 10s) ease-in-out infinite;
            animation-delay: var(--float-delay, 0s);
        }

        @keyframes iceFloat {
            0%, 100% { transform: translate(0, 0) rotate(0deg); }
            50% { transform: translate(calc(var(--drift-x, 15px) * -0.7), calc(var(--drift-y, -20px) * 0.5)) rotate(-0.3deg); }
        }

        .memory-block:hover {
            z-index: 9999 !important; cursor: grab; animation-play-state: paused;
            box-shadow: 0 0 20px rgba(100, 200, 255, 0.3), 0 8px 32px rgba(0, 0, 0, 0.5);
        }
        
        .memory-block.dragging { cursor: grabbing; animation-play-state: paused; transform: scale(1.03) !important; }

        .memory-block img { max-width: 200px; height: auto; display: block; filter: saturate(0.85) contrast(1.05); }
        .memory-text { font-size: 11px; line-height: 1.5; color: rgba(200, 230, 255, 0.9); }
        .timestamp { font-size: 9px; color: rgba(150, 180, 220, 0.6); margin-bottom: 6px; display: block; text-transform: uppercase; }

        @media (max-width: 768px) {
            .video-bg { opacity: 0.25; }
            #canvas { display: flex; flex-wrap: wrap; padding: 10px; min-height: 100vh; }
            
            /* Show ALL blocks in a grid on mobile */
            .memory-block {
                position: relative !important;
                display: block !important;
                float: left;
                width: 46%; margin: 2%;
                left: auto !important; top: auto !important;
                max-width: none;
                animation: none;
                background: rgba(20, 40, 80, 0.4);
            }
            .memory-text { font-size: 10px; }
            .memory-block img { max-width: 100%; }
        }
    </style>
</head>
<body>
    <video class="video-bg" autoplay muted loop playsinline><source src="bg.mp4" type="video/mp4"></video>
    <div class="caustics"></div>
    <div id="canvas"><!-- INJECT_CONTENT_HERE --></div>
    <script>
        if (window.Telegram && window.Telegram.WebApp) { Telegram.WebApp.ready(); Telegram.WebApp.expand(); }
        const blocks = document.querySelectorAll('.memory-block');
        
        if (window.innerWidth > 768) {
             let physics = Array.from(blocks).map(b => ({ el: b, x: b.offsetLeft, y: b.offsetTop, vx: 0, vy: 0 }));
             
             document.addEventListener('wheel', (e) => {
                physics.forEach(p => { p.vx += (Math.random()-0.5)*e.deltaY*0.04; p.vy += e.deltaY*0.04; });
             }, {passive:true});

             function update() {
                physics.forEach(p => {
                    if (Math.abs(p.vx)>0.1 || Math.abs(p.vy)>0.1) {
                        p.x+=p.vx; p.y+=p.vy;
                        p.el.style.left=p.x+'px'; p.el.style.top=p.y+'px';
                        p.vx*=0.95; p.vy*=0.95;
                    }
                });
                requestAnimationFrame(update);
             }
             update();
        }

        let z = 1000;
        blocks.forEach(el => {
            el.onmousedown = dragStart; el.ontouchstart = dragStart;
            function dragStart(e) { el.style.zIndex = ++z; }
        });
    </script>
</body>
</html>
"""

def get_all_exports():
    """Finds ALL ChatExport folders, sorted by date."""
    if not os.path.exists(PARENT_DIR): return []
    candidates = [
        os.path.join(PARENT_DIR, d) 
        for d in os.listdir(PARENT_DIR) 
        if d.startswith("ChatExport_") and os.path.isdir(os.path.join(PARENT_DIR, d))
    ]
    candidates.sort(key=os.path.getmtime)
    return candidates

def parse_messages_html(export_path):
    msg_file = os.path.join(export_path, "messages.html")
    if not os.path.exists(msg_file): return []
    
    with open(msg_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    memories = []
    messages = soup.find_all('div', class_='message')

    for msg in messages:
        date_div = msg.find('div', class_='date')
        if not date_div: continue
        ts = date_div.get('title') or date_div.text.strip()
        
        text_div = msg.find('div', class_='text')
        text = text_div.text.strip() if text_div else ""
        
        photo_rel = None
        wrap = msg.find('a', class_='photo_wrap') or msg.find('div', class_='photo_wrap')
        if wrap:
            if wrap.name == 'a': photo_rel = wrap.get('href')
            elif wrap.name == 'div': 
                img = wrap.find('img')
                if img: photo_rel = img.get('src')

        if text or photo_rel:
            memories.append({
                'type': 'image' if photo_rel else 'text',
                'ts': ts,
                'content': photo_rel if photo_rel else text,
                'is_text': bool(text and not photo_rel),
                'source_root': export_path
            })
    return memories

def load_json_posts():
    jpath = os.path.join(BASE_DIR, POSTS_JSON)
    if not os.path.exists(jpath): return []
    import json
    try:
        with open(jpath, 'r', encoding='utf-8') as f:
             data = json.load(f)
             if not data: return []
             return [{
                'type': p.get('type', 'text'),
                'ts': p.get('date'),
                'content': p.get('content') or p.get('image', ''),
                'is_text': p.get('type') == 'text',
                'local_image': p.get('image')
            } for p in data]
    except: return []

def load_archive():
    apath = os.path.join(BASE_DIR, ARCHIVE_JSON)
    if not os.path.exists(apath): return []
    import json
    try:
        with open(apath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data: return []
            return [{
                'type': p.get('type'),
                'ts': p.get('date'),
                'content': p.get('content') or p.get('image', ''),
                'is_text': p.get('type') == 'text',
                'local_image': p.get('image') if p.get('type') == 'image' else None
            } for p in data]
    except: return []

def stable_hash(s):
    """Returns a short, stable hash string for content."""
    return hashlib.md5(str(s).encode('utf-8')).hexdigest()[:5]

def rebuild_site():
    print("[GEN] Starting rebuild...")
    memories = []
    
    # 1. Gather Exports (Partial)
    exports = get_all_exports()
    for exp in exports:
        print(f" -> Parsing {os.path.basename(exp)}")
        memories += parse_messages_html(exp)

    # 2. Add Archive (Restored History)
    archive_mem = load_archive()
    if archive_mem:
        print(f"[GEN] Found {len(archive_mem)} archived posts.")
        memories += archive_mem

    # 3. Add Bot Posts
    json_mem = load_json_posts()
    if json_mem: 
        print(f"[GEN] Found {len(json_mem)} posts from bot.")
        memories += json_mem
        
    print(f"[GEN] Total memories found (raw): {len(memories)}")
    
    # 4. Deduplicate
    unique_mem = {}
    for m in memories:
        # Key: Time + Content Hash (keep concurrent/album posts)
        # Using hash ensures different photos at same time are preserved.
        h = stable_hash(m['content'])
        key = f"{m['ts']}_{h}"
        unique_mem[key] = m
    
    final_memories = list(unique_mem.values())
    print(f"[GEN] Unique memories: {len(final_memories)}")

    # 5. Build
    if not os.path.exists(PHOTOS_OUTPUT_DIR): os.makedirs(PHOTOS_OUTPUT_DIR)
    
    html_blocks = []
    
    for m in final_memories:
        img_html = ""
        if m['type'] == 'image' or not m['is_text']:
            src = None
            # Check various source locations
            if 'source_root' in m and m.get('content'): 
                 src = os.path.join(m['source_root'], m['content'])
            elif m.get('local_image') and not m['local_image'].startswith('photos/'): # Bot path
                 src = os.path.join(BASE_DIR, m['local_image'])
            elif m.get('local_image') and m['local_image'].startswith('photos/'): # Archive path (in root photos/)
                 src = os.path.join(BASE_DIR, m['local_image'])
                 
            # Logic for Archive: content is "photos/img_....jpg"
            if not src and m.get('content') and m['content'].startswith('photos/'):
                src = os.path.join(BASE_DIR, m['content'])

            if src and os.path.exists(src):
                safe_ts = re.sub(r'[^0-9]', '', m['ts'])[:14]
                cont_hash = stable_hash(m['content'])
                
                # Append hash to filename to avoid overwriting different images with same timestamp
                ext = os.path.splitext(src)[1] if os.path.splitext(src)[1] else ".jpg"
                dst_name = f"img_{safe_ts}_{cont_hash}{ext}"
                dst = os.path.join(PHOTOS_OUTPUT_DIR, dst_name)
                
                if not os.path.exists(dst): shutil.copy2(src, dst)
                img_html = f'<img src="photos/{dst_name}?v={safe_ts}" loading="lazy">'
            else:
                 pass

        top = random.randint(5, 80)
        left = random.randint(5, 80)
        
        block = f'''
        <div class="memory-block" style="top: {top}%; left: {left}%;" data-ts="{m['ts']}">
            <span class="timestamp">{m['ts']}</span>
            <div class="memory-text">{m['content'] if m['is_text'] else ''}</div>
            {img_html}
        </div>'''
        html_blocks.append(block)

    final_html = HTML_TEMPLATE.replace("<!-- INJECT_CONTENT_HERE -->", "\n".join(html_blocks))
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f: f.write(final_html)
    
    print(f"[GEN] Generated index.html with {len(html_blocks)} blocks.")
    git_push()

def git_push():
    try:
        os.chdir(os.path.join(BASE_DIR, "dist"))
        print("[GIT] Pulling...")
        subprocess.run(['git', 'pull', '--rebase'], check=False)
        subprocess.run(['git', 'add', '.'], check=False)
        subprocess.run(['git', 'commit', '-m', f"Rebuild {int(time.time())}"], check=False)
        subprocess.run(['git', 'push'], check=False)
        print("[GIT] Pushed.")
    except Exception as e:
        print(f"[GIT] Error: {e}")

if __name__ == "__main__":
    rebuild_site()
