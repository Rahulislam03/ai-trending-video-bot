import os
import yt_dlp
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

# কনফিগারেশন
TARGET_URL = "https://xhamster.com/creators/tasnim"
HISTORY_FILE = "upload_history.txt"
LOGO_FILE = "mixveo_logo.png" # আপনার লোগো ফাইল
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
    """ভিডিওতে লোগো বসানো এবং ফাইল হ্যাশ পরিবর্তন করা"""
    output_file = f"{OUTPUT_DIR}/final_{video_id}.mp4"
    clip = VideoFileClip(video_path)
    
    # লোগো সেটআপ (কোণে ছোট করে)
    if os.path.exists(LOGO_FILE):
        logo = (ImageClip(LOGO_FILE)
                .set_duration(clip.duration)
                .resize(height=50) # লোগোর সাইজ
                .margin(right=10, top=10, opacity=0)
                .set_pos(("right", "top")))
        final = CompositeVideoClip([clip, logo])
    else:
        final = clip

    final.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24)
    return output_file

def start_bot():
    history = get_history()
    ydl_opts = {'extract_flat': True, 'quiet': True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(TARGET_URL, download=False)
        if 'entries' in result:
            for entry in result['entries']:
                v_id = entry['id']
                
                if v_id in history:
                    print(f"⏭️ স্কিপ: {v_id} আগেই আপলোড হয়েছে।")
                    continue

                print(f"🚀 নতুন ভিডিও পাওয়া গেছে! আইডি: {v_id}")
                
                # ডাউনলোড করা
                download_opts = {'outtmpl': f'temp_{v_id}.mp4'}
                with yt_dlp.YoutubeDL(download_opts) as ydl_down:
                    ydl_down.download([entry['url']])
                
                # এডিট করা (লোগো বসানো)
                processed_path = process_video(f'temp_{v_id}.mp4', v_id)
                
                # এখানে আপনার আপলোড ফাংশন কল করতে পারেন
                print(f"✅ প্রসেস সম্পন্ন: {processed_path}")
                
                # ডুপ্লিকেট রোধে সেভ করা
                save_to_history(v_id)
                
                # টেম্পোরারি ফাইল ডিলিট করা
                os.remove(f'temp_{v_id}.mp4')
                break # গিটহাব স্টোরেজ বাঁচাতে একবারে একটি ভিডিও প্রসেস করা ভালো

if __name__ == "__main__":
    start_bot()
                    
