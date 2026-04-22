import os
import asyncio
import requests
import random
import PIL.Image
import time

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from edge_tts import Communicate
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

# ১. রিয়ালিস্টিক স্টোরি ও হাই-কোয়ালিটি প্রম্পট
def get_realistic_story():
    stories = [
        {
            "text": """ভবিষ্যতের এক ঢাকা শহর, যেখানে আকাশচুম্বী দালানের ফাঁক দিয়ে উড়ন্ত যান চলাচল করছে। 
            রাস্তার ধারে রোবটরা মানুষের সাথে কেনাকাটা করছে। প্রযুক্তির এই চরম উৎকর্ষের মাঝেও একটি ছোট ছেলে 
            পার্কে বসে একটি আসল গাছ লাগানোর চেষ্টা করছে। তার চোখে ছিল এক সুন্দর সবুজ পৃথিবীর স্বপ্ন। 
            ধীরে ধীরে চারপাশের যান্ত্রিক শহরটি যেন প্রকৃতির ছোঁয়ায় শান্ত হয়ে এল।""",
            "prompts": [
                "Hyper-realistic futuristic Dhaka city, neon lights, flying cars, cinematic 8k, photorealistic",
                "Advanced robots and humans interacting in a hi-tech marketplace, realistic skin textures, 8k",
                "A young boy planting a real tree in a futuristic metallic park, emotional lighting, hyper-detailed",
                "Close up of green leaves with raindrops, reflection of a futuristic city in the water drop, macro photography",
                "A beautiful blend of nature and technology, sunset over a futuristic city, breathtaking view, 8k"
            ]
        }
    ]
    return random.choice(stories)

async def create_voice(text, filename):
    # রিয়ালিস্টিক ভিডিওর জন্য 'BashkarNeural' (পুরুষ কণ্ঠ) বেশ গম্ভীর এবং মানানসই
    communicate = Communicate(text, "bn-BD-BashkarNeural")
    await communicate.save(filename)

def create_image(prompt, filename, retries=3):
    seed = random.randint(1, 999999)
    # রিয়ালিস্টিক লুকের জন্য 'seed' এবং ডিটেইল্ড প্যারামিটার যোগ করা হয়েছে
    url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}?width=1080&height=1920&nologo=true&seed={seed}&model=flux"
    
    for i in range(retries):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(r.content)
                return True
        except Exception as e:
            print(f"⚠️ চেষ্টা {i+1} ব্যর্থ: {e}")
            time.sleep(5)
    return False

def make_advanced_video(image_paths, audio_path, output_path):
    print("🎬 রিয়ালিস্টিক ভিডিও রেন্ডারিং শুরু হচ্ছে...")
    audio = AudioFileClip(audio_path)
    duration_per_img = audio.duration / len(image_paths)
    
    clips = []
    for i, img in enumerate(image_paths):
        clip = ImageClip(img).set_duration(duration_per_img)
        
        # একেক ছবিতে একেক মোশন (Zoom, Pan) যাতে রিয়ালিস্টিক লাগে
        if i % 2 == 0:
            # হালকা জুম ইন
            clip = clip.resize(lambda t: 1 + 0.03 * t)
        else:
            # হালকা জুম আউট (মোশন ডাইভার্সিটি)
            clip = clip.resize(lambda t: 1.1 - 0.03 * t)
            
        clips.append(clip)
    
    final_video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

async def main():
    os.makedirs('output', exist_ok=True)
    story_data = get_realistic_story()
    
    print("🔊 রিয়ালিস্টিক ভয়েস তৈরি হচ্ছে...")
    await create_voice(story_data['text'], "voice.mp3")
    
    img_list = []
    print(f"🎨 {len(story_data['prompts'])}টি রিয়ালিস্টিক ছবি জেনারেট হচ্ছে...")
    for i, p in enumerate(story_data['prompts']):
        path = f"img_{i}.jpg"
        if create_image(p, path):
            img_list.append(path)
    
    if len(img_list) > 0:
        make_advanced_video(img_list, "voice.mp3", "output/final_video.mp4")
        print(f"🚀 রিয়ালিস্টিক ভিডিও তৈরি সম্পন্ন!")
    else:
        print("❌ ছবি তৈরিতে ব্যর্থ।")

if __name__ == "__main__":
    asyncio.run(main())
            
