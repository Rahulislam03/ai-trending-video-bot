import os
import yt_dlp
import json
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

# --- কনফিগারেশন ---
TARGET_URL = "https://xhamster.com/creators/tasnim"
HISTORY_FILE = "upload_history.txt"
LOGO_FILE = "mixveo_logo.png"  # আপনার রিপোজিটরিতে এই নামে লোগো থাকতে হবে
OUTPUT_DIR = "processed_videos"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_history():
    """ইতিমধ্যে প্রসেস হওয়া ভিডিওর আইডি লোড করা"""
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_to_history(video_id):
    """নতুন ভিডিওর আইডি হিস্ট্রিতে সেভ করা"""
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{video_id}\n")

def process_video(video_path, video_id):
    """ভিডিওতে লোগো বসানো এবং ফাইল হ্যাশ পরিবর্তন করা"""
    output_file = f"{OUTPUT_DIR}/final_{video_id}.mp4"
    try:
        clip = VideoFileClip(video_path)
        
        # লোগো সেটআপ (ভিডিওর উপরে ডানে)
        if os.path.exists(LOGO_FILE):
            logo = (ImageClip(LOGO_FILE)
                    .set_duration(clip.duration)
                    .resize(height=50) 
                    .margin(right=10, top=10, opacity=0)
                    .set_pos(("right", "top")))
            final = CompositeVideoClip([clip, logo])
        else:
            print("⚠️ লোগো ফাইল পাওয়া যায়নি, লোগো ছাড়াই প্রসেস হচ্ছে।")
            final = clip

        final.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24, logger=None)
        clip.close()
        return output_file
    except Exception as e:
        print(f"❌ ভিডিও প্রসেসিং এরর: {e}")
        return None

def start_bot():
    history = get_history()
    
    # yt-dlp অপশনস (এরর এড়াতে extract_flat এবং quiet মোড)
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"🔍 {TARGET_URL} থেকে ভিডিও খোঁজা হচ্ছে...")
        try:
            result = ydl.extract_info(TARGET_URL, download=False)
            
            if result and 'entries' in result:
                for entry in result['entries']:
                    if not entry: continue
                    
                    # 'id' না থাকলে ইউআরএল থেকে আইডি বের করার চেষ্টা
                    v_id = entry.get('id') or entry.get('url')
                    v_title = entry.get('title', 'Unknown Title')

                    if not v_id:
                        continue

                    # ডুপ্লিকেট চেক
                    if v_id in history:
                        print(f"⏭️ স্কিপ: {v_title} (আগেই প্রসেস করা হয়েছে)")
                        continue

                    print(f"🚀 নতুন ভিডিও পাওয়া গেছে: {v_title}")
                    
                    video_url = entry.get('url')
                    if not video_url:
                        continue

                    # ডাউনলোড শুরু
                    temp_name = f"temp_{v_id}.mp4"
                    download_opts = {'outtmpl': temp_name, 'quiet': True}
                    
                    with yt_dlp.YoutubeDL(download_opts) as ydl_down:
                        ydl_down.download([video_url])
                    
                    # ভিডিও এডিটিং (লোগো বসানো)
                    if os.path.exists(temp_name):
                        processed_path = process_video(temp_name, v_id)
                        
                        if processed_path:
                            save_to_history(v_id)
                            print(f"✅ সফলভাবে তৈরি হয়েছে: {processed_path}")
                        
                        # টেম্প ফাইল রিমুভ
                        os.remove(temp_name)
                        
                        # গিটহাব অ্যাকশন মেমোরি লিমিট এড়াতে একবারে একটি ভিডিওই প্রসেস করা নিরাপদ
                        break 
            else:
                print("❌ কোনো ভিডিও এন্ট্রি পাওয়া যায়নি।")
        except Exception as e:
            print(f"❌ ডাটা ফেচিং এরর: {e}")

if __name__ == "__main__":
    start_bot()
    
