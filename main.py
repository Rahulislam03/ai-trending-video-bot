import os
import asyncio
import requests
import random
import PIL.Image
import time

# Pillow ভার্সন কনফ্লিক্ট ফিক্স
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

def get_realistic_story():
    stories = [
        {
            "text": "ভবিষ্যতের এক ঢাকা শহর, যেখানে আকাশচুম্বী দালানের ফাঁক দিয়ে উড়ন্ত যান চলাচল করছে। প্রযুক্তির এই উৎকর্ষের মাঝেও একটি ছোট ছেলে পার্কে বসে একটি আসল গাছ লাগানোর চেষ্টা করছে।",
            "prompts": [
                "Hyper-realistic futuristic Dhaka city, neon lights, flying cars, cinematic 8k",
                "Young boy planting a real tree in a futuristic park, emotional lighting, hyper-detailed",
                "Cinematic sunset over a high-tech green city, nature and technology, 8k resolution"
            ]
        }
    ]
    return random.choice(stories)

async def create_voice(text, filename):
    voices = ["bn-BD-PradeepNeural", "bn-BD-NabanitaNeural"]
    for voice in voices:
        try:
            communicate = Communicate(text, voice)
            await communicate.save(filename)
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                print(f"✅ অডিও ফাইল তৈরি হয়েছে: {filename}")
                return True
        except:
            continue
    return False

def create_image(prompt, filename, retries=3):
    seed = random.randint(1, 999999)
    # Pollinations AI-এর নতুন প্যারামিটার যোগ করা হয়েছে দ্রুত রেসপন্সের জন্য
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1920&nologo=true&seed={seed}"
    
    for i in range(retries):
        try:
            print(f"🎨 ছবি তৈরি হচ্ছে: {filename} (চেষ্টা {i+1})...")
            r = requests.get(url, timeout=45)
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(r.content)
                return True
        except:
            time.sleep(3)
    return False

def make_advanced_video(image_paths, audio_path, output_path):
    try:
        print("🎬 ভিডিও রেন্ডারিং শুরু হচ্ছে...")
        if not os.path.exists(audio_path):
            print("❌ অডিও ফাইল পাওয়া যায়নি!")
            return

        audio = AudioFileClip(audio_path)
        duration_per_img = audio.duration / len(image_paths)
        
        clips = []
        for i, img in enumerate(image_paths):
            if os.path.exists(img):
                # হালকা জুম ইফেক্ট
                clip = ImageClip(img).set_duration(duration_per_img).resize(lambda t: 1 + 0.03 * t)
                clips.append(clip)
        
        if not clips:
            print("❌ কোনো ছবির ক্লিপ তৈরি করা যায়নি!")
            return

        final_video = concatenate_videoclips(clips, method="compose").set_audio(audio)
        
        # GitHub Actions-এর জন্য libx264 কোডেক ব্যবহার
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True)
        print(f"🚀 ভিডিও সফলভাবে তৈরি হয়েছে: {output_path}")
    except Exception as e:
        print(f"❌ ভিডিও রেন্ডারিং এরর: {e}")

async def main():
    os.makedirs('output', exist_ok=True)
    story_data = get_realistic_story()
    
    # ১. অডিও তৈরি
    if not await create_voice(story_data['text'], "voice.mp3"):
        print("❌ অডিও তৈরিতে ব্যর্থ।")
        return

    # ২. ছবি তৈরি
    img_list = []
    for i, p in enumerate(story_data['prompts']):
        path = f"img_{i}.jpg"
        if create_image(p, path):
            img_list.append(path)
    
    # ৩. ভিডিও তৈরি (ছবি অন্তত ১টি থাকলেও ভিডিও হবে)
    if len(img_list) > 0:
        make_advanced_video(img_list, "voice.mp3", "output/final_video.mp4")
    else:
        print("❌ ছবি তৈরিতে ব্যর্থ হওয়ায় ভিডিও তৈরি করা সম্ভব হলো না।")

if __name__ == "__main__":
    asyncio.run(main())
    
