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
    """ভিডিওতে লোগো বসানো এবং ফাইল নাম ঠিক করা"""
    
    # এরর ফিক্স: আইডি থেকে স্পেশাল ক্যারেক্টার মুছে পরিষ্কার ফাইলের নাম তৈরি করা
    clean_id = re.sub(r'[^a-zA-Z0-9]', '_', str(video_id))
    output_file = os.path.join(OUTPUT_DIR, f"final_{clean_id}.mp4")
    
    try:
        print(f"🎬 প্রসেসিং শুরু হচ্ছে: {output_file}")
        clip = VideoFileClip(video_path)
        
        # লোগো সেটআপ
        if os.path.exists(LOGO_FILE):
            logo = (ImageClip(LOGO_FILE)
                    .set_duration(clip.duration)
                    .resize(height=50) 
                    .margin(right=10, top=10, opacity=0)
                    .set_pos(("right", "top")))
            final = CompositeVideoClip([clip, logo])
        else:
            print("⚠️ লোগো পাওয়া যায়নি, লোগো ছাড়াই এডিট হচ্ছে।")
            final = clip

        # মেমোরি এবং এরর হ্যান্ডলিং এর জন্য logger=None ও temp_audiofile ব্যবহার
        final.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24, logger=None)
        
        # মেমোরি খালি করা
        clip.close()
        if hasattr(final, 'close'): final.close()
        
        return output_file
    except Exception as e:
        print(f"❌ ভিডিও প্রসেসিং এরর: {str(e)}")
        return None

def start_bot():
    history = get_history()
    
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"🔍 {TARGET_URL} থেকে ভিডিও চেক করা হচ্ছে...")
        try:
            result = ydl.extract_info(TARGET_URL, download=False)
            
            if result and 'entries' in result:
                for entry in result['entries']:
                    if not entry: continue
                    
                    v_id = entry.get('id') or entry.get('url')
                    if not v_id: continue

                    if v_id in history:
                        print(f"⏭️ স্কিপ: {v_id}")
                        continue

                    print(f"🚀 নতুন ভিডিও পাওয়া গেছে! আইডি: {v_id}")
                    
                    video_url = entry.get('url')
                    temp_name = f"temp_video.mp4"
                    
                    # ভিডিও ডাউনলোড
                    download_opts = {'outtmpl': temp_name, 'quiet': True}
                    with yt_dlp.YoutubeDL(download_opts) as ydl_down:
                        ydl_down.download([video_url])
                    
                    # ভিডিও এডিটিং
                    if os.path.exists(temp_name):
                        processed_path = process_video(temp_name, v_id)
                        
                        if processed_path:
                            save_to_history(v_id)
                            print(f"✅ সফলভাবে তৈরি হয়েছে: {processed_path}")
                        
                        # টেম্পোরারি ফাইল ডিলিট
                        if os.path.exists(temp_name):
                            os.remove(temp_name)
                        
                        # গিটহাব অ্যাকশনের মেমোরি লিমিটের জন্য একবারে একটি ভিডিওই যথেষ্ট
                        break 
            else:
                print("❌ কোনো নতুন ভিডিও পাওয়া যায়নি।")
        except Exception as e:
            print(f"❌ এরর: {str(e)}")

if __name__ == "__main__":
    start_bot()
        
