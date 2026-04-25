import os
import yt_dlp
import re
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

# --- কনফিগারেশন ---
TARGET_URL = "https://xhamster.com/creators/tasnim"
HISTORY_FILE = "upload_history.txt"
LOGO_FILE = "mixveo_logo.png" 
OUTPUT_DIR = "processed_videos"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_to_history(video_id):
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{video_id}\n")

def process_video(video_path, video_id):
    clean_id = re.sub(r'[^a-zA-Z0-9]', '_', str(video_id))
    output_file = os.path.join(OUTPUT_DIR, f"final_{clean_id}.mp4")
    
    try:
        print(f"🎬 প্রসেসিং শুরু: {output_file}")
        clip = VideoFileClip(video_path)
        
        if os.path.exists(LOGO_FILE):
            logo = (ImageClip(LOGO_FILE)
                    .set_duration(clip.duration)
                    .resize(height=50) 
                    .set_pos(("right", "top")))
            final = CompositeVideoClip([clip, logo])
        else:
            final = clip

        final.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24, logger=None)
        clip.close()
        return output_file
    except Exception as e:
        print(f"❌ এডিটিং এরর: {e}")
        return None

def start_bot():
    history = get_history()
    
    # এরর ফিক্স: impersonate বাদ দিয়ে Headers ব্যবহার করা হচ্ছে
    ydl_opts = {
        'extract_flat': False,
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"🔍 {TARGET_URL} চেক করা হচ্ছে...")
        try:
            info = ydl.extract_info(TARGET_URL, download=False)
            
            if not info or 'entries' not in info:
                print("❌ কোনো ভিডিও খুঁজে পাওয়া যায়নি।")
                return

            for entry in info['entries']:
                if not entry: continue
                
                v_id = entry.get('id')
                if not v_id or v_id in history:
                    continue

                print(f"🚀 নতুন ভিডিও: {entry.get('title')}")
                video_url = entry.get('webpage_url') or entry.get('url')
                temp_video = "temp_raw.mp4"
                
                # ডাউনলোড
                with yt_dlp.YoutubeDL({'outtmpl': temp_video, 'quiet': True}) as ydl_d:
                    ydl_d.download([video_url])
                
                # এডিট
                if os.path.exists(temp_video):
                    if process_video(temp_video, v_id):
                        save_to_history(v_id)
                        print("✅ কাজ শেষ!")
                    
                    os.remove(temp_video)
                    break 
                    
        except Exception as e:
            print(f"❌ এরর: {e}")

if __name__ == "__main__":
    start_bot()
        
