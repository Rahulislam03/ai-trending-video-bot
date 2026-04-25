import os
import yt_dlp
import re
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

# --- কনফিগারেশন ---
TARGET_URL = "https://xhamster.com/creators/tasnim"
HISTORY_FILE = "upload_history.txt"
LOGO_FILE = "mixveo_logo.png" 
OUTPUT_DIR = "processed_videos"

# ডিরেক্টরি নিশ্চিত করা
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
    """ভিডিওতে লোগো বসানো এবং স্পেশাল ক্যারেক্টার ফিক্স করা"""
    # ফাইলের নাম থেকে আজেবাজে চিহ্ন মুছে ফেলা
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
            print("⚠️ লোগো ফাইল পাওয়া যায়নি!")
            final = clip

        # প্রসেসিং (libx264 দিয়ে দ্রুত করার চেষ্টা)
        final.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24, logger=None)
        clip.close()
        return output_file
    except Exception as e:
        print(f"❌ এডিটিং এরর: {e}")
        return None

def start_bot():
    history = get_history()
    
    # এক্সহ্যামস্টারের জন্য উন্নত সেটিংস
    ydl_opts = {
        'extract_flat': False, 
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,
        'impersonate': 'chrome', # ব্রাউজার ইমপার্সোনেট (curl_cffi লাগবে)
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"🔍 {TARGET_URL} থেকে ভিডিও স্ক্যান করা হচ্ছে...")
        try:
            info = ydl.extract_info(TARGET_URL, download=False)
            
            if not info or 'entries' not in info:
                print("❌ কোনো ভিডিও পাওয়া যায়নি! সাইট হয়তো বট ব্লক করেছে।")
                return

            for entry in info['entries']:
                if not entry: continue
                
                v_id = entry.get('id')
                if not v_id or v_id in history:
                    print(f"⏭️ স্কিপ বা আগে করা হয়েছে: {v_id}")
                    continue

                print(f"🚀 নতুন ভিডিও পাওয়া গেছে: {entry.get('title', 'Unknown')}")
                video_url = entry.get('webpage_url') or entry.get('url')
                temp_video = "temp_raw.mp4"
                
                # ডাউনলোড
                with yt_dlp.YoutubeDL({'outtmpl': temp_video, 'impersonate': 'chrome'}) as ydl_d:
                    ydl_d.download([video_url])
                
                # প্রসেসিং
                if os.path.exists(temp_video):
                    result = process_video(temp_video, v_id)
                    if result:
                        save_to_history(v_id)
                        print(f"✅ সফল: {result}")
                    
                    if os.path.exists(temp_video):
                        os.remove(temp_video)
                    break # গিটহাব মেমোরি বাঁচাতে একবারে একটিই যথেষ্ট।
                    
        except Exception as e:
            print(f"❌ ক্রাউলিং এরর: {e}")

if __name__ == "__main__":
    start_bot()
    
